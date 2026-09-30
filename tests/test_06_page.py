import pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
def test_no_placeholder_survives():
 p=ROOT/'page'/'index.html';assert p.exists();assert not re.search(r'__[A-Za-z0-9_]+__',p.read_text())
def test_run_all_is_complete():
 s=(ROOT/'run_all.py').read_text();assert 's01_control.py' in s and 's05_network.py' in s and 'write_reproduction_report.py' in s
