import json
import pathlib
import sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
from gwsel import dataio, psd, horizon, figures
from gwsel import provenance as pv

H, _, fs = dataio.load_strain("H1")
w = dataio.load_waveforms()
fp, p = psd.welch_median(H[:int(512 * fs)], fs)
P = psd.psd_on_grid(fp, p, w["freqs"])
s = horizon.sigma(w["h_imr"], P, w["freqs"], 20, 1024)
d = horizon.horizon_distance(s, 400)
grid = np.geomspace(1.5, 80, 80)
mc, curve = horizon.horizon_curve(grid, P, w["freqs"], f_cut="isco")
fit = (mc >= 1.5) & (mc <= 5)
low_mc, low_curve = horizon.horizon_curve(np.geomspace(1.5, 5, 40), P, w["freqs"])
values = {"sigma_imr_h1": s, "horizon_gw150914_mpc": d,
          "sensitive_volume_gpc3": horizon.sensitive_volume_euclidean(d),
          "horizon_mchirp_exponent": float(np.polyfit(np.log(low_mc), np.log(low_curve), 1)[0]),
          "distance_upper_bound_mpc": 400 * s / 19.81039063634292}
path = ROOT / "results.json"
doc = json.loads(path.read_text())
doc.update(values)
path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
figures.f03_horizon_vs_mchirp(mc, curve, 31.29747284, d)
choices = ["threshold 8", "Euclidean volume", "off-source H1 PSD", "optimal orientation", "1.5-5 Msun fixed-band fit"]
for key, value in values.items():
    pv.record_number(key, value, key, "src/gwsel/horizon.py::horizon_distance", "Implemented SNR-distance scaling.", "numpy.", choices)
pv.record_claim("threshold_is_a_distance", "At fixed waveform, an SNR threshold maps directly to horizon distance.", ["tests/test_03_horizon.py"], ["horizon_gw150914_mpc", "sensitive_volume_gpc3"])
pv.record_claim("selection_tilts_towards_heavy", "At low mass the horizon scales as chirp mass to the 5/6, increasing the sampled volume for heavier binaries.", ["tests/test_03_horizon.py"], ["horizon_mchirp_exponent"])
pv.record_figure("figures/f03_horizon_vs_mchirp.png", "src/gwsel/figures.py::f03_horizon_vs_mchirp", "Horizon against chirp mass.", "Computed horizon curve.", "matplotlib.", choices, ["threshold_is_a_distance", "selection_tilts_towards_heavy"])
print(json.dumps(values, indent=2))
