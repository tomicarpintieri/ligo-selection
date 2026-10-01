import importlib
import json
import pathlib
import re

import yaml

ROOT=pathlib.Path(__file__).resolve().parents[1]
def test_no_placeholder_survives():
 p=ROOT/'page'/'index.html';assert p.exists();assert not re.search(r'__[A-Za-z0-9_]+__',p.read_text())
def test_run_all_is_complete():
 s=(ROOT/'run_all.py').read_text();assert 's01_control.py' in s and 's05_network.py' in s and 'write_reproduction_report.py' in s


def _numbers():
    return json.loads((ROOT / 'provenance' / 'numbers.json').read_text())


def _claims():
    return yaml.safe_load((ROOT / 'provenance' / 'claims.yaml').read_text())


def test_every_page_number_is_recorded():
    template = (ROOT / 'page' / 'template.html').read_text(encoding='utf8')
    substituted = set(re.findall(r'__([A-Za-z0-9_]+)__', template))
    assert substituted <= set(_numbers())


def test_every_result_number_is_recorded():
    results = json.loads((ROOT / 'results.json').read_text())
    numeric_results = {key for key, value in results.items()
                       if isinstance(value, (int, float)) and not isinstance(value, bool)}
    assert numeric_results <= set(_numbers())


def test_every_figure_has_provenance():
    recorded = {entry['file'] for entry in _claims()['figures']}
    generated = {path.relative_to(ROOT).as_posix()
                 for path in (ROOT / 'figures').iterdir() if path.is_file()}
    assert generated <= recorded


def test_every_claim_resolves():
    numbers = set(_numbers())
    for claim in _claims()['claims']:
        assert set(claim['numbers']) <= numbers


def test_every_figure_has_a_producer():
    for figure in _claims()['figures']:
        module_path, function = figure['produced_by'].split('::')
        module_name = module_path.removesuffix('.py').replace('/', '.')
        module = importlib.import_module(module_name.replace('src.', ''))
        assert callable(getattr(module, function, None))
