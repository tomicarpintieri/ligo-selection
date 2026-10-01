"""A reproducible, two-detector injection-and-recovery pilot.

The project deliberately has no LALSuite on Windows, so this module uses the
validated non-spinning SPA waveform and says so.  It is a selection-function
pilot, not an IMR population analysis: heavy systems remain a declared limit.
"""
import numpy as np
from scipy.signal.windows import tukey

from . import antenna, filtering, waveform


def sample_population(n, rng, distance_min=100.0, distance_max=1800.0,
                      mass_min=5.0, mass_max=20.0, gps=1126259462.4):
    """Draw an isotropic, uniform-in-volume non-spinning binary population."""
    if n <= 0 or not (0 < distance_min < distance_max and 0 < mass_min <= mass_max):
        raise ValueError("invalid population bounds")
    distance = rng.uniform(distance_min**3, distance_max**3, n) ** (1 / 3)
    return {"m1": rng.uniform(mass_min, mass_max, n),
            "m2": rng.uniform(mass_min, mass_max, n), "distance_mpc": distance,
            "ra": rng.uniform(0, 2 * np.pi, n),
            "dec": np.arcsin(rng.uniform(-1, 1, n)),
            "psi": rng.uniform(0, 2 * np.pi, n),
            "inclination": np.arccos(rng.uniform(-1, 1, n)),
            "gps": np.full(n, gps)}


def network_snr(rho_h1, rho_l1):
    """Incoherent coincident-network statistic used by this pilot."""
    return np.hypot(rho_h1, rho_l1)


def efficiency(distance, detected, edges):
    """Binned recovery fraction and binomial uncertainty versus distance."""
    distance, detected, edges = np.asarray(distance), np.asarray(detected, bool), np.asarray(edges)
    index = np.digitize(distance, edges) - 1
    centers, fraction, uncertainty, count = [], [], [], []
    for i in range(len(edges) - 1):
        chosen = index == i
        n = int(np.sum(chosen))
        centers.append((edges[i] + edges[i + 1]) / 2)
        count.append(n)
        p = float(np.mean(detected[chosen])) if n else np.nan
        fraction.append(p)
        uncertainty.append(np.sqrt(p * (1 - p) / n) if n else np.nan)
    return {"distance_mpc": np.asarray(centers), "efficiency": np.asarray(fraction),
            "uncertainty": np.asarray(uncertainty), "count": np.asarray(count)}


def _time_series(htilde, fs):
    # TaylorF2's coalescence is at the periodic FFT boundary.  Move it to the
    # middle of the analysis segment before applying the same Tukey taper used
    # by the recovery filter; otherwise the taper silently erases the injection.
    waveform_time = np.fft.irfft(htilde * fs, n=2 * (len(htilde) - 1))
    return np.roll(waveform_time, len(waveform_time) // 2)


def _peak_snr(noise, htilde, psd, freqs, fs, inject=True, f_low=20.0, f_high=1024.0):
    injected = noise + _time_series(htilde, fs) if inject else noise
    dtilde = np.fft.rfft(injected * tukey(len(injected), alpha=.125)) / fs
    rho, _ = filtering.matched_filter(dtilde, htilde, psd, freqs, f_low, f_high)
    return filtering.peak(rho, int(4 * fs))[1]


def recover_population(population, h1, l1, psd_h1, psd_l1, freqs, seed=0,
                       threshold=12.0, inject=True):
    """Inject sources into independent off-source windows and recover network SNR.

    The H1/L1 statistic is ``sqrt(rho_H1^2 + rho_L1^2)`` after applying each
    detector's antenna response and geometric arrival delay.  It is explicitly
    coincident rather than a coherent likelihood.
    """
    rng = np.random.default_rng(seed)
    n = len(population["m1"])
    fs = h1["fs"]
    nseg = int(32 * fs)
    out = {key: np.empty(n) for key in ("rho_h1", "rho_l1", "rho_network")}
    for i in range(n):
        gps = population["gps"][i]
        ra, dec, psi, inc = (population[key][i] for key in ("ra", "dec", "psi", "inclination"))
        hp, hc = waveform.spa_inspiral(freqs, population["m1"][i], population["m2"][i],
                                       population["distance_mpc"][i], inclination=inc, f_cut="isco")
        fp_h, fc_h = antenna.response_earth("H1", ra, dec, psi, gps)
        fp_l, fc_l = antenna.response_earth("L1", ra, dec, psi, gps)
        h_h = fp_h * hp + fc_h * hc
        delay = antenna.time_delay("H1", "L1", ra, dec, gps)
        h_l = (fp_l * hp + fc_l * hc) * np.exp(-2j * np.pi * freqs * delay)
        # First 512 seconds are off-source; windows are independent of the event.
        start = int(rng.integers(0, int(512 * fs) - nseg))
        noise_h = h1["strain"][start:start + nseg]
        noise_l = l1["strain"][start:start + nseg]
        out["rho_h1"][i] = _peak_snr(noise_h, h_h, psd_h1, freqs, fs, inject=inject)
        out["rho_l1"][i] = _peak_snr(noise_l, h_l, psd_l1, freqs, fs, inject=inject)
        out["rho_network"][i] = network_snr(out["rho_h1"][i], out["rho_l1"][i])
    out["detected"] = out["rho_network"] >= threshold
    return out
