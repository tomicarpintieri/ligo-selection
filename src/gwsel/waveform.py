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

from . import constants as k

# LAL's solar-mass time conversion.  The phase accumulates thousands of radians,
# so its reference value is kept local rather than changing the project-wide
# pedagogical mass constant used by earlier stages.
LAL_MSUN_S = 4.925490947641267e-6


def chirp_mass(m1, m2):
    """(m1 m2)^(3/5) / (m1 + m2)^(1/5), in whatever units go in."""
    return (m1 * m2) ** (3.0 / 5.0) / (m1 + m2) ** (1.0 / 5.0)


def symmetric_mass_ratio(m1, m2):
    """eta = m1 m2 / (m1 + m2)^2. 1/4 for equal masses, -> 0 as they separate."""
    return m1 * m2 / (m1 + m2) ** 2


def f_isco(m_total_solar):
    """Orbital frequency of the innermost stable circular orbit, in Hz.

    Where the inspiral description stops being true. Approximately
    4400 / (M_total/Msun) Hz, so for GW150914 (72.15 Msun) it is 61 Hz -- which
    is why an inspiral-only waveform recovers 11.36 of that event's SNR and not
    19.81. That is the honest scope of this module, not a bug.

    MUST SATISFY: 61.0 +- 0.5 Hz at M_total = 72.15.
    """
    return 1.0 / (6.0 ** 1.5 * np.pi * m_total_solar * k.MSUN_S)


def spa_inspiral(freqs, m1, m2, distance_mpc, inclination=0.0,
                 chi1z=0.0, chi2z=0.0, f_low=20.0, f_high=None,
                 pn_order=3.5, f_cut="isco"):
    """Stationary-phase inspiral. Returns (h_plus, h_cross) on `freqs`.

    Amplitude at 0PN, phase to `pn_order` (3.5PN by default, which is what LAL's
    TaylorF2 uses -- matching it is the point). Masses in solar masses, distance
    in Mpc, angles in radians. Outside [f_low, f_cut] the output is zero;
    `f_cut=None` asks for no upper cutoff, which is the convention LAL's
    shipped reference uses and the only place this project wants it.

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
    if chi1z != 0.0 or chi2z != 0.0:
        raise NotImplementedError("aligned spins are a later stage")
    if pn_order not in (0.0, 3.5):
        raise ValueError("only 0PN and 3.5PN phase are implemented")
    freqs = np.asarray(freqs, dtype=float)
    eta = symmetric_mass_ratio(m1, m2)
    m_total_s = (m1 + m2) * LAL_MSUN_S
    mc_s = chirp_mass(m1, m2) * LAL_MSUN_S
    # Three ways to say where the waveform stops, and the default is the
    # physical one.  Until 2026-09-30 "isco" meant np.inf -- the default value
    # was named after the cutoff it disabled -- which inflated sigma by 1.83x
    # at 72 Msun and 4x at 120 Msun, growing with mass, i.e. along exactly the
    # axis this project measures.
    #
    #   "isco"        stop where the inspiral description stops being true
    #   None          no cutoff at all.  LAL's shipped TaylorF2 reference runs
    #                 to Nyquist, so comparing against it must ask for this
    #                 explicitly rather than receive it by accident
    #   a number      stop there, in Hz
    if f_cut == "isco":
        cutoff = f_isco(m1 + m2)
    elif f_cut is None:
        cutoff = np.inf
    else:
        cutoff = float(f_cut)
    if f_high is not None:
        cutoff = min(cutoff, f_high)
    valid = (freqs >= f_low) & (freqs <= cutoff)
    h_plus = np.zeros(freqs.shape, dtype=complex)
    h_cross = np.zeros(freqs.shape, dtype=complex)
    f = freqs[valid]
    v = (np.pi * m_total_s * f) ** (1.0 / 3.0)
    # TaylorF2, non-spinning phase through 3.5PN (Blanchet, Living Rev.
    # Relativity 17, 2 (2014), Eq. 223).  The arbitrary coalescence time and
    # phase are zero; match() maximises over both.
    phase_series = np.ones_like(v)
    if pn_order == 3.5:
        gamma = np.euler_gamma
        phase_series += (3715.0 / 756.0 + 55.0 * eta / 9.0) * v**2
        phase_series += -16.0 * np.pi * v**3
        phase_series += (15293365.0 / 508032.0 + 27145.0 * eta / 504.0
                         + 3085.0 * eta**2 / 72.0) * v**4
        phase_series += np.pi * (38645.0 / 756.0 - 65.0 * eta / 9.0) * (1.0 + 3.0 * np.log(v)) * v**5
        phase_series += (11583231236531.0 / 4694215680.0 - 640.0 * np.pi**2 / 3.0
                         - 6848.0 * gamma / 21.0 - 6848.0 * np.log(4.0 * v) / 21.0
                         + (-15737765635.0 / 3048192.0 + 2255.0 * np.pi**2 / 12.0) * eta
                         + 76055.0 * eta**2 / 1728.0 - 127825.0 * eta**3 / 1296.0) * v**6
        phase_series += np.pi * (77096675.0 / 254016.0 + 378515.0 * eta / 1512.0
                                 - 74045.0 * eta**2 / 756.0) * v**7
    phase = -np.pi / 4.0 + 3.0 * phase_series / (128.0 * eta * v**5)
    distance_m = distance_mpc * k.MPC
    amplitude = (np.sqrt(5.0 / 24.0) / np.pi**(2.0 / 3.0)
                 * (k.C / distance_m) * mc_s**(5.0 / 6.0) * f**(-7.0 / 6.0))
    ci = np.cos(inclination)
    # NumPy's forward FFT uses exp(-2 pi i f t), hence the frequency-domain
    # TaylorF2 convention is exp(-i Psi) for the shipped LAL arrays.
    h_plus[valid] = amplitude * (1.0 + ci**2) / 2.0 * np.exp(-1j * phase)
    h_cross[valid] = 1j * amplitude * ci * np.exp(-1j * phase)
    return h_plus, h_cross


def match(h1, h2, psd, freqs, f_low, f_high):
    """Normalised overlap, maximised over time and phase. 1.0 is identical.

    This is the matched filter applied to a template instead of to data, so it
    reuses filtering.matched_filter rather than restating the inner product.
    """
    from . import filtering
    rho, sigma = filtering.matched_filter(h1, h2, psd, freqs, f_low, f_high)
    return float(np.max(rho) / sigma)
