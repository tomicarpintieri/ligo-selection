# Day 6 — The page, and handing the repository to a stranger

## Objective

Turn five days of results into something a person can read, and then find out
whether a machine that has never spoken to us can rebuild it.

## Context — read these first

- `README.md` and `CLAUDE.md`.
- `results.json`, `provenance/numbers.json`, `provenance/claims.yaml` — everything
  on the page comes from these three files and from nowhere else.
- `NOTES.md`. The open discrepancies go on the page. They are results too.

## Build

**1. `page/template.html`** — the page, in **Spanish**, with every number written
as a placeholder token of the form `__SLUG__`. Sections in this order:

1. What the question is, and why it is not a repeat of the course.
2. **The control.** GW150914 found by our own pipeline, with the SNRs. This comes
   first on purpose: before showing a reader anything new, show them the code
   finding something they already believe.
3. The waveform against LAL, and the honest scope note about inspiral-only.
4. The horizon and the volume, with the mass tilt.
5. The antenna pattern, the blind spots, and the factor of 2.26.
6. The network, and the 24-hour sweep.
7. **What we have not done.** The open items in `NOTES.md`, the Euclidean volume,
   the ring that is not a localisation, and what week 2 is for.
8. The table of every check, with what it targeted and what it gave.

Each figure gets two short paragraphs under it: where it came from, and how it was
checked. That is the assignment's actual requirement and it is the part that
normally gets skipped.

**2. `scripts/make_page.py`** — substitute the tokens from `results.json` and
write `page/index.html`. Follow the pattern from
`day2/repro-gw150914/build_report.py` in the course tree: a substitution dict,
figures inlined as base64 data URIs so the page is a single file, and an
assertion at the end that **no token survived**.

**3. `run_all.py`** — fetch, then every stage script in order, then the page, then
pytest. One command that rebuilds the repository from nothing.

**4. `tests/test_06_page.py`**.

## Acceptance

| test | what it verifies |
|---|---|
| `test_no_placeholder_survives` | no `__TOKEN__` is left in the built `index.html` |
| `test_every_page_number_is_recorded` | every substituted token maps to a slug in `provenance/numbers.json` |
| `test_every_figure_has_provenance` | every file in `figures/` has an entry under `figures:` in `claims.yaml` |
| `test_every_claim_resolves` | every slug listed under a claim's `numbers:` exists in `numbers.json` |
| `test_every_figure_has_a_producer` | every figure entry names a function that exists in `src/gwsel/figures.py` |
| `test_run_all_is_complete` | every stage script in `scripts/` is called by `run_all.py` |

`test_every_page_number_is_recorded` is the one that matters. It is what makes it
structurally impossible for a number to appear on the page without a traceable
origin — not a policy anybody has to remember, a test that fails.

## The stranger test

This is the assignment's own test of the repository, and it is the real work of
the day.

1. Open a **fresh** agent session in an **empty** directory. No context, no
   history, nothing from this conversation.
2. Clone the repository from GitHub.
3. Say only: **"reproduce figure 3"**. Explain nothing else.
4. Watch. Write down every point where it got stuck or had to guess.

It will fail at something. It always does: a dependency that is installed here
and not pinned, a path typed absolutely, a step that lives in somebody's head. The
list of those failures is the day's deliverable.

5. Fix each one — usually in `README.md`, sometimes in the code.
6. Run the stranger test again, from a clean clone, until it gets there unaided.

Record the outcome in `NOTES.md`: how many attempts, what broke each time, and
what the fix was. That record is worth putting on the page.

## Provenance

Figures: any new ones.

Claim: `repository_reproduces_unaided` — stating what was actually achieved, with
the number of attempts and what had to be fixed as evidence. If it never fully
succeeded, say that instead, plainly. An honest negative is a result; a claim
that overstates what happened is the one thing that cannot be repaired later.

## Constraints

- Use `.venv/Scripts/python.exe`. Never `python3`.
- The page is a single self-contained HTML file: figures inlined, no external
  assets, no CDN. It has to work from a file:// URL and from a static host.
- Every number on the page comes from `results.json`. None is typed by hand.
- Page text in Spanish; code, comments and provenance stay in English.

## Do not

- Do not hard-code a number into the template to make a sentence read well.
- Do not leave a figure out of `claims.yaml` because it is "only illustrative".
- Do not describe the stranger test as having gone better than it did.

## When you are done

`python run_all.py` rebuilds everything from a clean clone, `pytest -q` is green,
`page/index.html` opens as one file, and `NOTES.md` records how the stranger test
actually went.
