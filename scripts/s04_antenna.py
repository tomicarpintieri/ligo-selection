import json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from gwsel import antenna, figures, provenance as pv


def antenna_averages(n=4_000_000, seed=0):
    """Monte-Carlo detector-frame averages with isotropic sky sampling."""
    rng=np.random.default_rng(seed)
    theta=np.arccos(rng.uniform(-1,1,n)); phi=rng.uniform(0,2*np.pi,n)
    psi=rng.uniform(0,2*np.pi,n); inc=np.arccos(rng.uniform(-1,1,n))
    fp,fc=antenna.response(theta,phi,psi); w=antenna.projection_factor(fp,fc,inc)
    return {'sky_mean_fplus_squared':float(np.mean(fp**2)),'sky_mean_fcross_squared':float(np.mean(fc**2)),'rms_projection_factor':float(np.sqrt(np.mean(w**2))),'horizon_over_range_factor':float(np.mean(w**3)**(-1/3))}


v=antenna_averages()
p=ROOT/'results.json';d=json.loads(p.read_text());d.update(v);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps(v,indent=2))
choices=['4,000,000 Monte-Carlo samples', 'random seed 0', 'theta measured from detector zenith', 'phi measured from the x arm', 'psi as polarization angle', 'uniform cos(theta) for isotropic sky sampling']
for key, value in v.items():
    pv.record_number(key,value,key,'scripts/s04_antenna.py::antenna_averages','Sampled the detector-frame antenna response and source inclination.','numpy random generator.',choices)
pv.record_claim('detector_has_blind_spots','An L-shaped detector has four exact geometric blind directions in its detector frame.',['tests/test_04_antenna.py'],['sky_mean_fplus_squared','sky_mean_fcross_squared'])
pv.record_claim('range_is_2p26_below_horizon','The volume-equivalent detector range is 2.2649 times smaller than its optimally oriented horizon.',['tests/test_04_antenna.py'],['horizon_over_range_factor','rms_projection_factor'])
figure=figures.f04_antenna_pattern()
pv.record_figure(figure,'src/gwsel/figures.py::f04_antenna_pattern','Detector-frame antenna response and its four exact null directions.','Evaluated the analytic antenna pattern on a regular angular grid.','matplotlib.',choices,['detector_has_blind_spots','range_is_2p26_below_horizon'])
