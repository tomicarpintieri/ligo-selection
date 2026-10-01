import numpy as np
import pytest
import json
import pathlib

from gwsel import injections

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_population_is_isotropic_and_volume_uniform():
    population = injections.sample_population(200000, np.random.default_rng(0))
    assert abs(np.mean(np.sin(population["dec"]))) < .005
    scaled = (population["distance_mpc"]**3 - 100**3) / (1800**3 - 100**3)
    assert np.mean(scaled) == pytest.approx(.5, abs=.005)


def test_network_snr_is_quadrature_sum():
    assert injections.network_snr(3.0, 4.0) == pytest.approx(5.0)


def test_efficiency_counts_and_fraction():
    measured = injections.efficiency([100, 200, 300, 400], [True, True, False, False], [0, 250, 500])
    assert measured["count"].tolist() == [2, 2]
    assert measured["efficiency"].tolist() == [1.0, 0.0]


def test_injection_pilot_recovers_more_than_background():
    results = json.loads((ROOT / "results.json").read_text())
    assert results["injection_count"] == 96
    assert results["injection_network_threshold"] == 8.0
    assert results["injection_recovery_fraction"] > results["injection_background_false_alarm_fraction"]
