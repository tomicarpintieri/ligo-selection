"""How far away a source can be and still be heard.

STATUS: skeleton. Filled in by TASKS/day-3-horizon.md.

SNR falls as 1/distance, so a detection threshold IS a distance, and a distance
cubed is a volume. That is the whole chain, and it is where selection effects
come from: loud things are visible from further away, so a catalogue over-counts
them relative to the universe.

Everything here is Euclidean -- no redshift, no expansion. That is fine out to
the ~2 Gpc Advanced LIGO reaches and wrong for the third-generation detectors of
week 4, and the figures have to say so on their face.
"""
import numpy as np

from . import waveform


def sigma(htilde, psd, freqs, f_low, f_high):
    """The optimal SNR of a template against itself: sqrt(4 int |h|^2 / S df).

    The SNR a perfectly-oriented, perfectly-placed source would give at whatever
    distance the waveform was generated for.

    MUST SATISFY: 39.3971 for the shipped IMRPhenomD waveform against the H1 PSD
    estimated off-source, over 20-1024 Hz.
    """
    band = (freqs >= f_low) & (freqs <= f_high) & np.isfinite(psd)
    return float(np.sqrt(4 * np.sum(abs(htilde[band])**2 / psd[band]) * (freqs[1]-freqs[0])))


def horizon_distance(sigma_at_ref, distance_ref_mpc, rho_thr=8.0):
    """Distance at which an optimally-oriented source hits the threshold, in Mpc.

    MUST SATISFY: 400 Mpc * 39.3971 / 8 = 1969.9 Mpc for GW150914, which is the
    1.9 Gpc the day 2 lecture quotes.
    """
    return float(distance_ref_mpc * sigma_at_ref / rho_thr)


def sensitive_volume_euclidean(d_mpc):
    """(4/3) pi d^3, in Gpc^3.

    MUST SATISFY: 32.0 +- 1.0 Gpc^3 at the GW150914 horizon, and
    d ln V / d ln rho_thr = -3 exactly.
    """
    return float(4*np.pi/3 * (d_mpc/1000)**3)


def horizon_curve(mchirp_grid, psd, freqs, rho_thr=8.0, **waveform_kwargs):
    """Horizon distance against chirp mass. Returns (mchirp_grid, d_mpc).

    Rises as chirp mass to the 5/6 while the signal fills the band, then turns
    over once the merger drops below the sensitive band.

    MUST SATISFY: a power-law fit over mchirp in [1.5, 5] Msun gives the exponent
    0.8333 +- 0.01. That range is not arbitrary -- there f_isco sits above
    ~380 Hz, i.e. above the sensitive band, so the band is effectively fixed,
    which is the condition under which 5/6 is exact. Record that as a choice.
    """
    distance = waveform_kwargs.pop("distance_mpc", 400.0)
    # Read the cutoff ONCE.  This pop() used to sit inside the loop, where it
    # consumed the key on the first iteration: mass 1 of 80 got the ISCO cutoff
    # and the other 79 got None.  The published curve therefore mixed two
    # physics and never turned over -- 5204 Mpc at Mc = 80 where the answer is
    # 359.  test_horizon_turns_over is the check that now holds it in place.
    f_cut = waveform_kwargs.pop("f_cut", "isco")
    eta = 0.25
    out = []
    for mc in mchirp_grid:
        total = mc / eta ** (3 / 5)
        mass = total / 2
        h, _ = waveform.spa_inspiral(freqs, mass, mass, distance,
                                     f_cut=f_cut, **waveform_kwargs)
        out.append(horizon_distance(sigma(h, psd, freqs, 20, 1024), distance, rho_thr))
    return np.asarray(mchirp_grid), np.asarray(out)
