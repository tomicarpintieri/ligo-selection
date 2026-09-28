import json
import pathlib
import pytest

r = json.loads((pathlib.Path(__file__).resolve().parents[1] / "results.json").read_text())

def test_sigma_imr(): assert r["sigma_imr_h1"] == pytest.approx(39.3971, abs=.01)
def test_horizon_gw150914(): assert r["horizon_gw150914_mpc"] == pytest.approx(1969.9, abs=5)
def test_horizon_in_slide_range(): assert 1.90 <= r["horizon_gw150914_mpc"] / 1000 <= 2.00
def test_volume_gpc3(): assert r["sensitive_volume_gpc3"] == pytest.approx(32, abs=1)
def test_horizon_exponent_5_6(): assert r["horizon_mchirp_exponent"] == pytest.approx(5/6, abs=.01)
def test_distance_bound_identity(): assert r["distance_upper_bound_mpc"] == pytest.approx(795.5, abs=1)
