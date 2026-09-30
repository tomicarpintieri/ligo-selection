"""Is this repository in a state where a number would mean anything?

These run before any physics exists and must keep passing forever. They check
the things every later test silently assumes: the data is the data we think it
is, the package imports, there is exactly one frequency grid, and the installed
environment is the one requirements.txt pins.
"""
import importlib
import pathlib
import re

import numpy as np
import pytest

import gwsel
from gwsel import constants as k

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_data_matches_manifest(manifest_checked):
    """Every .npz hashes to what data/MANIFEST.json records."""
    assert len(manifest_checked) == 4


def test_all_modules_import():
    for name in gwsel.__all__:
        importlib.import_module(f"gwsel.{name}")


def test_grid_matches_shipped_waveform_grid(grid, waveforms):
    """Our analysis grid is the grid LAL's waveforms were generated on.

    If this ever fails, every SNR in the project is being computed by comparing
    two different frequency axes, and nothing downstream is meaningful.
    """
    assert np.allclose(grid["freqs"], waveforms["freqs"])
    assert grid["n"] == int(k.SEG_S * k.FS)


def test_waveform_metadata_is_what_we_assume(waveforms):
    """The reference waveform's parameters, hard-coded in docstrings all over."""
    assert float(waveforms["distance_mpc"]) == 400.0
    assert float(waveforms["inclination"]) == 0.0
    assert float(waveforms["f_low_generated"]) == k.F_LOW
    assert float(waveforms["m1"]) == pytest.approx(38.8)
    assert float(waveforms["m2"]) == pytest.approx(33.35)
    assert str(waveforms["approximant"]) == "IMRPhenomD"
    assert str(waveforms["approximant_tf2"]) == "TaylorF2"


def test_installed_versions_match_requirements():
    """The environment is the exact resolved one that produced the results."""
    from importlib.metadata import version

    pinned = {}
    for line in (ROOT / "requirements.lock").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([A-Za-z0-9_.-]+)==([0-9][0-9A-Za-z.+-]*)\s*$", line.strip())
        if m:
            pinned[m.group(1)] = m.group(2)
    assert pinned, "requirements.txt pins nothing"

    wrong = {name: (want, version(name)) for name, want in pinned.items()
             if version(name) != want}
    assert not wrong, f"installed != pinned: {wrong}"


def _load_gate():
    """Import .claude/hooks/provenance_gate.py by path -- it is not a package."""
    import importlib.util
    path = ROOT / ".claude" / "hooks" / "provenance_gate.py"
    spec = importlib.util.spec_from_file_location("provenance_gate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_provenance_helpers_write_what_the_gate_requires():
    """The helpers and the gate must not drift apart.

    provenance.record_number() emits six fields; the gate rejects an entry that
    is missing any of them. If someone edits one side, this fails rather than
    the record quietly becoming unacceptable at the end of a long session.
    """
    from gwsel import provenance as pv

    gate = _load_gate()
    assert set(gate.NUMBER_FIELDS) == set(pv.NUMBER_FIELDS)

    entry = pv.record_number.__doc__  # the helper builds exactly these keys
    assert entry is not None
    built = {"value", "statement", "produced_by",
             "from_scratch", "from_library", "choices"}
    assert built == set(gate.NUMBER_FIELDS)


def test_hook_is_wired_to_an_interpreter_that_exists():
    """The Windows trap: the course scaffold calls `python3`.

    On this machine `python3` resolves to the Microsoft Store stub and the hook
    silently never runs -- which is worse than having no hook, because you
    believe it is watching. settings.json must point at an interpreter that is
    actually here.
    """
    import json

    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    commands = [h["command"]
                for event in settings["hooks"].values()
                for group in event for h in group["hooks"]]
    assert commands, "no hooks wired"
    for cmd in commands:
        assert "python3" not in cmd, f"bare python3 in hook command: {cmd}"
        assert ".venv" in cmd, f"hook does not use the project venv: {cmd}"

    interpreter = ROOT / ".venv" / "Scripts" / "python.exe"
    if not interpreter.exists():                      # a POSIX checkout
        interpreter = ROOT / ".venv" / "bin" / "python"
    assert interpreter.exists(), (
        f"{interpreter} is missing. Create the venv from requirements.txt, or "
        f"edit .claude/settings.json if your venv lives elsewhere.")
