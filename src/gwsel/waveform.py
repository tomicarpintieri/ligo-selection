"""The signal, in the frequency domain, with an amplitude that means something.

STATUS: skeleton. Filled in by TASKS/day-2-waveform.md.

Day 2's reproduction had a template good enough to SEARCH with, because the
matched filter normalises the amplitude away. This project has to ask whether a
source at a given distance is detectable, and for that the amplitude has to be
physical: proportional to chirp mass to the 5/6 and inversely proportional to
distance.

The reference is data/imr_gw150914.npz['h_taylorf2_lal'] -- LAL computing
exactly this for m1=38.8, m2=33.35 Msun at 400 Mpc, face-on, from 20 Hz, on a
32 s / 4096 Hz grid. Everything in this module is measured against it.
"""
import numpy as np


def chirp_mass(m1, m2):
    """(m1 m2)^(3/5) / (m1 + m2)^(1/5), in whatever units go in."""
    raise NotImplementedError("TASKS/day-2-waveform.md")


def symmetric_mass_ratio(m1, m2):
    """eta = m1 m2 / (m1 + m2)^2. 1/4 for equal masses, -> 0 as they separate."""
    raise NotImplementedError("TASKS/day-2-waveform.md")


def f_isco(m_total_solar):
    """Orbital frequency of the innermost stable circular orbit, in Hz.

    Where the inspiral description stops being true. Approximately
    4400 / (M_total/Msun) Hz, so for GW150914 (72.15 Msun) it is 61 Hz -- which
    is why an inspiral-only waveform recovers 11.36 of that event's SNR and not
    19.81. That is the honest scope of this module, not a bug.

    MUST SATISFY: 61.0 +- 0.5 Hz at M_total = 72.15.
    """
    raise NotImplementedError("TASKS/day-2-waveform.md")


def spa_inspiral(freqs, m1, m2, distance_mpc, inclination=0.0,
                 chi1z=0.0, chi2z=0.0, f_low=20.0, f_high=None,
                 pn_order=3.5, f_cut="isco"):
    """Stationary-phase inspiral. Returns (h_plus, h_cross) on `freqs`.

    Amplitude at 0PN, phase to `pn_order` (3.5PN by default, which is what LAL's
    TaylorF2 uses -- matching it is the point). Masses in solar masses, distance
    in Mpc, angles in radians. Outside [f_low, f_cut] the output is zero.

    chi1z and chi2z are accepted so that week 3's aligned-spin work is an edit
    and not a rewrite. Until then anything non-zero must raise
    NotImplementedError rather than silently ignore the spin.

    MUST SATISFY, against h_taylorf2_lal at its own parameters:
      median |h_ours| / |h_lal| over 20-150 Hz  = 1.000 +- 0.005
      std of that ratio                          < 0.01
      match, maximised over time and phase,      > 0.99
        weighted by the H1 PSD over 20-300 Hz
      SNR against real H1 data                   = 11.358 +- 0.05
      h(2D) = h(D)/2                             to 1e-12
      amplitude exponent in chirp mass           = 0.8333 +- 0.001

    If the amplitude ratio comes out smooth-but-not-flat, that is LAL having
    used post-Newtonian amplitude corrections rather than the 0PN amplitude.
    Record which convention we chose and why. Do not tune to close the gap.
    """
    raise NotImplementedError("TASKS/day-2-waveform.md")


def match(h1, h2, psd, freqs, f_low, f_high):
    """Normalised overlap, maximised over time and phase. 1.0 is identical.

    This is the matched filter applied to a template instead of to data, so it
    reuses filtering.matched_filter rather than restating the inner product.
    """
    raise NotImplementedError("TASKS/day-2-waveform.md")
