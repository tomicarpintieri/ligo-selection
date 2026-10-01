import json,pathlib,numpy as np,pytest
from gwsel import antenna
r=json.loads((pathlib.Path(__file__).resolve().parents[1]/'results.json').read_text())
def test_overhead_is_unity():assert antenna.response(0,0,0)[0]==pytest.approx(1)
def test_overhead_cross_is_zero():assert antenna.response(0,0,0)[1]==pytest.approx(0)
def test_four_blind_directions():
 f,g=antenna.response(np.pi/2,np.pi/4,1.2);assert f==pytest.approx(0,abs=1e-12) and g==pytest.approx(0,abs=1e-12)
def test_mean_fplus_squared():assert r['sky_mean_fplus_squared']==pytest.approx(.2,abs=.001)
def test_mean_fcross_squared():assert r['sky_mean_fcross_squared']==pytest.approx(.2,abs=.001)
def test_fplus_fcross_uncorrelated():
 rng=np.random.default_rng(17);n=200000
 theta=np.arccos(rng.uniform(-1,1,n));phi=rng.uniform(0,2*np.pi,n);psi=rng.uniform(0,2*np.pi,n)
 fp,fc=antenna.response(theta,phi,psi);assert np.mean(fp*fc)==pytest.approx(0,abs=.001)
def test_rms_projection_factor():assert r['rms_projection_factor']==pytest.approx(.4,abs=.002)
def test_range_factor_2_26():assert r['horizon_over_range_factor']==pytest.approx(2.2649,abs=.01)
def test_bad_sky_sampler_fails():
 rng=np.random.default_rng(0);n=200000
 theta=rng.uniform(0,np.pi,n);phi=rng.uniform(0,2*np.pi,n);psi=rng.uniform(0,2*np.pi,n)
 fp,_=antenna.response(theta,phi,psi);assert abs(np.mean(fp**2)-.2)>.01
