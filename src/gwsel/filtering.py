"""Whitening, and the matched filter.

STATUS: skeleton. Filled in by TASKS/day-1-control.md.

Lifted from day2/repro-gw150914/reproduce.py, with the globals (FREQS, BAND,
NSEG, DF, GUARD) turned into arguments. The physics is ten lines; everything
else is bookkeeping about which grid you are on.
"""
import numpy as np
from scipy.signal.windows import tukey


def whiten(x, fs, freqs_psd, psd, f_lo=None, f_hi=None, window=True):
    """Divide out the noise, so every frequency counts the same.

    MUST SATISFY: whitened clean data has unit variance. Measured on 32 s of H1
    away from the event, cut at 20 Hz, the value is 0.9650 -- not 1.000, and the
    gap is the window, which is why `window` is an argument and not a constant.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    freqs = np.fft.rfftfreq(n, 1.0 / fs)
    noise = np.interp(freqs, freqs_psd, psd, left=np.inf, right=np.inf)
    band = np.isfinite(noise)
    if f_lo is not None:
        band &= freqs >= f_lo
    if f_hi is not None:
        band &= freqs <= f_hi
    taper = tukey(n, alpha=0.125) if window else np.ones(n)
    spectrum = np.fft.rfft(x * taper)
    spectrum[~band] = 0.0
    # The PSD is one-sided and the Tukey taper removes time-domain energy.
    # Restore both conventions so unit-variance stationary noise stays unit
    # variance after the finite-length, tapered transform.
    normalization = np.sqrt(2.0 / np.mean(taper ** 2))
    return normalization * np.fft.irfft(
        spectrum / np.sqrt(noise * fs / 2.0), n=n)


def segment(strain, t0, fs, gps_centre, seg_s):
    """Cut one analysis segment and return its FFT.

    Returns (dtilde, seg_start_gps). dtilde carries the 1/fs of the discrete
    transform, so it has the units of the continuous Fourier transform of the
    strain -- the matched filter below assumes that.
    """
    n = int(round(seg_s * fs))
    centre = int(round((gps_centre - t0) * fs))
    start = centre - n // 2
    if start < 0 or start + n > len(strain):
        raise ValueError("requested segment is outside the strain array")
    taper = tukey(n, alpha=0.125)
    return np.fft.rfft(np.asarray(strain[start:start + n]) * taper) / fs, t0 + start / fs


def matched_filter(dtilde, htilde, psd, freqs, f_low, f_high):
    """SNR against every possible arrival time at once.

        <a|b>  = 4 Re int a b* / S df
        z(t)   = 4 int d h* / S exp(2 pi i f t) df     one inverse FFT
        rho(t) = |z(t)| / sqrt(<h|h>)

    Returns (rho, sigma), where sigma = sqrt(<h|h>) is the SNR the template
    would have against itself -- the optimal SNR at the template's own distance.
    Built on f > 0 only, so z is the analytic signal and |z| is already
    maximised over the phase.

    MUST SATISFY: against real H1 data with the shipped IMRPhenomD waveform,
    rho peaks at 19.8104 and sigma is 39.3971.
    """
    dtilde = np.asarray(dtilde)
    htilde = np.asarray(htilde)
    psd = np.asarray(psd, dtype=float)
    freqs = np.asarray(freqs, dtype=float)
    if not (dtilde.shape == htilde.shape == psd.shape == freqs.shape):
        raise ValueError("filter inputs must share one frequency grid")
    band = ((freqs >= f_low) & (freqs <= f_high) & np.isfinite(psd)
            & (psd > 0.0))
    df = freqs[1] - freqs[0]
    sigma2 = 4.0 * np.sum(np.abs(htilde[band]) ** 2 / psd[band]) * df
    spectrum = np.zeros_like(dtilde, dtype=complex)
    spectrum[band] = 4.0 * dtilde[band] * np.conj(htilde[band]) / psd[band] * df
    n = 2 * (len(freqs) - 1)
    analytic = np.zeros(n, dtype=complex)
    analytic[:len(spectrum)] = spectrum
    z = np.fft.ifft(analytic) * n
    return np.abs(z) / np.sqrt(sigma2), np.sqrt(sigma2)


def peak(rho, guard):
    """Loudest sample, ignoring `guard` samples at each end.

    The guard is not cosmetic: the segment is windowed, and the taper at the
    edges produces a filter response that is an artifact of the window.
    Returns (index, value).
    """
    rho = np.asarray(rho)
    if 2 * guard >= rho.size:
        raise ValueError("guard leaves no samples to search")
    local = int(np.argmax(rho[guard:rho.size - guard]))
    index = local + guard
    return index, float(rho[index])


def template_peak_time(htilde, freqs, f_low, f_high, n, fs):
    """Where the template's own peak sits inside the segment, in seconds.

    Needed to turn a filter-output index into an arrival time: the filter tells
    you the offset between data and template, not when the signal arrived.
    """
    band = (freqs >= f_low) & (freqs <= f_high)
    spectrum = np.zeros_like(htilde, dtype=complex)
    spectrum[band] = htilde[band]
    waveform = np.fft.irfft(spectrum * fs, n=n)
    time = float(np.argmax(np.abs(waveform)) / fs)
    # FFT time is periodic.  A peak at the right edge is a small negative
    # offset from zero, not an arrival one segment later.
    return time if time <= (n / fs) / 2.0 else time - n / fs


def search(strain, t0, fs, htilde, psd, freqs, gps_centre, seg_s,
           f_low, f_high, guard):
    """segment -> matched_filter -> peak, with the arrival time worked out.

    Returns a dict with rho, seg_start, peak, sigma, gps.
    """
    dtilde, seg_start = segment(strain, t0, fs, gps_centre, seg_s)
    rho, sigma = matched_filter(dtilde, htilde, psd, freqs, f_low, f_high)
    index, value = peak(rho, guard)
    template_time = template_peak_time(htilde, freqs, f_low, f_high,
                                       2 * (len(freqs) - 1), fs)
    gps = seg_start + index / fs + template_time
    return {"rho": rho, "seg_start": seg_start, "peak": value,
            "sigma": sigma, "gps": gps, "peak_index": index}
