"""Regenerate every derived result, run the full test suite, then record the run."""

import pathlib
import subprocess
import sys

ROOT=pathlib.Path(__file__).resolve().parent
for name in ('s01_control.py','s02_waveform.py','s03_horizon.py','s04_antenna.py','s05_network.py','make_page.py'):
    subprocess.run([sys.executable,str(ROOT/'scripts'/name)],check=True)
subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(ROOT/'scripts'/'write_reproduction_report.py')],check=True)
