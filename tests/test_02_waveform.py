import json,pathlib,pytest
ROOT=pathlib.Path(__file__).resolve().parents[1]
@pytest.fixture(scope='module')
def r(): return json.loads((ROOT/'results.json').read_text())
def test_amplitude_matches_lal(r): assert r['amplitude_ratio_vs_lal']==pytest.approx(1,abs=.005)
def test_amplitude_ratio_is_flat(r): assert r['amplitude_ratio_std']<.01
def test_phase_match_lal(r): assert r['match_vs_lal']>.99
def test_snr_on_real_data(r): assert r['snr_taylorf2_real_data']==pytest.approx(11.358,abs=.05)
def test_f_isco_gw150914(r): assert r['f_isco_gw150914']==pytest.approx(61,abs=.5)
