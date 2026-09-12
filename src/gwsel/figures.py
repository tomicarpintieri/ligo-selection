"""One style for every figure, and one way to save them.

The style is the one day 2's reproduction used (day2/repro-gw150914/plots.py in
the course tree), kept identical so this project's figures sit beside those
without looking like they came from somewhere else.

Per-figure functions live here too, one per figure, named for the file they
write: f01_snr_timeseries(), f02_waveform_vs_lal(), and so on. A figure with no
function here is a figure nobody can regenerate.
"""
import pathlib

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
