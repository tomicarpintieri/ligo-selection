"""Reproduce the analysis from a clean checkout with the active Python environment.

This is the supported one-command entry point after installing requirements.
It obtains the pinned public inputs, verifies their hashes, regenerates every
derived output, runs the full test suite, and writes a machine-readable run
record in artifacts/reproduction.json.
"""

import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]


def run(*args):
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def main():
    run("scripts/fetch_data.py")
    run("run_all.py")
    print("\nReproduction complete. Run record: artifacts/reproduction.json")


if __name__ == "__main__":
    main()
