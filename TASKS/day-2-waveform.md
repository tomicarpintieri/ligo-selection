# Day 2 — A waveform with an amplitude that means something

## Objective

Write our own frequency-domain inspiral, and prove it agrees with LAL's.

Day 1's templates are good enough to *search* with, because the matched filter
normalises the amplitude away. This project has to ask whether a source at a
given distance is detectable, and for that the amplitude has to be physical.
That is what today adds — and it is checkable to three decimal places, because
`data/imr_gw150914.npz` ships LAL's answer for exactly these parameters.

## Context — read these first

- `CLAUDE.md`, and the docstrings in `src/gwsel/waveform.py`, which state every
  target below.
- `data/imr_gw150914.npz['h_taylorf2_lal']` is the reference: LAL's TaylorF2 for
  m1 = 38.8, m2 = 33.35 Msun, 400 Mpc, face-on (iota = 0), from 20 Hz, on the
  32 s / 4096 Hz grid. `load_waveforms()` in `dataio.py` hands it to you with the
  parameters attached.
- `filtering.matched_filter` from day 1. `match()` must reuse it rather than
  restate the inner product.
- `NOTES.md`, the entry about 11.36 and f_ISCO. Read it before you are surprised
  by it.

## Build

**1. `src/gwsel/waveform.py`** — `chirp_mass`, `symmetric_mass_ratio`, `f_isco`,
`spa_inspiral`, `match`.

The phase goes to 3.5PN, because that is what LAL's TaylorF2 uses by default and
matching it is the entire point. The coefficients are a published table:
transcribe them and cite where from, in `from_library` and in the claim's
`evidence`. Nothing here is derived by hand.

The amplitude is 0PN: proportional to chirp mass to the 5/6 and to 1/distance.

`chi1z` and `chi2z` are in the signature so that week 3's aligned-spin work is an
edit rather than a rewrite. Anything non-zero must raise `NotImplementedError`.
Silently ignoring a spin argument is worse than not having one.

**2. `scripts/s02_waveform.py`** — the comparison against LAL, the numbers into
`results.json`, the provenance records, the figure.

**3. `figures.f02_waveform_vs_lal()`** — two panels: the amplitude of ours and
LAL's on log axes above, their ratio below with a line at 1.0. Mark f_ISCO.

**4. `tests/test_02_waveform.py`**.

## Acceptance

| test | quantity | target | tolerance |
|---|---|---|---|
| `test_amplitude_matches_lal` | median amplitude ratio ours/LAL, 20-150 Hz | 1.000 | 0.005 |
| `test_amplitude_ratio_is_flat` | standard deviation of that ratio | 0 | below 0.01 |
| `test_phase_match_lal` | match over time and phase, PSD-weighted, 20-300 Hz | 1.0 | above 0.99 |
| `test_match_beats_0pn` | match at 3.5PN exceeds match at 0PN | — | strict |
| `test_snr_on_real_data` | peak SNR of our waveform against real H1 | 11.358 | 0.05 |
| `test_amplitude_inverse_distance` | amplitude at 2D equals amplitude at D over 2 | exact | 1e-12 |
| `test_amplitude_mchirp_exponent` | fitted exponent of amplitude against chirp mass | 0.83333 | 0.001 |
| `test_f_isco_gw150914` | f_ISCO at total mass 72.15 Msun | 61.0 Hz | 0.5 |
| `test_spin_argument_refuses` | a non-zero chi1z raises NotImplementedError | — | strict |

**If the flatness test fails, it may not be our error.** A smooth but non-flat
ratio means LAL generated the array with post-Newtonian amplitude corrections
rather than the 0PN amplitude. If that is what you find: say which convention we
use, record it in `choices` with the reason, and write the observation into
`NOTES.md`. Do not tune anything to close the gap. The test exists to discover
that fact, not to assume it away.

**The two SNRs are both right.** Our inspiral recovers 11.36 where IMRPhenomD
recovers 19.81, because GW150914 has a total mass of 72.15 Msun and therefore
f_ISCO near 61 Hz: this system's inspiral ends at the bottom of the sensitive
band and most of its SNR is in the merger. That is the honest scope of an
inspiral-only waveform, and it has a consequence the final page has to carry:
**a campaign built on inspiral-only waveforms underestimates the detectability of
heavy systems.** Record it as a claim with its alternative stated.

## Provenance

Numbers: `amplitude_ratio_vs_lal`, `match_vs_lal`, `snr_taylorf2_real_data`,
`f_isco_gw150914`, `amplitude_mchirp_exponent`.

Claims: `waveform_agrees_with_lal`, and `inspiral_only_is_a_floor` — the second
being the scope statement above, with its alternative written out (use the
shipped IMR waveform, which exists for exactly one set of masses and so cannot
sweep a population).

Figure: `figures/f02_waveform_vs_lal.png`.

`choices` must include: the PN order of the phase, the 0PN amplitude, where the
waveform is cut off, the bands used for the amplitude comparison and for the
match, and the source the PN coefficients were transcribed from.

## Constraints

- Use `.venv/Scripts/python.exe`. Never `python3`.
- Add no dependencies.
- Everything on the one frequency grid.
- `match()` reuses `filtering.matched_filter`.

## Do not

- Do not touch day 1's modules, or `horizon.py` and `antenna.py`.
- Do not implement spin. Today it raises.
- Do not adjust a tolerance or a target. See `CLAUDE.md`.

## When you are done

`pytest -q` green across the whole suite, the figure on disk with its record in
`provenance/claims.yaml`, `results.json` updated, and a report saying what each
comparison came out at — especially the amplitude ratio, whether it was flat, and
what that told you about LAL's convention.
