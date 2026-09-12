# House rules

Read `README.md` first, then the brief in `TASKS/` for the stage you were asked
to do. Do that stage and stop.

## The rule that is not negotiable

If a check does not pass, **DO NOT** widen the tolerance, change the target
value, mark the test `xfail`, or delete it. Stop, write what you got and what was
expected into `NOTES.md`, and report it as a blocker.

A tolerance loosened to make a test pass is the single failure mode that destroys
this project, because every number downstream inherits it silently and nothing
ever fails again.

The same applies to a target you think is wrong. It may well be — one is already
recorded as an open discrepancy in `NOTES.md`. Write it down there; do not edit
it away.

## Provenance is part of the work, not the write-up

Every number you report and every figure you leave needs a record, written as you
go. Use `src/gwsel/provenance.py`:

```python
from gwsel import provenance as pv
pv.record_number(slug, value, statement, produced_by, from_scratch, from_library, choices)
pv.record_claim(claim_id, statement, evidence, numbers)
pv.record_figure(file, produced_by, shows, from_scratch, from_library, choices, supports)
```

The format is stated once, in `.claude/provenance/*.md`. Read those before
writing each kind of record. `produced_by` is `<file>::<function>` and must name
the function that *computed* the value, not the script that printed it.

`choices` is the field people skip. It is every decision that had a defensible
alternative — a band edge, a segment length, an estimator, a PN order, a cutoff.
`[]` is allowed only when there genuinely was nothing to decide, and it is
written explicitly.

A `Stop` hook checks all of this and will not let a turn end without it.

## Working in this repository

- **Use the project venv.** `.venv/Scripts/python.exe`. Not `python`, not
  `python3` — on this machine `python3` is a Microsoft Store stub that does
  nothing.
- **Do not add dependencies.** `requirements.txt` is pinned and a test asserts
  the installed versions match it. If you are convinced something is genuinely
  needed, say so and stop; do not install it.
- **One frequency grid.** 32 s at 4096 Hz, the `grid` fixture in
  `tests/conftest.py`. Every waveform, PSD and filter output lives on it. Mixing
  grids is the quiet way to produce a wrong SNR that looks entirely normal.
- **Numbers go in `results.json`**, written by the stage script, and nowhere
  else. The page is built from that file; a number typed into HTML by hand is a
  number nobody can trace.
- **Figures go through `figures.save()`**, which returns the path in the exact
  form `provenance.record_figure()` wants.
- **Stay in your stage.** Do not edit another stage's module, script or tests. If
  something there is wrong, write it in `NOTES.md` and say so.

## What "done" means for a stage

1. the named tests pass, with the tolerances as written
2. the named figures exist
3. every number and figure has a provenance record
4. `pytest -q` is green across the whole suite, not just your file
5. anything surprising is in `NOTES.md`

Report what you measured, including anything that did not match. A stage that
reports an honest failure is worth more here than one that reports success.
