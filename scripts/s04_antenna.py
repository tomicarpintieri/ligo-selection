import json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from gwsel import antenna
rng=np.random.default_rng(0); n=4_000_000
theta=np.arccos(rng.uniform(-1,1,n)); phi=rng.uniform(0,2*np.pi,n); psi=rng.uniform(0,2*np.pi,n); inc=np.arccos(rng.uniform(-1,1,n))
fp,fc=antenna.response(theta,phi,psi); w=antenna.projection_factor(fp,fc,inc)
v={'sky_mean_fplus_squared':float(np.mean(fp**2)),'sky_mean_fcross_squared':float(np.mean(fc**2)),'rms_projection_factor':float(np.sqrt(np.mean(w**2))),'horizon_over_range_factor':float(np.mean(w**3)**(-1/3))}
p=ROOT/'results.json';d=json.loads(p.read_text());d.update(v);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps(v,indent=2))
