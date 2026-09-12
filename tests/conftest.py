"""Shared fixtures. Everything expensive is loaded once per session.

The data fixtures are raw: they hand back what is on disk, already checked
against data/MANIFEST.json. The derived fixtures (the PSDs, the analysis grid)
depend on code that is written day by day, so they will raise
NotImplementedError until the module they need exists. That is the intended
signal, not a broken test rig.
"""
import numpy as np
import pytest

from gwsel import constants as k
from gwsel import dataio


@pytest.fixture(scope="session")
def manifest_checked():
    """Every data file matches its recorded hash. Nothing else may assume it."""
    return dataio.verify_all()


@pytest.fixture(scope="session")
def h1(manifest_checked):
    strain, t0, fs = dataio.load_strain("H1")
    return {"strain": strain, "t0": t0, "fs": fs}


@pytest.fixture(scope="session")
def l1(manifest_checked):
    strain, t0, fs = dataio.load_strain("L1")
    return {"strain": strain, "t0": t0, "fs": fs}


@pytest.fixture(scope="session")
def waveforms(manifest_checked):
    """LAL's IMRPhenomD and TaylorF2 for GW150914, at 400 Mpc, face-on."""
    return dataio.load_waveforms()


@pytest.fixture(scope="session")
def reference_psd(manifest_checked):
    """gwpy's PSD and the Advanced LIGO design curve."""
    return dataio.load_reference_psd()


@pytest.fixture(scope="session")
def grid():
    """The analysis frequency grid: 32 s at 4096 Hz, and the 20-1024 Hz band.

    Every waveform, PSD and filter output in this project lives on this grid.
    Mixing grids is the quiet way to get a wrong SNR, so there is exactly one.
    """
    n = int(k.SEG_S * k.FS)
    freqs = np.fft.rfftfreq(n, 1.0 / k.FS)
    return {
        "n": n,
        "freqs": freqs,
        "df": float(freqs[1] - freqs[0]),
        "band": (freqs >= k.F_LOW) & (freqs <= k.F_HIGH),
        "guard": int(4 * k.FS),
    }


@pytest.fixture(scope="session")
def psd_h1(h1, grid):
    """H1 noise PSD on the analysis grid, estimated OFF-SOURCE.

    Off-source matters: the event sits at t = 1024 s into the H1 array, and a
    PSD estimated from data containing the signal partly whitens the signal
    away. Day 2 used the first 512 s.
    """
    from gwsel import psd as psd_mod
    off = int(512 * h1["fs"])
    f, p = psd_mod.welch_median(h1["strain"][:off], h1["fs"])
    return psd_mod.psd_on_grid(f, p, grid["freqs"])


@pytest.fixture(scope="session")
def psd_l1(l1, grid):
    """L1 gets its OWN PSD. The two detectors do not share a noise curve."""
    from gwsel import psd as psd_mod
    f, p = psd_mod.welch_median(l1["strain"], l1["fs"])
    return psd_mod.psd_on_grid(f, p, grid["freqs"])
