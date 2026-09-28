import json,pathlib,pytest,numpy as np
from gwsel import antenna
r=json.loads((pathlib.Path(__file__).resolve().parents[1]/'results.json').read_text())
def test_h1_l1_light_travel_time():assert r['h1_l1_light_travel_ms']==pytest.approx(10.002,abs=.05)
def test_gmst_period():assert abs(np.angle(np.exp(1j*(antenna.gmst_from_gps(1e9+86164.0905)-antenna.gmst_from_gps(1e9)))))<1e-6
def test_network_beats_single():assert r['network_sky_average_gain']>=1
