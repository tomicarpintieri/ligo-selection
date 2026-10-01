import json,pathlib,pytest
import numpy as np

from gwsel import waveform
ROOT=pathlib.Path(__file__).resolve().parents[1]
@pytest.fixture(scope='module')
def r(): return json.loads((ROOT/'results.json').read_text())
def test_amplitude_matches_lal(r): assert r['amplitude_ratio_vs_lal']==pytest.approx(1,abs=.005)
def test_amplitude_ratio_is_flat(r): assert r['amplitude_ratio_std']<.01
def test_phase_match_lal(r): assert r['match_vs_lal']>.99
def test_snr_on_real_data(r): assert r['snr_taylorf2_real_data']==pytest.approx(11.358,abs=.05)
def test_f_isco_gw150914(r): assert r['f_isco_gw150914']==pytest.approx(61,abs=.5)

def test_amplitude_mchirp_exponent(r):
    assert r['amplitude_mchirp_exponent'] == pytest.approx(5 / 6, abs=.001)

def test_amplitude_mchirp_exponent_uses_full_frequency_grid(grid):
    assert waveform.amplitude_mchirp_exponent(grid['freqs']) == pytest.approx(5 / 6, abs=.001)

def test_match_beats_0pn(waveforms, psd_h1):
    freqs = waveforms['freqs']
    h35, _ = waveform.spa_inspiral(freqs, 38.8, 33.35, 400.0, pn_order=3.5)
    h0, _ = waveform.spa_inspiral(freqs, 38.8, 33.35, 400.0, pn_order=0.0)
    reference = waveforms['h_taylorf2_lal']
    assert waveform.match(h35, reference, psd_h1, freqs, 20, 300) > waveform.match(h0, reference, psd_h1, freqs, 20, 300)

def test_match_is_normalised(grid, psd_h1):
    freqs = grid['freqs']
    h, _ = waveform.spa_inspiral(freqs, 12.0, 12.0, 400.0)
    assert waveform.match(2.0 * h, h, psd_h1, freqs, 20, 300) == pytest.approx(1.0, abs=1e-12)

def test_amplitude_inverse_distance(grid):
    h_distance, _ = waveform.spa_inspiral(grid['freqs'], 12.0, 12.0, 400.0)
    h_twice_distance, _ = waveform.spa_inspiral(grid['freqs'], 12.0, 12.0, 800.0)
    assert np.allclose(h_twice_distance, h_distance / 2.0, rtol=0.0, atol=1e-12)

def test_spin_argument_refuses(grid):
    with pytest.raises(NotImplementedError):
        waveform.spa_inspiral(grid['freqs'], 12.0, 12.0, 400.0, chi1z=0.1)
