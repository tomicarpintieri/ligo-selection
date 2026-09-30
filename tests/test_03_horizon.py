"""Acceptance checks for horizon distance and sensitive volume.

Run scripts/s03_horizon.py first; most of these read what it measured.
The two that recompute do so on purpose -- see test_horizon_turns_over.
"""
import json
import pathlib

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
r = json.loads((ROOT / "results.json").read_text(encoding="utf-8"))


def test_sigma_imr():
    assert r["sigma_imr_h1"] == pytest.approx(39.3971, abs=.01)


def test_horizon_gw150914():
    assert r["horizon_gw150914_mpc"] == pytest.approx(1969.9, abs=5)


def test_horizon_in_slide_range():
    assert 1.90 <= r["horizon_gw150914_mpc"] / 1000 <= 2.00


def test_volume_gpc3():
    assert r["sensitive_volume_gpc3"] == pytest.approx(32, abs=1)


def test_horizon_exponent_5_6():
    assert r["horizon_mchirp_exponent"] == pytest.approx(5 / 6, abs=.01)


def test_distance_bound_identity():
    assert r["distance_upper_bound_mpc"] == pytest.approx(795.5, abs=1)


def test_volume_threshold_slope():
    """Volume goes as distance cubed, so d ln V / d ln rho_thr is exactly -3.

    Halving the threshold multiplies the searched volume by eight. That is why
    a few percent in a pipeline is worth having.
    """
    assert r["volume_threshold_log_slope"] == pytest.approx(-3.0, abs=.01)


def test_horizon_turns_over(psd_h1, grid):
    """The curve rises, peaks, and falls -- and it is recomputed here to say so.

    This is the check that was missing when horizon_curve popped its cutoff
    argument inside its own loop, so that one mass of eighty got the ISCO cut
    and the rest got none. The published curve rose monotonically to 5204 Mpc
    at Mc = 80, where the answer is 359. A curve that only rises is the
    signature of that bug, so this test recomputes rather than reading the
    recorded peak: reading it back would only confirm the script agrees with
    itself.

    Physically: heavier means louder, until heavier means the merger falls out
    of the sensitive band. Both effects, one curve.
    """
    from gwsel import horizon

    mc, d = horizon.horizon_curve(np.geomspace(1.5, 80.0, 16), psd_h1,
                                  grid["freqs"], rho_thr=8.0, f_cut="isco")
    peak = int(np.argmax(d))
    assert 0 < peak < len(d) - 1, "no interior maximum: the curve never turns over"
    assert np.any(np.diff(d[:peak + 1]) > 0), "the curve never rises"
    assert np.any(np.diff(d[peak:]) < 0), "the curve never falls"
    assert mc[peak] == pytest.approx(r["horizon_peak_mchirp"], rel=.15)


def test_fit_window_is_derived_not_chosen(psd_h1, grid):
    """The 5/6 window has to follow from the stated criterion, not from taste.

    BAND_FIXED_TOLERANCE is fixed before the window is computed; the window is
    the largest chirp mass whose ISCO cut still costs less than that fraction
    of sigma. This pins both ends of that bisection, so the window cannot be
    quietly widened to make test_horizon_exponent_5_6 pass.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "s03_horizon", ROOT / "scripts" / "s03_horizon.py")
    s03 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s03)

    mc_max = r["horizon_fit_window_max_mchirp"]
    tol = r["horizon_band_fixed_tolerance"]
    assert tol == s03.BAND_FIXED_TOLERANCE

    inside = s03.band_fixed_ratio(mc_max * 0.99, psd_h1, grid["freqs"])
    outside = s03.band_fixed_ratio(mc_max * 1.05, psd_h1, grid["freqs"])
    assert inside >= tol, "the window includes a mass where the band is not fixed"
    assert outside < tol, "the window stops short of where the criterion allows"


def test_brief_window_is_recorded_as_too_wide():
    """The finding itself, kept as a check rather than only as prose.

    The day-3 brief's [1.5, 5] Msun window measures 0.8219, outside the +-0.01
    it also asks for, because at Mc = 5 the ISCO cut sits inside the analysis
    band rather than above it. The tolerance was not widened; the window was
    derived instead. If someone ever restores the wide window, the exponent
    test fails and this one explains why.
    """
    wide = r["horizon_mchirp_exponent_brief_window"]
    assert wide == pytest.approx(0.8219, abs=.002)
    assert abs(wide - 5 / 6) > .01, (
        "the wide window now passes; the finding recorded in NOTES.md no longer "
        "holds and should be revisited rather than left in place")
