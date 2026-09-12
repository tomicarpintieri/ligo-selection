# Day 3 — How far it reaches, and how much universe that is

## Objective

Turn a detection threshold into a distance, and a distance into a volume.

SNR falls as one over distance, so "detected if SNR above 8" *is* "closer than
D". A distance cubed is a volume. That chain is where selection effects come
from: loud sources are visible from further away, so a catalogue
over-represents them relative to the universe. By the end of today you can say
by how much, along the mass axis, with a curve.

## Context — read these first

- `src/gwsel/horizon.py`, whose docstrings state every target below.
- The day 2 slide this reproduces: SNR goes as one over distance, so a detection
  threshold is a distance and a distance cubed is a volume; measured with the
  real H1 PSD for a GW150914-like binary at threshold 8, that is 1.9 Gpc and a
  searched volume of 30 Gpc cubed.
- `NOTES.md`, the open entry on 786 against 795.5 Mpc. It is today's, and it
  stays open.
- `waveform.spa_inspiral` from day 2 sweeps the mass axis. The shipped
  IMRPhenomD waveform pins the GW150914 point.

## Build

**1. `src/gwsel/horizon.py`** — `sigma`, `horizon_distance`,
`sensitive_volume_euclidean`, `horizon_curve`.

Everything is Euclidean: no redshift, no expansion. That is fine out to the
2 Gpc Advanced LIGO reaches and wrong for week 4's third-generation detectors,
and the figure has to say so on its face.

**2. `scripts/s03_horizon.py`**, **3. `figures.f03_horizon_vs_mchirp()`**,
**4. `tests/test_03_horizon.py`**.

The figure: horizon distance against chirp mass on log axes, the 5/6 reference
power law drawn on it, the turnover visible, GW150914 marked, and a note on the
face that the volume is Euclidean.

## Acceptance

| test | quantity | target | tolerance |
|---|---|---|---|
| `test_sigma_imr` | optimal SNR of IMRPhenomD against the H1 PSD | 39.3971 | 0.01 |
| `test_horizon_gw150914` | 400 Mpc times 39.3971 divided by 8 | 1969.9 Mpc | 5 Mpc |
| `test_horizon_in_slide_range` | the same, in Gpc | 1.90 to 2.00 | the slide says 1.9 |
| `test_volume_gpc3` | four thirds pi D cubed at that horizon | 32.0 Gpc3 | 1.0 |
| `test_volume_threshold_slope` | d log V over d log threshold | -3.000 | 0.01 |
| `test_horizon_exponent_5_6` | power-law fit of the curve, chirp mass 1.5 to 5 Msun | 0.83333 | 0.01 |
| `test_horizon_turns_over` | the curve has an interior maximum | — | strict |
| `test_distance_bound_identity` | 400 Mpc times sigma over observed SNR | 795.5 Mpc | 1 Mpc |

**The 1.5 to 5 Msun window is not arbitrary and must be recorded as a choice.**
The 5/6 exponent is exact only while the *band* is fixed. Below chirp mass
5 Msun, f_ISCO sits above roughly 380 Hz, which is above the sensitive band, so
the waveform fills the band and the exponent holds. Above it the waveform starts
ending inside the band, the effective band shrinks with mass, and the exponent
drifts. Verify that condition numerically with `waveform.f_isco` rather than
taking it on trust from this brief.

`test_horizon_turns_over` is the physical content of the figure: the curve rises
because heavier means louder, then falls because heavier means the merger drops
out of the band. Both effects, one picture.

**The open discrepancy.** The slide says 786 Mpc for GW150914's distance upper
bound; our own sigma and SNR give 795.5. Assert *our* identity. Leave the entry
in `NOTES.md` open and state the 1.2 percent difference. Do not chase it today
and do not adjust anything to make it agree.

## Provenance

Numbers: `sigma_imr_h1`, `horizon_gw150914_mpc`, `sensitive_volume_gpc3`,
`horizon_mchirp_exponent`, `distance_upper_bound_mpc`.

Claims: `threshold_is_a_distance`, and `selection_tilts_towards_heavy` — the
exponent, and what a tilt of that size does to an observed mass distribution.

Figure: `figures/f03_horizon_vs_mchirp.png`.

`choices` must include: threshold 8 rather than the 9 that Roulet and
Zaldarriaga use; Euclidean volume; the fit window and the reason for it; which
PSD, off-source H1; and optimal orientation, which is what makes today's number
a *horizon* rather than a *range*. Day 4 is where that gets fixed.

## Constraints

- Use `.venv/Scripts/python.exe`. Never `python3`.
- Add no dependencies. Everything on the one frequency grid.

## Do not

- Do not touch `antenna.py`, and do not apply any orientation averaging today.
  Today's number is deliberately the best case, so that tomorrow's factor of
  2.26 has something to be a factor *of*.
- Do not touch day 1 or day 2 modules.
- Do not adjust a tolerance or a target. See `CLAUDE.md`.

## When you are done

`pytest -q` green across the whole suite, the figure with its record,
`results.json` updated, and a report that states the 786 against 795.5 gap
plainly rather than smoothing it over.
