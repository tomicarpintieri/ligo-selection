"""Write the record of where a number, a claim or a figure came from.

Two files, both at the repository root, both the shape the .claude/provenance/
specs describe -- read those before changing anything here:

    provenance/numbers.json   one entry per reported number
    provenance/claims.yaml    what we assert, what backs it, and every figure

This module only writes them. It does not decide what goes in. The hook at
.claude/hooks/provenance_gate.py is what refuses to let work finish without a
complete record; these helpers just make writing one a one-liner.

Every call is a merge: an existing entry with the same key is replaced, others
are left alone. Re-running a script therefore updates its own record and touches
nothing else.
"""
import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
NUMBERS = ROOT / "provenance" / "numbers.json"
CLAIMS = ROOT / "provenance" / "claims.yaml"

# The six fields .claude/provenance/numbers.md requires. All are mandatory;
# `choices` may be [] but only written explicitly.
NUMBER_FIELDS = ("value", "statement", "produced_by",
                 "from_scratch", "from_library", "choices")


def _read_json(path, default):
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _read_yaml(path, default):
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return default
    return yaml.safe_load(path.read_text(encoding="utf-8")) or default


def _write_yaml(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(doc, sort_keys=False, default_flow_style=False,
                       allow_unicode=True, width=88),
        encoding="utf-8")


def record_number(slug, value, statement, produced_by,
                  from_scratch, from_library, choices):
    """One reported number, and the six things that make it checkable.

    produced_by is "<file>::<function>", relative to the repository root, and it
    has to be the function that actually computed the value -- not the script
    that printed it.
    """
    if not isinstance(choices, (list, tuple)):
        raise TypeError("choices must be a list; use [] when there was nothing "
                        "to decide, and say so explicitly")
    doc = _read_json(NUMBERS, {})
    doc[slug] = {
        "value": float(value) if isinstance(value, (int, float)) else value,
        "statement": statement,
        "produced_by": produced_by,
        "from_scratch": from_scratch,
        "from_library": from_library,
        "choices": list(choices),
    }
    NUMBERS.parent.mkdir(parents=True, exist_ok=True)
    NUMBERS.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8")
    return doc[slug]


def record_claim(claim_id, statement, evidence, numbers=()):
    """Something we are asking the reader to believe, and what backs it.

    A claim is not a description of what we did. Every slug in `numbers` must
    already exist in numbers.json -- record the numbers first.
    """
    doc = _read_yaml(CLAIMS, {})
    doc.setdefault("claims", [])
    doc.setdefault("figures", [])
    entry = {
        "id": claim_id,
        "statement": statement,
        "evidence": list(evidence),
        "numbers": list(numbers),
    }
    doc["claims"] = [c for c in doc["claims"] if c.get("id") != claim_id] + [entry]
    _write_yaml(CLAIMS, doc)
    return entry


def record_figure(file, produced_by, shows, from_scratch, from_library,
                  choices, supports=()):
    """A figure, written exactly as it sits on disk, relative to the root.

    `file` must match the path the gate sees, e.g. "figures/f01_snr.png".
    """
    doc = _read_yaml(CLAIMS, {})
    doc.setdefault("claims", [])
    doc.setdefault("figures", [])
    entry = {
        "file": file,
        "produced_by": produced_by,
        "shows": shows,
        "from_scratch": from_scratch,
        "from_library": from_library,
        "choices": list(choices),
        "supports": list(supports),
    }
    doc["figures"] = [f for f in doc["figures"] if f.get("file") != file] + [entry]
    _write_yaml(CLAIMS, doc)
    return entry


def load_numbers():
    return _read_json(NUMBERS, {})


def load_claims():
    return _read_yaml(CLAIMS, {"claims": [], "figures": []})
