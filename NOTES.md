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
