"""One style for every figure, and one way to save them.

The style is the one day 2's reproduction used (day2/repro-gw150914/plots.py in
the course tree), kept identical so this project's figures sit beside those
without looking like they came from somewhere else.

Per-figure functions live here too, one per figure, named for the file they
write: f01_snr_timeseries(), f02_waveform_vs_lal(), and so on. A figure with no
function here is a figure nobody can regenerate.
"""
import pathlib

import numpy as np

import matplotlib

matplotlib.use("Agg")           # no display; this has to run headless
import matplotlib.pyplot as plt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIGDIR = ROOT / "figures"

INK, MUTED, GRID = "#1f2933", "#6b7684", "#dfe3e8"
ORANGE, BLUE, TEAL, RED = "#e8703a", "#2f6fb5", "#2a9d8f", "#c1121f"
SERIES = (ORANGE, BLUE, TEAL, RED)

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": GRID, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlesize": 12.5,
    "axes.titleweight": "600", "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.7, "grid.alpha": 0.9, "legend.frameon": False,
    "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 150,
})


def save(fig, name):
    """Write to figures/<name> and close. Returns the path, as the gate sees it.

    The returned string is what goes in provenance/claims.yaml under `file:`,
    so pass it straight to provenance.record_figure().
    """
    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGDIR / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  figures/{name}")
    return f"figures/{name}"


def f01_snr_timeseries(h1, l1, event_gps):
    """Plot the two single-detector matched-filter SNR time series.

    ``h1`` and ``l1`` are the dictionaries returned by ``filtering.search``.
    Their time axes are reconstructed from the segment start so the annotated
    offset is a measured GPS difference rather than a display-only shift.
    """
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    for label, result, colour in (("H1", h1, ORANGE), ("L1", l1, BLUE)):
        times = result["seg_start"] + np.arange(len(result["rho"])) / 4096.0
        relative_ms = (times - event_gps) * 1000.0
        ax.plot(relative_ms, result["rho"], color=colour, lw=1.0, label=label)
        ax.plot((result["gps"] - event_gps) * 1000.0, result["peak"], "o",
                color=colour, ms=5)
    h1_ms = (h1["gps"] - event_gps) * 1000.0
    l1_ms = (l1["gps"] - event_gps) * 1000.0
    midpoint = (h1_ms + l1_ms) / 2.0
    ax.annotate(f"L1 − H1 = {(l1['gps'] - h1['gps']) * 1000:.2f} ms",
                xy=(midpoint, max(h1["peak"], l1["peak"])),
                xytext=(midpoint + 20, max(h1["peak"], l1["peak"]) - 3),
                arrowprops={"arrowstyle": "-", "color": MUTED}, color=INK)
    ax.set(xlim=(-1000, 1000), ylim=(0, None), xlabel="Time from GW150914 (ms)",
           ylabel="Matched-filter SNR", title="GW150914 recovered independently")
    ax.legend()
    return save(fig, "f01_snr_timeseries.png")


def f02_waveform_vs_lal(freqs, ours, lal, f_isco):
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(8, 6), sharex=True,
                                      gridspec_kw={"height_ratios": (2, 1)})
    valid = (freqs >= 20) & (freqs <= 300)
    top.loglog(freqs[valid], abs(ours[valid]), label="ours", color=ORANGE)
    top.loglog(freqs[valid], abs(lal[valid]), label="LAL TaylorF2", color=BLUE, ls="--")
    top.axvline(f_isco, color=MUTED, ls=":", label=f"f_ISCO = {f_isco:.1f} Hz")
    top.set(ylabel="|h(f)|", title="TaylorF2 amplitude comparison")
    top.legend()
    bottom.semilogx(freqs[valid], abs(ours[valid]) / abs(lal[valid]), color=TEAL)
    bottom.axhline(1, color=MUTED, ls=":")
    bottom.set(xlabel="Frequency (Hz)", ylabel="ours / LAL", ylim=(.98, 1.02))
    return save(fig, "f02_waveform_vs_lal.png")

def f03_horizon_vs_mchirp(mchirp, distance, gw_mc, gw_distance):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.loglog(mchirp, distance, color=ORANGE)
    ax.scatter([gw_mc], [gw_distance], color=BLUE, label="GW150914")
    ax.set(xlabel="Chirp mass (Msun)", ylabel="Horizon distance (Mpc)",
           title="Horizon versus chirp mass (Euclidean)")
    ax.legend()
    return save(fig, "f03_horizon_vs_mchirp.png")
