"""Whitening, and the matched filter.

STATUS: skeleton. Filled in by TASKS/day-1-control.md.

Lifted from day2/repro-gw150914/reproduce.py, with the globals (FREQS, BAND,
NSEG, DF, GUARD) turned into arguments. The physics is ten lines; everything
else is bookkeeping about which grid you are on.
"""
import numpy as np


def whiten(x, fs, freqs_psd, psd, f_lo=None, f_hi=None, window=True):
    """Divide out the noise, so every frequency counts the same.

    MUST SATISFY: whitened clean data has unit variance. Measured on 32 s of H1
    away from the event, cut at 20 Hz, the value is 0.9650 -- not 1.000, and the
    gap is the window, which is why `window` is an argument and not a constant.
    """
    raise NotImplementedError("TASKS/day-1-control.md")


def segment(strain, t0, fs, gps_centre, seg_s):
    """Cut one analysis segment and return its FFT.

    Returns (dtilde, seg_start_gps). dtilde carries the 1/fs of the discrete
    transform, so it has the units of the continuous Fourier transform of the
    strain -- the matched filter below assumes that.
    """
    raise NotImplementedError("TASKS/day-1-control.md")


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
    raise NotImplementedError("TASKS/day-1-control.md")


def peak(rho, guard):
    """Loudest sample, ignoring `guard` samples at each end.

    The guard is not cosmetic: the segment is windowed, and the taper at the
    edges produces a filter response that is an artifact of the window.
    Returns (index, value).
    """
    raise NotImplementedError("TASKS/day-1-control.md")


def template_peak_time(htilde, freqs, f_low, f_high, n, fs):
    """Where the template's own peak sits inside the segment, in seconds.

    Needed to turn a filter-output index into an arrival time: the filter tells
    you the offset between data and template, not when the signal arrived.
    """
    raise NotImplementedError("TASKS/day-1-control.md")


def search(strain, t0, fs, htilde, psd, freqs, gps_centre, seg_s,
           f_low, f_high, guard):
    """segment -> matched_filter -> peak, with the arrival time worked out.

    Returns a dict with rho, seg_start, peak, sigma, gps.
    """
    raise NotImplementedError("TASKS/day-1-control.md")
