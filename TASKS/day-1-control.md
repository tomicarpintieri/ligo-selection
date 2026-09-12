# Day 1 — The control

## Objective

Make this repository find GW150914 on its own, and prove it with tests.

Nothing in this project means anything until the machinery is known to work on a
signal somebody else already measured. That is what today is: a control. By the
end, `pytest tests/test_01_control.py` reproduces nine numbers that were measured
independently, and everything later stands on it.

## Context — read these first

- `README.md` and `CLAUDE.md` in this repository. `CLAUDE.md` has one rule in it
  that matters more than the rest.
- `src/gwsel/constants.py`, `dataio.py`, `figures.py`, `provenance.py` are already
  written and tested. Use them; do not reimplement them.
- `tests/conftest.py` — the fixtures you are handed: `h1`, `l1`, `waveforms`,
  `reference_psd`, `grid`, `psd_h1`, `psd_l1`. The last two call the functions you
  are about to write.
- `tests/test_00_scaffold.py` passes now and must keep passing.

**Where the code comes from.** We wrote the original on 2026-08-31, and it is at
`C:\Users\tomic\GW-AI-course\day2\repro-gw150914\reproduce.py`. It is a *script*:
it computes on import and reaches for module-level globals (`FREQS`, `BAND`,
`NSEG`, `DF`, `GUARD`). Lift the functions into the skeletons here and give them
explicit arguments. **Do not copy the script.** The provenance record has to say
what came from there and what changed in the lifting.

## Build

**1. `src/gwsel/psd.py`** — `welch_median`, `psd_on_grid`. The docstrings state
the contract, including the median bias correction (the alternating harmonic sum)
which is the part that is easy to leave out and which moves the answer by ~40 %.

**2. `src/gwsel/filtering.py`** — `whiten`, `segment`, `matched_filter`, `peak`,
`template_peak_time`, `search`. Ten lines of this carry the physics; the rest is
bookkeeping about which grid you are on.

**3. `scripts/s01_control.py`** — runs the control and writes every number below
into `results.json` (merge into it, do not overwrite the file), records the
provenance, and draws the figure. Runnable as
`.venv/Scripts/python.exe scripts/s01_control.py`.

**4. `figures.f01_snr_timeseries()`** — add it to `src/gwsel/figures.py`. Filter
output against time in H1 and L1, peaks marked, the 7.08 ms offset annotated.
Save with `figures.save(fig, "f01_snr_timeseries.png")`.

**5. `tests/test_01_control.py`** — the acceptance table below, one test each,
reading from `results.json` where the number is expensive to recompute.

## Acceptance

Every target was measured independently before this repository existed.

| test | quantity | target | tolerance |
|---|---|---|---|
| `test_h1_peak_snr` | peak SNR, IMRPhenomD vs real H1 | 19.8104 | ±0.01 |
| `test_l1_peak_snr` | peak SNR, IMRPhenomD vs real L1 | 13.5432 | ±0.01 |
| `test_h1_sigma` | sqrt(<h\|h>) of IMRPhenomD vs the H1 PSD | 39.3971 | ±0.01 |
| `test_gps_peak` | GPS time at the H1 peak | 1126259462.4233 | ±0.01 s |
| `test_time_delay_l1_minus_h1_ms` | L1 arrival minus H1 arrival | −7.080 ms | ±0.2 ms |
| `test_welch_vs_gwpy_pct` | median rel. difference, our Welch vs gwpy's, 20–1024 Hz | 0.00096 % | < 0.01 % |
| `test_whitened_variance` | variance of whitened clean H1, cut at 20 Hz | 0.9650 | ±0.02 |
| `test_background_mean_rho2` | mean of rho² on independent off-source samples | 2.0176 | within 3 sem of 2.0, sem ≈ 0.0371 |
| `test_no_signal_in_background` | loudest off-source rho stays below the Gaussian expectation for that many samples | 6.316 vs 5.708 | report both |

The background test loops a matched filter over ~121 windows and takes a minute
or two. Mark it `@pytest.mark.slow`.

`test_background_mean_rho2` is the one worth understanding before writing it:
rho² for pure Gaussian noise is chi-squared with two degrees of freedom, so its
mean is 2 — with no fit and no free parameter. Measuring 2.018 on real data says
the noise is behaving and the filter normalisation is right, in one number.

The last row is not a pass/fail against a target: report both numbers and say
which is larger. It is the honest statement of how loud the loudest thing in the
off-source data was.

## Provenance

Numbers: `h1_peak_snr`, `l1_peak_snr`, `h1_sigma`, `time_delay_ms`,
`welch_vs_gwpy_pct`, `background_mean_rho2`.

At least one claim, `control_gw150914`, saying in a sentence that this repository
independently reproduces the published detection, with the tests as evidence.

One figure entry for `figures/f01_snr_timeseries.png`.

`choices` must include, at minimum: the 4 s Welch segment length, the median
rather than the mean, estimating the H1 PSD off-source from the first 512 s,
the 20–1024 Hz band, and the Tukey window with alpha 0.125.

## Constraints

- Use `.venv/Scripts/python.exe`. Never `python3`.
- Add no dependencies. `tests/test_00_scaffold.py` asserts the installed versions
  match `requirements.txt`.
- Everything on the `grid` fixture's frequency axis.
- Numbers go into `results.json`, written by the script. Not typed anywhere else.

## Do not

- Do not touch `waveform.py`, `horizon.py` or `antenna.py`. They are later stages.
- Do not widen a tolerance or change a target. See `CLAUDE.md`.
- Do not "fix" `NOTES.md`'s open discrepancies. They are not today's work.

## When you are done

`pytest -q` green across the whole suite, `figures/f01_snr_timeseries.png` on
disk with an entry in `provenance/claims.yaml`, `results.json` written, and a
short report of what each number came out as — including anything that did not
match.
