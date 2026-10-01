import json,pathlib,pytest,numpy as np
from gwsel import antenna, constants as k
r=json.loads((pathlib.Path(__file__).resolve().parents[1]/'results.json').read_text())
def test_h1_l1_light_travel_time():assert r['h1_l1_light_travel_ms']==pytest.approx(k.H1_L1_LIGHT_TRAVEL_MS,abs=.001)
def test_gmst_period():assert abs(np.angle(np.exp(1j*(antenna.gmst_from_gps(1e9+86164.0905)-antenna.gmst_from_gps(1e9)))))<1e-6
def test_gmst_vs_astropy():
 astropy=pytest.importorskip('astropy.time')
 gps=1126259462.4
 expected=astropy.Time(gps,format='gps',scale='utc').sidereal_time('mean','greenwich').rad
 error=np.angle(np.exp(1j*(antenna.gmst_from_gps(gps)-expected)))
 assert abs(error)<2e-5
def test_time_delay_bounded():
 rng=np.random.default_rng(3);ra=rng.uniform(0,2*np.pi,100000);dec=np.arcsin(rng.uniform(-1,1,100000))
 assert np.max(abs(antenna.time_delay('H1','L1',ra,dec,1126259462.4)))*1000<=k.H1_L1_LIGHT_TRAVEL_MS+1e-9
def test_gw150914_delay_ring_nonempty():
 rng=np.random.default_rng(4);ra=rng.uniform(0,2*np.pi,500000);dec=np.arcsin(rng.uniform(-1,1,500000))
 delay=antenna.time_delay('H1','L1',ra,dec,1126259462.4)*1000
 assert np.count_nonzero(abs(delay+7.080)<.02)>0
def test_sky_average_invariant():
 rng=np.random.default_rng(5);ra=rng.uniform(0,2*np.pi,200000);dec=np.arcsin(rng.uniform(-1,1,200000));psi=rng.uniform(0,2*np.pi,200000)
 for gps in (1e9,1126259462.4,1e9+86164.0905):
  fp,_=antenna.response_earth('H1',ra,dec,psi,gps);assert np.mean(fp**2)==pytest.approx(.2,abs=.001)
def test_network_beats_single():
 ra=np.linspace(0,2*np.pi,721);dec=np.linspace(-np.pi/2,np.pi/2,361);ra,dec=np.meshgrid(ra,dec)
 hfp,hfc=antenna.response_earth('H1',ra,dec,0,1126259462.4);lfp,lfc=antenna.response_earth('L1',ra,dec,0,1126259462.4)
 single=hfp**2+hfc**2;network=single+lfp**2+lfc**2
 assert np.min(single)<1e-5 and np.min(network)>1e-4
