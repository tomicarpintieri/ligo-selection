import json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from gwsel import antenna, figures, provenance as pv


def network_summary(n=100000, seed=0, gps=1126259462.4):
    """Measure timing extent and two-detector response gain on an isotropic sky."""
    rng=np.random.default_rng(seed); ra=rng.uniform(0,2*np.pi,n); dec=np.arcsin(rng.uniform(-1,1,n))
    delay=antenna.time_delay('H1','L1',ra,dec,gps)
    fp1,_=antenna.response_earth('H1',ra,dec,0,gps);fp2,_=antenna.response_earth('L1',ra,dec,0,gps)
    baseline = antenna._site_position(antenna.DETECTORS['L1']) - antenna._site_position(antenna.DETECTORS['H1'])
    return {'h1_l1_light_travel_ms':float(np.linalg.norm(baseline) / antenna.k.C * 1000),'network_sky_average_gain':float(np.mean(fp1**2+fp2**2)/np.mean(fp1**2))}


v=network_summary()
p=ROOT/'results.json';d=json.loads(p.read_text());d.update(v);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps(v,indent=2))
choices=['100,000 isotropic sky directions', 'random seed 0', 'GPS 1126259462.4', 'network response as sum of detector response squared', 'LIGO T030215 H1/L1 site coordinates', 'WGS84 Earth-fixed baseline for the light-travel bound']
for key, value in v.items():
    pv.record_number(key,value,key,'scripts/s05_network.py::network_summary','Sampled timing and antenna response over the celestial sphere.','Published H1 and L1 coordinates transcribed into gwsel.antenna.',choices)
pv.record_claim('network_covers_the_blind_spots','The combined H1–L1 response has no common blind direction on the sampled sky.',['tests/test_05_network.py'],['network_sky_average_gain'])
pv.record_claim('detectability_depends_on_time_of_day','Because detector response is Earth-fixed, the network response sweeps across celestial coordinates in one sidereal day.',['figures/f06_rotation.gif'],[])
pv.record_claim('gw150914_timing_is_consistent','The measured −7.08 ms H1–L1 delay selects a non-empty sky ring; it is a consistency check, not a localisation.',['tests/test_05_network.py'],['time_delay_l1_minus_h1_ms','h1_l1_light_travel_ms'])
map_figure=figures.f05_network_skymap(1126259462.4)
gif_figure, panels_figure=figures.f06_rotation(1126259462.4)
pv.record_figure(map_figure,'src/gwsel/figures.py::f05_network_skymap','H1, L1 and combined celestial response, with the −7.08 ms timing ring.','Evaluated both detector antenna patterns and the geometric delay over a sky grid.','matplotlib.',choices,['network_covers_the_blind_spots','gw150914_timing_is_consistent'])
pv.record_figure(gif_figure,'src/gwsel/figures.py::f06_rotation','A sidereal day of combined network response sweeping across the celestial sphere.','Evaluated the Earth-fixed antenna pattern in 24 frames.','matplotlib Pillow writer.',choices + ['24 sidereal-hour frames'],['detectability_depends_on_time_of_day'])
pv.record_figure(panels_figure,'src/gwsel/figures.py::f06_rotation','Four static frames sampled from the sidereal-day response sweep.','Evaluated the Earth-fixed antenna pattern at four sidereal hours.','matplotlib.',choices + ['24 sidereal-hour frames'],['detectability_depends_on_time_of_day'])
