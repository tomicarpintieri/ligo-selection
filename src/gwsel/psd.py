"""Noise power spectra.

STATUS: skeleton. Filled in by TASKS/day-1-control.md.

Lifted from day2/repro-gw150914/reproduce.py in the course tree, which we wrote
on 2026-08-31. That file is a script: it computes on import and reaches for
module-level globals. Here the same functions take their inputs as arguments.
The record of what changed goes in provenance/numbers.json under
`from_scratch`.
"""
import numpy as np


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
    raise NotImplementedError("TASKS/day-1-control.md")


def psd_on_grid(freqs_psd, psd, freqs_target):
    """Interpolate a PSD onto an analysis frequency grid.

    Outside the range where the PSD is known the value must be +inf, not zero
    and not the edge value: an infinite noise power is what makes the matched
    filter ignore a band, and anything finite silently invents sensitivity.
    """
    raise NotImplementedError("TASKS/day-1-control.md")
