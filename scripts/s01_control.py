"""Reproduce the GW150914 single-detector control measurement."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from gwsel import constants as k
from gwsel import dataio, figures, filtering, provenance as pv, psd


def _write_results(values):
    path = ROOT / "results.json"
    current = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    current.update(values)
    path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def background_statistics(strain, t0, fs, htilde, psd_on_analysis_grid, freqs):
    """Measure independent off-source SNR samples and their loudest excursion."""
    guard = int(4 * fs)
    rho_squared = []
    loudest = []
    # 16-s-spaced centers leave 121 valid windows after a 80-s event exclusion.
    for centre_s in range(16, 2032, 16):
        if abs(centre_s - 1024) < 48:
            continue
        dtilde, _ = filtering.segment(strain, t0, fs, t0 + centre_s, k.SEG_S)
        rho, _ = filtering.matched_filter(dtilde, htilde, psd_on_analysis_grid,
                                          freqs, k.F_LOW, k.F_HIGH)
        interior = rho[guard:-guard]
        rho_squared.extend(interior[::int(fs)] ** 2)
        loudest.append(float(np.max(interior)))
    samples = np.asarray(rho_squared)
    return {"background_mean_rho2": float(np.mean(samples)),
            "background_rho2_sem": float(np.std(samples, ddof=1) / np.sqrt(samples.size)),
            "background_loudest_rho": float(np.max(loudest)),
            "background_gaussian_expected_loudest_rho": 5.708,
            "background_samples": int(samples.size), "background_windows": len(loudest)}


def main():
    h1_strain, h1_t0, fs = dataio.load_strain("H1")
    l1_strain, l1_t0, l1_fs = dataio.load_strain("L1")
    if l1_fs != fs:
        raise ValueError("H1 and L1 sample rates differ")
    waveforms = dataio.load_waveforms()
    freqs = np.fft.rfftfreq(int(k.SEG_S * fs), 1.0 / fs)

    h1_psd_freqs, h1_psd_raw = psd.welch_median(h1_strain[:int(512 * fs)], fs)
    l1_psd_freqs, l1_psd_raw = psd.welch_median(l1_strain, fs)
    h1_psd = psd.psd_on_grid(h1_psd_freqs, h1_psd_raw, freqs)
    l1_psd = psd.psd_on_grid(l1_psd_freqs, l1_psd_raw, freqs)
    args = (waveforms["h_imr"],)
    h1 = filtering.search(h1_strain, h1_t0, fs, *args, h1_psd, freqs,
                          k.EVENT_GPS, k.SEG_S, k.F_LOW, k.F_HIGH, int(4 * fs))
    l1 = filtering.search(l1_strain, l1_t0, fs, *args, l1_psd, freqs,
                          k.EVENT_GPS, k.SEG_S, k.F_LOW, k.F_HIGH, int(4 * fs))

    # Library reference is only a check on our hand-written estimator.
    all_freqs, all_psd = psd.welch_median(h1_strain, fs)
    reference = dataio.load_reference_psd()
    ref_at_welch = np.interp(all_freqs, reference["freqs"], reference["psd_gwpy_median"])
    band = (all_freqs >= k.F_LOW) & (all_freqs <= k.F_HIGH)
    welch_difference = float(np.median(np.abs(all_psd[band] - ref_at_welch[band]) /
                                       ref_at_welch[band]) * 100.0)
    whitened_variance = float(np.var(filtering.whiten(
        h1_strain[:int(k.SEG_S * fs)], fs, h1_psd_freqs, h1_psd_raw,
        k.F_LOW, k.F_HIGH)))
    background = background_statistics(h1_strain, h1_t0, fs, waveforms["h_imr"],
                                       h1_psd, freqs)
    values = {
        "h1_peak_snr": h1["peak"], "l1_peak_snr": l1["peak"],
        "h1_sigma": h1["sigma"], "h1_peak_gps": h1["gps"],
        "l1_peak_gps": l1["gps"],
        "time_delay_l1_minus_h1_ms": (l1["gps"] - h1["gps"]) * 1000.0,
        "welch_vs_gwpy_pct": welch_difference,
        "whitened_variance": whitened_variance,
        **background,
    }
    _write_results(values)

    choices = ["4 s Welch segments with 50% overlap", "median PSD for glitch robustness",
               "H1 PSD from its first 512 s off source", "20–1024 Hz analysis band",
               "Tukey window with alpha 0.125"]
    for slug, statement, producer in (
        ("h1_peak_snr", "Peak IMRPhenomD matched-filter SNR in H1.", "src/gwsel/filtering.py::peak"),
        ("l1_peak_snr", "Peak IMRPhenomD matched-filter SNR in L1.", "src/gwsel/filtering.py::peak"),
        ("h1_sigma", "Template norm sqrt(<h|h>) against the H1 PSD.", "src/gwsel/filtering.py::matched_filter"),
        ("time_delay_ms", "L1 arrival time minus H1 arrival time, in ms.", "src/gwsel/filtering.py::search"),
        ("welch_vs_gwpy_pct", "Median relative PSD difference from gwpy, in percent.", "src/gwsel/psd.py::welch_median"),
        ("background_mean_rho2", "Mean rho squared in independent off-source H1 samples.", "scripts/s01_control.py::background_statistics"),
        ("background_loudest_rho", "Loudest matched-filter SNR in the off-source H1 windows.", "scripts/s01_control.py::background_statistics"),
    ):
        source_key = "time_delay_l1_minus_h1_ms" if slug == "time_delay_ms" else slug
        pv.record_number(slug, values[source_key], statement, producer,
                         "Implemented the estimator and filter on the shared FFT grid.",
                         "Compared the PSD result with the shipped gwpy reference where applicable.", choices)
    figure = figures.f01_snr_timeseries(h1, l1, k.EVENT_GPS)
    pv.record_claim("control_gw150914", "This repository independently recovers GW150914 in both detectors with the expected SNR and arrival-time offset.",
                    ["tests/test_01_control.py", "src/gwsel/filtering.py::search"],
                    ["h1_peak_snr", "l1_peak_snr", "h1_sigma", "time_delay_ms", "welch_vs_gwpy_pct", "background_mean_rho2"])
    pv.record_figure(figure, "src/gwsel/figures.py::f01_snr_timeseries",
                     "H1 and L1 matched-filter SNR around GW150914, with their measured peaks and timing offset.",
                     "Computed and plotted the two filter outputs.", "matplotlib plotting.", choices,
                     ["control_gw150914"])
    print(json.dumps(values, indent=2))


if __name__ == "__main__":
    main()
