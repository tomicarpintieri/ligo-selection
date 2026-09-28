"""Noise power spectra.

STATUS: skeleton. Filled in by TASKS/day-1-control.md.

Lifted from day2/repro-gw150914/reproduce.py in the course tree, which we wrote
on 2026-08-31. That file is a script: it computes on import and reaches for
module-level globals. Here the same functions take their inputs as arguments.
The record of what changed goes in provenance/numbers.json under
`from_scratch`.
"""
import numpy as np
from scipy.signal.windows import hann


def welch_median(x, fs, seg_s=4.0, overlap=0.5):
    """One-sided PSD by segmenting, windowing, and taking the median.

    Returns (freqs, psd).

    Three choices with a trap in each, and all three belong in `choices` when a
    number that depends on them is recorded:
      segment length  long resolves the lines, short averages the continuum
      window          divide by sum(w**2), NOT by n  (8/3 for a Hann window)
      median          robust to a glitch, or to a signal sitting in the data
                      the estimate is made from -- but biased low, and the bias
                      is the alternating harmonic sum, which must be divided out

    MUST SATISFY: on the full 2048 s of H1, the median relative difference
    against data/psd_reference.npz['psd_gwpy_median'] over 20-1024 Hz is
    0.00096 %. See tests/test_01_control.py::test_welch_vs_gwpy_pct.
    """
    x = np.asarray(x, dtype=float)
    nseg = int(round(seg_s * fs))
    step = int(round(nseg * (1.0 - overlap)))
    if nseg <= 1 or step <= 0 or x.size < nseg:
        raise ValueError("input is too short for the requested Welch segments")

    starts = np.arange(0, x.size - nseg + 1, step)
    # gwpy's FFTPlan uses the periodic Hann convention (rather than the
    # symmetric window used for FIR design) and removes each segment's mean.
    window = hann(nseg, sym=False)
    scale = 1.0 / (fs * np.sum(window ** 2))
    spectra = np.empty((starts.size, nseg // 2 + 1))
    for row, start in enumerate(starts):
        piece = x[start:start + nseg]
        spectrum = np.fft.rfft((piece - np.mean(piece)) * window)
        spectra[row] = scale * np.abs(spectrum) ** 2
    # rfft holds only positive frequencies; their negative-frequency partners
    # carry the other half of the one-sided power (except DC and Nyquist).
    spectra[:, 1:-1] *= 2.0

    # For exponentially distributed periodograms the sample median is biased.
    # This finite-sample alternating harmonic sum is scipy/gwpy's correction.
    count = starts.size
    odds = 2 * np.arange(1, (count - 1) // 2 + 1) + 1
    median_bias = 1.0 + np.sum(1.0 / odds - 1.0 / (odds - 1.0))
    return np.fft.rfftfreq(nseg, 1.0 / fs), np.median(spectra, axis=0) / median_bias


def psd_on_grid(freqs_psd, psd, freqs_target):
    """Interpolate a PSD onto an analysis frequency grid.

    Outside the range where the PSD is known the value must be +inf, not zero
    and not the edge value: an infinite noise power is what makes the matched
    filter ignore a band, and anything finite silently invents sensitivity.
    """
    freqs_psd = np.asarray(freqs_psd, dtype=float)
    psd = np.asarray(psd, dtype=float)
    freqs_target = np.asarray(freqs_target, dtype=float)
    if freqs_psd.ndim != 1 or psd.shape != freqs_psd.shape:
        raise ValueError("freqs_psd and psd must be matching one-dimensional arrays")
    return np.interp(freqs_target, freqs_psd, psd, left=np.inf, right=np.inf)
