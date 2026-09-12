# Day 5 — Real detectors, and the Earth turning underneath the sky

## Objective

Bolt the antenna pattern to two real instruments, let the Earth rotate, and
produce the figure the whole week has been heading for.

## The physics, before you write anything

Yesterday the detector floated in space. Today Hanford is in Washington state and
Livingston is in Louisiana, each with its arms pointing along a published azimuth.

And the Earth turns. The sensitivity map is glued to the detector, so it **sweeps
across the sky** once every sidereal day. A source that sat in a blind spot at
three in the morning is perfectly audible by nine. Which means the detectability
of a source depends on what time of day it happened — a fact nobody says out loud
and which your animation will make obvious.

Two detectors also cover each other's holes, because they are oriented
differently. That is half the reason there is more than one. The other half is
that the difference in arrival time between them tells you where the source was.

## Context — read these first

- `src/gwsel/antenna.py`, the day 5 section, whose docstrings carry the targets.
- Day 1's measured arrival-time difference: L1 received GW150914 7.08 ms before
  H1. That is in `results.json`.
- `astropy` is installed and is a **test-only** dependency here. Write
  `gmst_from_gps` yourself and check it against `astropy.time`. Every test that
  touches astropy must skip cleanly when it is absent.

## Build

**1. `src/gwsel/antenna.py`, day 5 section** — a `Detector` record holding
latitude, longitude, elevation and the two arm azimuths; a `DETECTORS` mapping
with `H1` and `L1`; `gmst_from_gps`; `response_earth`; `time_delay`.

The H1 and L1 coordinates must be transcribed from a citable published source,
and the citation goes in the claim's `evidence`. Do not take them from memory and
do not take them from this brief — this brief does not contain them on purpose.
The light-travel-time test below is what tells you whether you transcribed them
correctly.

**2. `scripts/s05_network.py`**, **3. two figure functions**,
**4. `tests/test_05_network.py`**.

## Acceptance

| test | quantity | target | tolerance |
|---|---|---|---|
| `test_h1_l1_light_travel_time` | site separation divided by c | 10.002 ms | 0.05 ms |
| `test_gmst_period` | GMST advance over one sidereal day, 86164.0905 s | 2 pi | 1e-6 rad |
| `test_gmst_vs_astropy` | our sidereal time against astropy's | agreement | 1e-4 rad, skip if absent |
| `test_sky_average_invariant` | sky average of F_plus squared, at several GPS times | 0.2 | 0.001 |
| `test_time_delay_bounded` | absolute delay over 100,000 random sky directions | at most 10.002 ms | strict |
| `test_gw150914_delay_ring_nonempty` | sky directions giving a delay of -7.08 ms | non-empty | strict |
| `test_network_beats_single` | sky-averaged total response, network against one detector | at least as large | strict |

**The light travel time is the test that validates the whole geometry.** It is a
single published number that depends on both sites' coordinates and on nothing
else. If it comes out at 9 or at 12, the coordinates or the coordinate conversion
are wrong, and you know that before looking at anything that matters.

**The sky-average invariance is nearly free and catches a lot.** A rotation
cannot change an average taken over all directions, so one fifth must survive
being evaluated at any GPS time. If it does not, the conversion from celestial to
detector coordinates has a bug in it.

**`test_gw150914_delay_ring_nonempty` is a consistency check, not a precision
one, and the page must say so in those words.** A 7.08 ms delay between two
detectors picks out a ring on the sky, not a point. The published localisation of
GW150914 is a banana-shaped region of roughly 600 square degrees. All our
geometry can honestly claim is that the ring exists and is consistent. Claiming
more than that would be the kind of overreach this project is supposed to be
better than.

## Figures

`figures/f05_network_skymap.png` — H1, L1 and the combined network in celestial
coordinates, at GW150914's GPS time, with the event's published sky region
overlaid.

`figures/f06_rotation.gif` — 24 hours of the network response sweeping the sky.
Use matplotlib's **pillow** writer. There is no ffmpeg on this machine, so no mp4.

`figures/f06_rotation_panels.png` — four frames from that animation as a static
figure. The PDF cannot show a GIF, and the page should not depend on one.

## Provenance

Numbers: `h1_l1_light_travel_ms`, `gmst_vs_astropy_rad`,
`network_sky_average_gain`.

Claims: `network_covers_the_blind_spots`; `detectability_depends_on_time_of_day`,
which is the animation's content stated as an assertion; and
`gw150914_timing_is_consistent`, worded to claim only consistency.

Figures: all three.

`choices`: the source the detector coordinates were transcribed from; the
convention for the arm azimuths; how the network response is combined, which has
more than one defensible definition — state which and why; and the number of
frames in the animation.

## Constraints

- Use `.venv/Scripts/python.exe`. Never `python3`.
- Add no dependencies. astropy is already pinned and is test-only: no module
  under `src/gwsel/` may import it.
- No healpy.

## Do not

- Do not change yesterday's detector-frame functions. Today extends; it does not
  edit.
- Do not claim a sky localisation. The ring is a ring.
- Do not adjust a tolerance or a target. See `CLAUDE.md`.

## When you are done

`pytest -q` green across the whole suite, three figures with their records,
`results.json` updated, and a report that says what the light travel time came
out at and how close the hand-written sidereal time landed to astropy's.
