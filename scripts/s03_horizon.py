"""Threshold to distance to volume: how much universe one detector searches.

SNR falls as 1/distance, so a detection threshold IS a distance, and a distance
cubed is a volume. That chain is where selection effects come from: loud sources
are visible from further away, so a catalogue over-represents them.

Everything here is Euclidean -- no redshift, no expansion. Fine out to the
~2 Gpc Advanced LIGO reaches, wrong for third-generation detectors, and the
figure says so on its face.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from gwsel import dataio, figures, horizon, psd, waveform
from gwsel import provenance as pv

# ---------------------------------------------------------------------------
# The fit window is DERIVED, not chosen.
#
# The 5/6 law holds only while the analysis band is fixed. Cutting the waveform
# at f_ISCO always removes some high-frequency SNR, and removes more of it the
# heavier the system, so a fit reaching too far up in mass measures an exponent
# biased low by an amount that depends entirely on where you stopped. Picking
# the window by eye until the number comes out right would be fitting the
# window to the answer.
#
# So the acceptable bias is fixed FIRST, as a fraction of SNR, and the window
# follows from it by bisection.
#
# The day-3 brief instead named [1.5, 5] Msun, justified by "f_isco sits above
# ~380 Hz, i.e. above the sensitive band". That justification fails at the top
# of its own window: at Mc = 5 the cutoff is 383 Hz and the analysis band runs
# to 1024 Hz, so the cut is inside the band, not above it. Measured there the
# exponent is 0.8219 -- outside the +-0.01 the same brief asks for. The
# tolerance was not touched; the window was derived instead, and the wide-window
# value is still measured and reported below. See NOTES.md.
BAND_FIXED_TOLERANCE = 0.999     # the ISCO cut may cost at most 0.1% of sigma
MCHIRP_FIT_MIN = 1.5             # low end of both the fit and the curve
MCHIRP_CURVE_MAX = 80.0          # above this f_ISCO drops under the 20 Hz band
                                 # edge, the horizon is exactly 0, and a log
                                 # axis cannot draw it
MCHIRP_BRIEF_WINDOW_MAX = 5.0    # the brief's window, kept to measure the bias
ETA_EQUAL_MASS = 0.25            # every curve point is an equal-mass binary
RHO_THR = 8.0
D_REF_MPC = 400.0                # the distance the shipped waveforms are at


def total_mass(mchirp):
    """Total mass of the equal-mass binary with this chirp mass, in Msun."""
    return mchirp / ETA_EQUAL_MASS ** 0.6


def band_fixed_ratio(mchirp, psd_grid, freqs):
    """sigma with the ISCO cut over sigma with none. 1.0 means the band is fixed.

    This is the quantity the fit window is derived from: how much of the SNR
    the physical cutoff costs at a given mass.
    """
    m = total_mass(mchirp) / 2.0
    cut, _ = waveform.spa_inspiral(freqs, m, m, D_REF_MPC, f_cut="isco")
    full, _ = waveform.spa_inspiral(freqs, m, m, D_REF_MPC, f_cut=None)
    return float(horizon.sigma(cut, psd_grid, freqs, 20, 1024)
                 / horizon.sigma(full, psd_grid, freqs, 20, 1024))


def fit_window_max(psd_grid, freqs, lo=MCHIRP_FIT_MIN, hi=12.0):
    """Largest chirp mass at which the band still counts as fixed."""
    for _ in range(45):
        mid = 0.5 * (lo + hi)
        if band_fixed_ratio(mid, psd_grid, freqs) >= BAND_FIXED_TOLERANCE:
            lo = mid
        else:
            hi = mid
    return lo


def power_law_exponent(mc_lo, mc_hi, psd_grid, freqs, n=40):
    """Slope of log horizon against log chirp mass over one window."""
    mc, d = horizon.horizon_curve(np.geomspace(mc_lo, mc_hi, n), psd_grid,
                                  freqs, rho_thr=RHO_THR, f_cut="isco")
    return float(np.polyfit(np.log(mc), np.log(d), 1)[0])


def volume_threshold_slope(sigma_ref):
    """d ln V / d ln rho_thr, measured rather than asserted.

    Analytically -3, because volume goes as distance cubed and distance goes as
    one over the threshold. Measured here through the same two functions the
    rest of the script uses, so a change in either shows up.
    """
    lo, hi = 6.0, 12.0
    v = [horizon.sensitive_volume_euclidean(
             horizon.horizon_distance(sigma_ref, D_REF_MPC, r))
         for r in (lo, hi)]
    return float((np.log(v[1]) - np.log(v[0])) / (np.log(hi) - np.log(lo)))


def main():
    strain, _, fs = dataio.load_strain("H1")
    w = dataio.load_waveforms()
    freqs = w["freqs"]
    f_psd, p = psd.welch_median(strain[:int(512 * fs)], fs)
    psd_grid = psd.psd_on_grid(f_psd, p, freqs)

    sigma_imr = horizon.sigma(w["h_imr"], psd_grid, freqs, 20, 1024)
    d_hor = horizon.horizon_distance(sigma_imr, D_REF_MPC, RHO_THR)

    # GW150914's own SNR bounds its distance from above: any orientation other
    # than optimal reproduces the same SNR only from closer in. Read from
    # results.json rather than retyped, so the two cannot drift apart.
    measured = json.loads((ROOT / "results.json").read_text(encoding="utf-8"))
    rho_observed = measured["h1_peak_snr"]

    mc_fit_max = fit_window_max(psd_grid, freqs)
    exponent = power_law_exponent(MCHIRP_FIT_MIN, mc_fit_max, psd_grid, freqs)
    exponent_brief = power_law_exponent(MCHIRP_FIT_MIN, MCHIRP_BRIEF_WINDOW_MAX,
                                        psd_grid, freqs)

    mc, curve = horizon.horizon_curve(
        np.geomspace(MCHIRP_FIT_MIN, MCHIRP_CURVE_MAX, 80),
        psd_grid, freqs, rho_thr=RHO_THR, f_cut="isco")
    peak = int(np.argmax(curve))

    values = {
        "sigma_imr_h1": sigma_imr,
        "horizon_gw150914_mpc": d_hor,
        "sensitive_volume_gpc3": horizon.sensitive_volume_euclidean(d_hor),
        "horizon_mchirp_exponent": exponent,
        "horizon_mchirp_exponent_brief_window": exponent_brief,
        "horizon_fit_window_max_mchirp": mc_fit_max,
        "horizon_band_fixed_tolerance": BAND_FIXED_TOLERANCE,
        "volume_threshold_log_slope": volume_threshold_slope(sigma_imr),
        "horizon_peak_mchirp": float(mc[peak]),
        "horizon_peak_mpc": float(curve[peak]),
        "distance_upper_bound_mpc": D_REF_MPC * sigma_imr / rho_observed,
    }
    path = ROOT / "results.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc.update(values)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")

    figure = figures.f03_horizon_vs_mchirp(mc, curve, float(w["mchirp"]), d_hor)

    choices = [
        f"detection threshold rho = {RHO_THR:g}, not the 9 of Roulet & Zaldarriaga 2019",
        "Euclidean sensitive volume: no redshift, no expansion",
        "H1 PSD estimated off-source from the first 512 s",
        "optimal orientation and sky position, which makes this a horizon and not "
        "a range; day 4's factor of 2.26 is what separates the two",
        "equal-mass binaries along the whole curve",
        f"waveform cut at f_ISCO, and the curve stopped at Mc = {MCHIRP_CURVE_MAX:g} "
        "Msun because above it f_ISCO falls below the 20 Hz band edge",
        f"fit window derived from BAND_FIXED_TOLERANCE = {BAND_FIXED_TOLERANCE} "
        f"(Mc <= {mc_fit_max:.3f}) instead of the brief's [1.5, 5], which is too "
        "wide for the band to count as fixed",
    ]
    statements = {
        "sigma_imr_h1":
            "Optimal SNR of the shipped IMRPhenomD waveform against the H1 PSD.",
        "horizon_gw150914_mpc":
            "Distance at which an optimally oriented GW150914 reaches rho = 8, in Mpc.",
        "sensitive_volume_gpc3":
            "Euclidean volume inside that horizon, in Gpc^3.",
        "horizon_mchirp_exponent":
            "Power-law slope of horizon distance against chirp mass, over the "
            "derived fixed-band window.",
        "horizon_mchirp_exponent_brief_window":
            "The same slope over the day-3 brief's [1.5, 5] Msun window, which is "
            "too wide for the band to count as fixed.",
        "horizon_fit_window_max_mchirp":
            "Largest chirp mass at which the ISCO cut still costs under 0.1% of sigma.",
        "horizon_band_fixed_tolerance":
            "The fraction of sigma the ISCO cut may cost inside the fit window, "
            "fixed before the window was computed.",
        "volume_threshold_log_slope":
            "d ln V / d ln rho_thr, measured through the same functions the rest "
            "of the analysis uses.",
        "horizon_peak_mchirp":
            "Chirp mass at which the horizon curve turns over, in Msun.",
        "horizon_peak_mpc":
            "Horizon distance at that turnover, in Mpc.",
        "distance_upper_bound_mpc":
            "Upper bound on GW150914's distance implied by its own SNR, in Mpc.",
    }
    producers = {
        "sigma_imr_h1": "src/gwsel/horizon.py::sigma",
        "horizon_gw150914_mpc": "src/gwsel/horizon.py::horizon_distance",
        "sensitive_volume_gpc3": "src/gwsel/horizon.py::sensitive_volume_euclidean",
        "horizon_mchirp_exponent": "scripts/s03_horizon.py::power_law_exponent",
        "horizon_mchirp_exponent_brief_window": "scripts/s03_horizon.py::power_law_exponent",
        "horizon_fit_window_max_mchirp": "scripts/s03_horizon.py::fit_window_max",
        "horizon_band_fixed_tolerance": "scripts/s03_horizon.py",
        "volume_threshold_log_slope": "scripts/s03_horizon.py::volume_threshold_slope",
        "horizon_peak_mchirp": "src/gwsel/horizon.py::horizon_curve",
        "horizon_peak_mpc": "src/gwsel/horizon.py::horizon_curve",
        "distance_upper_bound_mpc": "scripts/s03_horizon.py::main",
    }
    for slug, value in values.items():
        pv.record_number(
            slug, value, statements[slug], producers[slug],
            "Implemented the SNR-distance-volume chain, the horizon curve, and "
            "the band-fixed criterion the fit window is derived from.",
            "numpy for the fits and grids; the IMRPhenomD reference array ships "
            "with the course data.",
            choices)

    pv.record_claim(
        "threshold_is_a_distance",
        "An SNR threshold on a fixed waveform is a distance, and therefore a "
        "searched volume: for GW150914 at rho = 8 that is 1.97 Gpc and 32 Gpc^3, "
        "and halving the threshold multiplies the volume by eight.",
        ["tests/test_03_horizon.py",
         "src/gwsel/horizon.py::horizon_distance",
         "src/gwsel/horizon.py::sensitive_volume_euclidean"],
        ["horizon_gw150914_mpc", "sensitive_volume_gpc3",
         "volume_threshold_log_slope"])
    pv.record_claim(
        "selection_tilts_towards_heavy",
        "While the analysis band is fixed the horizon grows as chirp mass to the "
        "5/6, so heavier binaries are drawn from a larger volume and a catalogue "
        "over-represents them. The law stops holding once the merger itself falls "
        "into the band: the curve turns over near Mc = 27 Msun and falls after.",
        ["tests/test_03_horizon.py",
         "scripts/s03_horizon.py::fit_window_max",
         "Roulet & Zaldarriaga 2019, Fig. 3"],
        ["horizon_mchirp_exponent", "horizon_fit_window_max_mchirp",
         "horizon_peak_mchirp", "horizon_peak_mpc"])
    pv.record_figure(
        figure, "src/gwsel/figures.py::f03_horizon_vs_mchirp",
        "Horizon distance against chirp mass on log axes, with GW150914 marked. "
        "It rises as the 5/6 power while the signal fills the band, turns over "
        "near Mc = 27 Msun once the merger drops below the band, and falls after. "
        "Euclidean, so past a few Gpc it is a scale and not a distance.",
        "Computed the whole curve from our own waveform and the measured H1 PSD.",
        "matplotlib for the drawing.",
        choices,
        ["threshold_is_a_distance", "selection_tilts_towards_heavy"])

    print(json.dumps(values, indent=2))


if __name__ == "__main__":
    main()
