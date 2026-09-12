"""Getting the arrays off disk, and refusing to hand back bytes we cannot vouch for.

Every loader checks the file against data/MANIFEST.json the first time it is
asked for it. That check is cheap next to everything downstream and it turns the
commonest silent failure -- a truncated or swapped data file -- into an
exception at the top of the run instead of a wrong number at the bottom.

Run `python scripts/fetch_data.py` if anything here says a file is missing.
"""
import hashlib
import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
MANIFEST = DATA / "MANIFEST.json"

_verified = set()


def manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def verify(name):
    """Check one file against the manifest. Cached: each file is hashed once."""
    if name in _verified:
        return
    path = DATA / name
    if not path.exists():
        raise FileNotFoundError(
            f"{path} is missing. Run:  python scripts/fetch_data.py")
    expected = manifest()["files"][name]["sha256"]
    got = sha256(path)
    if got != expected:
        raise ValueError(
            f"{name} does not match data/MANIFEST.json.\n"
            f"  found    {got}\n  expected {expected}\n"
            f"Run:  python scripts/fetch_data.py --force")
    _verified.add(name)


def verify_all():
    """Check every file the manifest names. Returns the list of names checked."""
    names = list(manifest()["files"])
    for n in names:
        verify(n)
    return names


def _load(name):
    verify(name)
    return np.load(DATA / name)


def load_strain(detector):
    """Strain for 'H1' or 'L1', as float64.

    Returns (strain, t0, fs). The shipped arrays are float32; everything
    downstream is float64, and the cast happens here rather than in five places.
    """
    d = _load(f"{detector}_gw150914.npz")
    return d["strain"].astype(np.float64), float(d["t0"]), float(d["fs"])


def load_waveforms():
    """LAL's two reference waveforms and the parameters they were made with.

    Keys: freqs, h_imr (IMRPhenomD), h_taylorf2_lal (TaylorF2), m1, m2, mchirp,
    distance_mpc (400.0), inclination (0.0, face-on), f_low_generated (20.0),
    fs, seg_seconds, approximant, approximant_tf2, note.

    h_taylorf2_lal is the array src/gwsel/waveform.py is measured against.
    """
    return _load("imr_gw150914.npz")


def load_reference_psd():
    """gwpy's PSD on the same H1 data, and the Advanced LIGO design curve.

    Returns a dict with freqs, psd_gwpy_median, f_design, psd_aligo_design.
    The first is the library answer our hand-written Welch is checked against;
    it is a target, never an input.
    """
    d = _load("psd_reference.npz")
    return {k: d[k] for k in ("freqs", "psd_gwpy_median",
                              "f_design", "psd_aligo_design")}
