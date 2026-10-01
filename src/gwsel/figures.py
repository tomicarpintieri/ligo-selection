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
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402

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
    # tight_layout fights fig.colorbar(ax=...): it re-lays out the axes over the
    # space the colorbar reserved, which drew the bar across the sky maps in
    # f05 and f06. A figure that already declares a layout engine keeps it.
    if fig.get_layout_engine() is None:
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


def _sky_grid(n_ra=241, n_dec=121):
    """Regular celestial grid, returned in Mollweide plotting coordinates."""
    # Mollweide plots longitude on [-pi, pi]. Building ra on [0, 2pi] and
    # wrapping it afterwards gives a grid that is not monotonic, and pcolormesh
    # drew a hard seam down the middle of every sky map. Build the plotting
    # longitude first; right ascension only ever enters as (ra - gmst), so a
    # shift of 2 pi is physically irrelevant.
    lon = np.linspace(-np.pi, np.pi, n_ra)
    dec = np.linspace(-np.pi / 2.0, np.pi / 2.0, n_dec)
    lon, dec = np.meshgrid(lon, dec)
    return lon, dec, lon


def f04_antenna_pattern():
    """Detector-frame total response, including the four geometric nulls."""
    from . import antenna
    phi = np.linspace(-np.pi, np.pi, 241)
    latitude = np.linspace(-np.pi / 2.0, np.pi / 2.0, 121)
    phi, latitude = np.meshgrid(phi, latitude)
    theta = np.pi / 2.0 - latitude
    f_plus, f_cross = antenna.response(theta, phi, 0.0)
    power = f_plus**2 + f_cross**2
    fig, ax = plt.subplots(figsize=(8.5, 4.8), layout="constrained",
                           subplot_kw={"projection": "mollweide"})
    image = ax.pcolormesh(phi, latitude, power, shading="auto", cmap="viridis", vmin=0, vmax=1)
    nulls = np.array([np.pi / 4.0, 3 * np.pi / 4.0, -3 * np.pi / 4.0, -np.pi / 4.0])
    ax.scatter(nulls, np.zeros(4), marker="x", color="white", s=42, label="four exact nulls")
    ax.grid(True, color="white", alpha=.35)
    ax.set_title("Detector-frame antenna response")
    # below the ellipse, not on it: inside the axes the label landed on the
    # -75 degree gridline annotation
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.01), frameon=False)
    fig.colorbar(image, ax=ax, orientation="horizontal", pad=.1, label=r"$F_+^2+F_\times^2$")
    return save(fig, "f04_antenna_pattern.png")


def _network_power(ra, dec, gps):
    from . import antenna
    h_plus, h_cross = antenna.response_earth("H1", ra, dec, 0.0, gps)
    l_plus, l_cross = antenna.response_earth("L1", ra, dec, 0.0, gps)
    h1 = h_plus**2 + h_cross**2
    l1 = l_plus**2 + l_cross**2
    return h1, l1, h1 + l1


def f05_network_skymap(gps, observed_delay_ms=-7.080):
    """H1, L1 and summed response in celestial coordinates at one GPS time."""
    from . import antenna
    ra, dec, lon = _sky_grid()
    h1, l1, network = _network_power(ra, dec, gps)
    delay = antenna.time_delay("H1", "L1", ra, dec, gps) * 1000.0
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), layout="constrained",
                             subplot_kw={"projection": "mollweide"})
    for ax, power, title in zip(axes, (h1, l1, network), ("H1", "L1", "H1 + L1 network")):
        image = ax.pcolormesh(lon, dec, power, shading="auto", cmap="magma", vmin=0, vmax=1)
        ax.contour(lon, dec, delay, levels=[observed_delay_ms], colors="cyan", linewidths=1.0)
        ax.set_title(title)
        ax.grid(True, color="white", alpha=.3)
    fig.colorbar(image, ax=axes, orientation="horizontal", pad=.1, label="polarization-independent response power")
    # supxlabel, not fig.text: constrained layout reserves room for it, so the
    # caption cannot land on top of the colorbar.
    fig.supxlabel("Cyan: directions consistent with the −7.08 ms delay — a ring, "
                  "not a localisation.", fontsize=10, color=MUTED)
    return save(fig, "f05_network_skymap.png")


def f06_rotation(gps, frames=24):
    """Save a 24-hour network sweep as GIF plus four static reference frames."""
    ra, dec, lon = _sky_grid(181, 91)
    sidereal_hour = 86164.0905 / 24.0
    times = gps + np.arange(frames) * sidereal_hour
    powers = [_network_power(ra, dec, time)[2] for time in times]

    fig, ax = plt.subplots(figsize=(7.5, 4.6), layout="constrained",
                           subplot_kw={"projection": "mollweide"})
    image = ax.pcolormesh(lon, dec, powers[0], shading="auto", cmap="magma", vmin=0, vmax=1)
    ax.grid(True, color="white", alpha=.3)
    title = ax.set_title("H1 + L1 response — sidereal hour 0")
    colorbar = fig.colorbar(image, ax=ax, orientation="horizontal", pad=.12, label="network response power")

    def update(index):
        image.set_array(powers[index].ravel())
        title.set_text(f"H1 + L1 response — sidereal hour {index:02d}")
        return image, title

    animation = FuncAnimation(fig, update, frames=frames, interval=180, blit=False)
    FIGDIR.mkdir(parents=True, exist_ok=True)
    animation.save(FIGDIR / "f06_rotation.gif", writer=PillowWriter(fps=6))
    plt.close(fig)

    panel_figure, axes = plt.subplots(2, 2, figsize=(9.5, 6.4), layout="constrained",
                                      subplot_kw={"projection": "mollweide"})
    for ax, index in zip(axes.ravel(), (0, frames // 4, frames // 2, 3 * frames // 4)):
        image = ax.pcolormesh(lon, dec, powers[index], shading="auto", cmap="magma", vmin=0, vmax=1)
        ax.set_title(f"sidereal hour {index:02d}")
        ax.grid(True, color="white", alpha=.3)
    panel_figure.colorbar(image, ax=axes.ravel().tolist(), orientation="horizontal", pad=.08, label="network response power")
    panels = save(panel_figure, "f06_rotation_panels.png")
    return "figures/f06_rotation.gif", panels


def f07_injection_efficiency(measured):
    """Recovery efficiency of the reproducible injection pilot versus distance."""
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    valid = np.isfinite(measured["efficiency"])
    ax.errorbar(measured["distance_mpc"][valid], measured["efficiency"][valid],
                yerr=measured["uncertainty"][valid], fmt="o-", color=TEAL,
                label="injected and recovered")
    ax.axhline(.5, color=MUTED, ls=":", label="50% efficiency")
    ax.set(xlabel="Luminosity distance (Mpc)", ylabel="Detection efficiency",
           ylim=(-.05, 1.05), title="H1–L1 injection-recovery pilot")
    ax.legend()
    return save(fig, "f07_injection_efficiency.png")
