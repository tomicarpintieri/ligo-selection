"""Write provenance for one successful full reproduction run.

The report is ignored by Git because it records the local host and timestamp.
CI uploads it as an artifact, while the committed manifest and pinned
requirements define what a fresh run must use.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "MANIFEST.json"
OUT = ROOT / "artifacts" / "reproduction.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def git_status() -> list[str]:
    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        )
        return status.splitlines()
    except (OSError, subprocess.CalledProcessError):
        return []


def pinned_packages() -> dict[str, str]:
    packages = {}
    for line in (ROOT / "requirements.lock").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "==" in line and not line.startswith("#"):
            name, pinned = line.split("==", 1)
            packages[name] = version(name)
            if packages[name] != pinned:
                raise RuntimeError(f"{name} is {packages[name]}, expected {pinned}")
    return packages


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    inputs = {}
    for name, metadata in manifest["files"].items():
        path = ROOT / "data" / name
        digest = sha256(path)
        if digest != metadata["sha256"]:
            raise RuntimeError(f"input hash mismatch for {name}")
        inputs[name] = {"bytes": path.stat().st_size, "sha256": digest}

    status = git_status()
    report = {
        "schema_version": 1,
        "completed_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": git_commit(),
        "git_worktree_clean": not status,
        "git_status_porcelain": status,
        "python": sys.version,
        "platform": platform.platform(),
        "packages": pinned_packages(),
        "input_source": manifest["source"],
        "input_source_commit": manifest["source_commit"],
        "inputs": inputs,
        "outputs": {
            "results.json_sha256": sha256(ROOT / "results.json"),
            "page/index.html_sha256": sha256(ROOT / "page" / "index.html"),
        },
        "verification": "run_all.py completed and pytest -q passed before this report was written",
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
