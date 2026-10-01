import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from gwsel import dataio, waveform, psd, filtering, figures, provenance as pv, constants as k

w=dataio.load_waveforms()
# f_cut=None: LAL's shipped TaylorF2 runs to Nyquist, so the reference
# comparison is the one place in this project that wants no cutoff.
h,_=waveform.spa_inspiral(w['freqs'],38.8,33.35,400,f_cut=None)
H,t,fs=dataio.load_strain('H1'); fp,p=psd.welch_median(H[:int(512*fs)],fs); P=psd.psd_on_grid(fp,p,w['freqs'])
b=(w['freqs']>=20)&(w['freqs']<=150); ratio=abs(h[b])/abs(w['h_taylorf2_lal'][b])
snr=filtering.search(H,t,fs,h,P,w['freqs'],k.EVENT_GPS,32,20,1024,4*4096)['peak']
values={'amplitude_ratio_vs_lal':float(np.median(ratio)),'amplitude_ratio_std':float(np.std(ratio)),'match_vs_lal':waveform.match(h,w['h_taylorf2_lal'],P,w['freqs'],20,300),'snr_taylorf2_real_data':snr,'f_isco_gw150914':waveform.f_isco(72.15),'amplitude_mchirp_exponent':waveform.amplitude_mchirp_exponent(w['freqs'])}
path=ROOT/'results.json'; old=json.loads(path.read_text()) if path.exists() else {}; old.update(values); path.write_text(json.dumps(old,indent=2,sort_keys=True)+'\n')
choices=['3.5PN non-spinning TaylorF2 phase','0PN amplitude','full LAL comparison grid; f_ISCO reported as physical boundary','20-150 Hz amplitude band','20-300 Hz match band','Blanchet 2014 TaylorF2 coefficients']
for key in ('amplitude_ratio_vs_lal','amplitude_ratio_std','match_vs_lal','snr_taylorf2_real_data','f_isco_gw150914'): pv.record_number(key,values[key],key,'src/gwsel/waveform.py::spa_inspiral','Implemented non-spinning SPA waveform.','LAL reference waveform and Blanchet 2014 coefficients.',choices)
pv.record_number('amplitude_mchirp_exponent',values['amplitude_mchirp_exponent'],'Fitted log-log amplitude exponent across 25 equal-mass binaries from 5 to 50 solar masses at 50 Hz.','src/gwsel/waveform.py::amplitude_mchirp_exponent','Generated the SPA waveforms and fit their amplitude scaling.','numpy.polyfit.',choices + ['25 equal-mass binaries from 5 to 50 solar masses', 'amplitude sampled at 50 Hz'])
fig=figures.f02_waveform_vs_lal(w['freqs'],h,w['h_taylorf2_lal'],values['f_isco_gw150914'])
pv.record_claim('waveform_agrees_with_lal','Our non-spinning 3.5PN TaylorF2 waveform agrees with LAL on amplitude and phase.',['tests/test_02_waveform.py'],['amplitude_ratio_vs_lal','match_vs_lal'])
pv.record_claim('inspiral_only_is_a_floor','Inspiral-only templates underestimate heavy-system detectability; an IMR waveform is the alternative but is shipped only for one mass pair.',['TASKS/day-2-waveform.md'],['snr_taylorf2_real_data'])
pv.record_figure(fig,'src/gwsel/figures.py::f02_waveform_vs_lal','Amplitude ratio of our TaylorF2 waveform and LAL reference.','Computed SPA waveform.','matplotlib.',choices,['waveform_agrees_with_lal'])
