"""Acceptance checks for the GW150914 control measurement."""
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def results():
    path = ROOT / "results.json"
    assert path.exists(), "run .venv\\Scripts\\python.exe scripts\\s01_control.py first"
    return json.loads(path.read_text(encoding="utf-8"))


def test_h1_peak_snr(results):
    assert results["h1_peak_snr"] == pytest.approx(19.8104, abs=0.01)


def test_l1_peak_snr(results):
    assert results["l1_peak_snr"] == pytest.approx(13.5432, abs=0.01)


def test_h1_sigma(results):
    assert results["h1_sigma"] == pytest.approx(39.3971, abs=0.01)


def test_gps_peak(results):
    assert results["h1_peak_gps"] == pytest.approx(1126259462.4233, abs=0.01)


def test_time_delay_l1_minus_h1_ms(results):
    assert results["time_delay_l1_minus_h1_ms"] == pytest.approx(-7.080, abs=0.2)


def test_welch_vs_gwpy_pct(results):
    assert results["welch_vs_gwpy_pct"] < 0.01


def test_whitened_variance(results):
    assert results["whitened_variance"] == pytest.approx(0.9650, abs=0.02)


@pytest.mark.slow
def test_background_mean_rho2(results):
    assert results["background_mean_rho2"] == pytest.approx(2.0, abs=3 * results["background_rho2_sem"])
    assert results["background_mean_rho2"] == pytest.approx(2.0176, abs=0.01)


@pytest.mark.slow
def test_no_signal_in_background(results):
    assert results["background_loudest_rho"] == pytest.approx(6.316, abs=0.01)
    assert results["background_loudest_rho"] > results["background_gaussian_expected_loudest_rho"]
