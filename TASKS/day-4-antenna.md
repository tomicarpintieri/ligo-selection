# Day 4 — Which directions a detector is deaf to

## Objective

Build the antenna pattern, and compute the first number in this project that
appears nowhere in the course material.

This is where the new work starts. Day 2 of the course states its own boundary
on a slide of its own: *"No antenna patterns. No sky localisation. We do not do
a coherent multi-detector search — for simplicity. Every number today is computed
from a single interferometer."* Everything in this file is outside that boundary.

## The physics, before you write anything

An L-shaped detector measures the difference in length between two perpendicular
arms. A wave arriving in the right orientation stretches one arm and squeezes
the other: maximum signal. Arriving rotated by 45 degrees it stretches both
equally, the difference is zero, and the detector sees **nothing at all**, no
matter how strong the wave is. There are four such directions and they are
geometry, not a defect. Every L has them.

A wave also has two independent polarisations, rotated 45 degrees from each
other, and the detector responds differently to each. The two functions
describing that are F_plus and F_cross, and they are the whole object of today.

Why it matters here: an identical merger at an identical distance is detected or
not depending on where it came from and how it is tilted. The entire selection
bias this project measures starts at this function.

## Context — read these first

- `src/gwsel/antenna.py`, whose docstrings carry every target below, including
  five Monte Carlo values that were measured on this machine before any of this
  code was written.
- `horizon.py` from day 3, which computed the *best case*. Today is the factor
  between that and the average.

## Build

**1. `src/gwsel/antenna.py`** — `response(theta, phi, psi)` and
`projection_factor(f_plus, f_cross, inclination)`.

Detector frame only. No Earth, no time, no real detectors: those are day 5.
Theta from the zenith, meaning the normal to the plane of the arms; phi from the
x arm; psi the polarisation angle. All radians, all broadcasting over arrays,
because the Monte Carlo below runs at N of several million.

**2. `scripts/s04_antenna.py`**, **3. `figures.f04_antenna_pattern()`**,
**4. `tests/test_04_antenna.py`**.

The figure: a Mollweide map of the total response over the sky in the detector
frame, with the four null directions marked. No healpy — it has no Windows build.
Use matplotlib's Mollweide projection on a regular grid.

## Acceptance

Use N = 4,000,000 with a fixed seed of 0 for the Monte Carlo tests, and mark them
`slow`. The measured values in the last column are what this machine gave before
any of this was written — they are the evidence that the targets are reachable,
not the targets themselves.

| test | quantity | target | tolerance | measured |
|---|---|---|---|---|
| `test_overhead_is_unity` | F_plus at theta 0, phi 0, psi 0 | 1.0 | 1e-12 | exact |
| `test_overhead_cross_is_zero` | F_cross at the same point | 0.0 | 1e-12 | exact |
| `test_four_blind_directions` | both responses at theta pi/2, phi pi/4 plus multiples of pi/2, for every psi | 0.0 | 1e-12 | exact |
| `test_mean_fplus_squared` | sky and polarisation average of F_plus squared | 0.2 | 0.001 | 0.19997 |
| `test_mean_fcross_squared` | the same for F_cross | 0.2 | 0.001 | 0.19987 |
| `test_fplus_fcross_uncorrelated` | average of their product | 0.0 | 0.001 | -3.6e-05 |
| `test_rms_projection_factor` | root mean square of w over sky, polarisation and inclination | 0.4 | 0.002 | 0.39996 |
| `test_range_factor_2_26` | horizon over range: the cube root of the mean of w cubed, inverted | 2.2649 | 0.01 | 2.2649 |
| `test_bad_sky_sampler_fails` | a sampler uniform in theta must NOT give 0.2 | — | strict | — |

**The sky average is the sharp test.** One fifth is exact and analytic, so a
Monte Carlo reproducing it without being told to is strong evidence the sampling
and the formula are both right. There is one classic way to get it wrong: sample
theta uniformly instead of sampling its cosine uniformly. That produces a smooth,
plausible, wrong answer with no symptom. `test_bad_sky_sampler_fails` deliberately
builds the wrong sampler and asserts the check catches it — without it, a correct
0.2 proves nothing, because you have not shown the test can fail.

**The 2.26 is the point of the day.** It is the ratio between the horizon
distance — best case, which is all day 3 computed — and the range, the distance
that gives the same sensitive *volume* once you average over where sources
actually are and how they are actually tilted. Day 2 of the course mentions "the
averaged range is 2.26x smaller" in a presenter note and never computes it.
Today it is computed, and it is the first result in this repository that is not
a reproduction of something the course already did.

Note the two different averages and record why each is used: the root mean square
of w, which is 0.4, is the amplitude average; the cube-root average, which gives
2.2649, is the volume-equivalent one, and it is the one that matters for counting
sources because the number of sources grows with volume.

## Provenance

Numbers: `sky_mean_fplus_squared`, `sky_mean_fcross_squared`,
`rms_projection_factor`, `horizon_over_range_factor`.

Claims: `detector_has_blind_spots` — with the four directions, and the fact that
they are exact zeros and not small numbers — and `range_is_2p26_below_horizon`,
which states what day 3's horizon really means once orientation is accounted for.

Figure: `figures/f04_antenna_pattern.png`.

`choices`: N and the seed; the convention for theta, phi and psi, stated
explicitly because there are several in the literature and they are not
interchangeable; and sampling the cosine of theta rather than theta, with the
reason.

## Constraints

- Use `.venv/Scripts/python.exe`. Never `python3`.
- Add no dependencies. No healpy: it has no Windows build.
- Vectorise. A Python loop over four million samples will not finish in a
  reasonable time and there is no reason to write one.

## Do not

- Do not put any real detector coordinates, sidereal time or Earth rotation in
  this file today. That is day 5, and mixing them makes the detector-frame tests
  impossible to interpret.
- Do not touch earlier modules.
- Do not adjust a tolerance or a target. See `CLAUDE.md`.

## When you are done

`pytest -q` green across the whole suite, the figure with its record,
`results.json` updated, and a report that says what the four averages came out
at and how far the 2.26 landed from the published value.
