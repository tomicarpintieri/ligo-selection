# Open questions, discrepancies, and platform quirks

Things that are known, unresolved, or surprising. Nothing in here is hidden from
the page: an open discrepancy is a result too, and it is cheaper to write it down
when it appears than to rediscover it in week 4.

Add to the bottom. Do not delete an entry; mark it resolved and say how.

---

## OPEN — GW150914 distance upper bound: 795.5 Mpc here, 786 Mpc on the slide

Day 2 of the course states that the observed SNR bounds GW150914's distance from
above at **786 Mpc** (the published luminosity distance is 440 Mpc). From our own
reproduction the same identity gives

    D_max = 400 Mpc x sigma / rho_obs = 400 x 39.3971 / 19.8104 = 795.5 Mpc

a 1.2 % difference. Our number is internally consistent — it is our sigma and our
peak SNR — so the discrepancy is in an input, most likely a slightly different
PSD estimate or SNR value behind the slide. Not chased in week 1. The test asserts
our own identity, not the slide's number.

*Status: open. Recorded 2026-09-11, before any code was written.*

---

## OPEN — TaylorF2 recovers 11.36; the day 2 lecture says about 16

Day 2's reproduction measured a peak SNR of **11.358** for LAL's TaylorF2
waveform against real H1 data, where the lecture quotes roughly 16. The 11.358 is
what the shipped array actually gives through our filter, and it is the target
`tests/test_02_waveform.py` uses, because it is the number we can reproduce.

Note this is separate from the *expected* gap between TaylorF2 (11.36) and
IMRPhenomD (19.81): that one is understood and is not a discrepancy. GW150914 has
a total mass of 72.15 Msun, so f_ISCO is about **61 Hz** — the inspiral of this
system ends near the bottom of the sensitive band and most of its SNR is in the
merger, which an inspiral-only waveform does not have.

**Consequence for this project, which has to be stated on the page:** a campaign
run with inspiral-only waveforms *underestimates* the detectability of heavy
systems. That is a choice with a defensible alternative and it belongs in
`claims.yaml`.

*Status: open (the 16). Understood (the 11.36 vs 19.81). Recorded 2026-09-11.*

---

## RESOLVED — the provenance hook needed two Windows fixes

The scaffold comes from `day5/exercise/b/.claude/` in the course tree. Two things
stopped it working here, both fixed and both marked in the file:

1. `settings.json` invoked `python3`, which on Windows resolves to the Microsoft
   Store stub. It now points at `.venv/Scripts/python.exe`.
   `tests/test_00_scaffold.py::test_hook_is_wired_to_an_interpreter_that_exists`
   keeps it that way.
2. `figures_in_tree()` filtered paths with `"/.claude/" in p`, which never matched
   because `glob` returns backslashes here, and it walked the entire tree —
   including `.venv/`, thirty thousand files of site-packages, on every `Stop`.
   Rewritten with `os.walk` and an explicit skip list.

Verified 2026-09-11: exits 0 when nothing was produced, exits 2 with the format
spec when a figure appears with no record, exits 0 once
`src/gwsel/provenance.py` has written the records.

*Status: resolved.*

---

## KNOWN — no lalsuite, no healpy on this machine

Neither publishes a Windows build; this was established the hard way during the
course (`pip install lalsuite` returns "from versions: none"; healpy has no
`win_amd64` wheel). Nothing in this project needs either:

- waveforms come from `data/imr_gw150914.npz` plus our own `src/gwsel/waveform.py`
- sky maps use matplotlib's Mollweide projection on a regular grid

If a stage finds itself wanting one of them, that is a design problem, not a
packaging problem. Say so and stop.

*Status: known constraint, worked around by design.*

---

## OPEN — Day 1 whitened variance does not yet reproduce the reference

The matched-filter control now reproduces H1 SNR 19.81039, L1 SNR 13.54323,
H1 sigma 39.39713, GPS 1126259462.42334, the −7.08008 ms delay, and the
gwpy PSD comparison (0.0009599%).  However, the current Tukey-windowed
one-sided whitening implementation measures **0.44199** on the first clean
32 s of H1, where the day-1 acceptance value is **0.9650 ± 0.02**.

The tolerance and target have not been changed. The normalization/convention
needs to be reconciled before Day 1 can be called complete.

*Status: open. Recorded 2026-09-28.*

**Resolution (2026-09-28):** `filtering.whiten()` now restores the one-sided
PSD convention and Tukey taper energy with `sqrt(2 / mean(taper**2))`. The
regenerated variance is **0.95891**, within the unchanged 0.9650 +/- 0.02
acceptance interval.

*Status: resolved. The original observation above remains as the record of the
failed normalization.*

---

## RESOLVED — `f_cut="isco"` disabled the cutoff it was named after

`spa_inspiral`'s docstring said *"Outside [f_low, f_cut] the output is zero"*,
and its default value `"isco"` was implemented as `np.inf`. Every waveform the
project generated therefore ran to Nyquist, tens of times past the frequency
where the inspiral description stops being true.

Measured cost, sigma with no cutoff over sigma cut at f_ISCO:

| total mass | f_ISCO | inflation in sigma | in Euclidean volume |
|---|---|---|---|
| 20 Msun | 220 Hz | 1.06x | 1.2x |
| 40 Msun | 110 Hz | 1.27x | 2.1x |
| 72 Msun | 61 Hz | **1.83x** | **6.1x** |
| 120 Msun | 37 Hz | **4.02x** | **65x** |

The inflation grows with mass, which is the axis this project exists to
measure, so this was not a small systematic — it pointed straight at the
headline result.

**Fix (2026-09-30):** `f_cut="isco"` now cuts at `f_isco(m1 + m2)`, and
`f_cut=None` is the explicit way to ask for no cutoff. LAL's shipped TaylorF2
reference runs to Nyquist, so `scripts/s02_waveform.py` now passes `None`
deliberately — it is the only place in the project that wants it. The four
numbers that compare against LAL are unchanged: amplitude ratio 1.000, match
1.000, SNR 11.3578, f_ISCO 60.93 Hz.

*Status: resolved.*

---

## RESOLVED — the horizon curve was computed with two different physics in it

`horizon_curve` read its cutoff with `waveform_kwargs.pop("f_cut", None)`
**inside** its own loop. `pop` consumes the key, so mass 1 of 80 received the
ISCO cutoff and masses 2 through 80 received `None`.

| chirp mass | published curve | correct | error |
|---|---|---|---|
| 1.50 | 189.3 Mpc | 189.3 Mpc | — (the one point that got the cutoff) |
| 10.95 | 992.7 Mpc | 903.4 Mpc | 1.1x |
| 29.60 | 2272.9 Mpc | 1315.9 Mpc | 1.7x |
| 80.00 | 5204.5 Mpc | 358.9 Mpc | **14.5x** |

Worse than the numbers: the correct curve **turns over**. Heavier means louder
until heavier means the merger falls out of the band. The published curve rose
monotonically forever, which is the physical content of the figure inverted.

**Fix (2026-09-30):** the `pop` moved out of the loop, and
`tests/test_03_horizon.py::test_horizon_turns_over` now recomputes a coarse
curve and asserts an interior maximum. It recomputes rather than reading the
recorded peak on purpose: reading it back would only confirm the script agrees
with itself. The regenerated curve peaks at **Mc = 27.8 Msun / 1329 Mpc**.

That test was specified in `TASKS/day-3-horizon.md` and had been dropped. It
would have caught this on the day it was written.

*Status: resolved.*

---

## FINDING — the day-3 brief's 5/6 fit window is too wide, and by how much

Once the ISCO cutoff actually cuts, `test_horizon_exponent_5_6` fails over the
window the brief names: **0.8219**, where the same brief asks for 5/6 within
±0.01, i.e. ≥ 0.8233.

**The tolerance was not touched.** The window was wrong, and it can be shown:

`TASKS/day-3-horizon.md` justifies [1.5, 5] Msun with *"there f_isco sits above
~380 Hz, i.e. above the sensitive band, so the waveform fills the band and the
exponent holds"*. That does not hold at the top of its own window. At Mc = 5,
f_ISCO is 383 Hz and the analysis band runs to **1024 Hz** — so the cutoff is
inside the band, not above it. The band is not fixed there, and the 5/6 law
requires a fixed band.

**What replaced it.** `scripts/s03_horizon.py` fixes the acceptable bias first,
as a fraction of SNR — `BAND_FIXED_TOLERANCE = 0.999`, meaning the ISCO cut may
cost at most 0.1 % of sigma — and derives the window from it by bisection. That
gives Mc ≤ **2.385**, where the exponent measures **0.8314**, inside ±0.01 with
80 % of the tolerance to spare. Both the criterion and the resulting window are
in `results.json` and in the provenance `choices`, and
`test_fit_window_is_derived_not_chosen` pins both ends of the bisection so the
window cannot be quietly widened later.

The wide-window value stays measured and recorded as
`horizon_mchirp_exponent_brief_window`, with
`test_brief_window_is_recorded_as_too_wide` asserting it is still outside
tolerance — so if anyone restores the old window, the failure explains itself.

*Status: resolved, and kept as a finding. Recorded 2026-09-30.*
