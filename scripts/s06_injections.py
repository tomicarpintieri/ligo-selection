"""Run the reproducible H1--L1 inspiral-only injection-and-recovery pilot."""
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gwsel import dataio, figures, injections, provenance as pv, psd


def main():
    h1_strain, _, fs = dataio.load_strain("H1")
    l1_strain, _, l1_fs = dataio.load_strain("L1")
    if fs != l1_fs:
        raise ValueError("H1 and L1 sample rates differ")
    freqs = np.fft.rfftfreq(int(32 * fs), 1 / fs)
    h1_f, h1_p = psd.welch_median(h1_strain[:int(512 * fs)], fs)
    l1_f, l1_p = psd.welch_median(l1_strain[:int(512 * fs)], fs)
    p_h1 = psd.psd_on_grid(h1_f, h1_p, freqs)
    p_l1 = psd.psd_on_grid(l1_f, l1_p, freqs)
    population = injections.sample_population(96, np.random.default_rng(20261001), distance_max=600.0)
    recovered = injections.recover_population(
        population, {"strain": h1_strain, "fs": fs}, {"strain": l1_strain, "fs": fs},
        p_h1, p_l1, freqs, seed=20261002, threshold=8.0)
    background = injections.recover_population(
        population, {"strain": h1_strain, "fs": fs}, {"strain": l1_strain, "fs": fs},
        p_h1, p_l1, freqs, seed=20261002, threshold=8.0, inject=False)
    measured = injections.efficiency(population["distance_mpc"], recovered["detected"],
                                     np.linspace(100, 600, 7))
    figure = figures.f07_injection_efficiency(measured)
    values = {"injection_count": 96, "injection_network_threshold": 8.0,
              "injection_recovery_fraction": float(np.mean(recovered["detected"])),
              "injection_mean_network_snr": float(np.mean(recovered["rho_network"])),
              "injection_background_false_alarm_fraction": float(np.mean(background["detected"]))}
    path = ROOT / "results.json"
    results = json.loads(path.read_text(encoding="utf8")); results.update(values)
    path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf8")
    choices = ["96 injections", "population seed 20261001", "noise-window seed 20261002",
               "uniform component masses 5–20 Msun", "uniform-in-volume distances 100–600 Mpc",
               "isotropic sky, polarization and inclination", "SPA inspiral-only waveform",
               "incoherent quadrature network SNR", "network threshold 8"]
    for key, value in values.items():
        pv.record_number(key, value, key, "scripts/s06_injections.py::main",
                         "Injected the sampled population into off-source H1 and L1 strain and recovered it; the background control uses the same windows without injection.",
                         "numpy and the project matched-filter implementation.", choices)
    pv.record_claim("injection_pilot_measures_selection", "A reproducible H1–L1 injection-and-recovery pilot measures detection efficiency as a function of distance for an isotropic population.", ["tests/test_07_injections.py", "scripts/s06_injections.py"], ["injection_count", "injection_recovery_fraction", "injection_mean_network_snr"])
    pv.record_claim("injection_pilot_is_inspiral_only", "The pilot is not an IMR population campaign: it uses the validated SPA inspiral waveform and therefore remains conservative for heavy systems.", ["TASKS/day-2-waveform.md", "src/gwsel/injections.py"], [])
    pv.record_figure(figure, "src/gwsel/figures.py::f07_injection_efficiency", "Binned H1–L1 recovery efficiency against injected distance.", "Injected and recovered an isotropic source population in off-source strain.", "matplotlib.", choices, ["injection_pilot_measures_selection"])
    print(json.dumps(values, indent=2))


if __name__ == "__main__":
    main()
