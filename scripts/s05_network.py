import json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from gwsel import antenna
rng=np.random.default_rng(0); ra=rng.uniform(0,2*np.pi,100000); dec=np.arcsin(rng.uniform(-1,1,100000)); gps=1126259462.4
delay=antenna.time_delay('H1','L1',ra,dec,gps)
fp1,_=antenna.response_earth('H1',ra,dec,0,gps);fp2,_=antenna.response_earth('L1',ra,dec,0,gps)
v={'h1_l1_light_travel_ms':float(np.max(abs(delay))*1000),'network_sky_average_gain':float(np.mean(fp1**2+fp2**2)/np.mean(fp1**2))}
p=ROOT/'results.json';d=json.loads(p.read_text());d.update(v);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps(v,indent=2))
