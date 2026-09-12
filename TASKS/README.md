# The briefs

One file per stage. Each is self-contained: an agent that has read nothing else
in this repository except `README.md` and `CLAUDE.md` can do it.

| | | leaves behind |
|---|---|---|
| `day-1-control.md` | the pipeline finds GW150914 | 9 checks, figure 1 |
| `day-2-waveform.md` | our own waveform, measured against LAL's | 9 checks, figure 2 |
| `day-3-horizon.md` | threshold to distance to volume | 8 checks, figure 3 |
| `day-4-antenna.md` | the blind spots, and the factor of 2.26 | 9 checks, figure 4 |
| `day-5-network.md` | real detectors, the Earth turning | 7 checks, figures 5 and 6 |
| `day-6-page.md` | the page, and the stranger test | 6 checks, the deliverable |

Do them in order. Each one leans on the one before.

## Running one

```
cd C:\Users\tomic\ligo-selection
claude
```

then, as the first message:

```
read TASKS/day-1-control.md and do it
```

Unattended:

```
claude -p "$(cat TASKS/day-1-control.md)" --output-format json > logs/day1.json
```

A `Stop` hook checks the provenance record and will not let the session end
without one. It fires whether or not the agent ever loaded the skill.

## If you would rather use agent-team

Days 4 and 5 are the long ones and are the only reasonable candidates:

```
python C:\Users\tomic\agent-team\bin\job new feature "@TASKS/day-5-network.md" --rounds 2 --workers 1
```

Two things that bit us in the course and will bite again:

- invoke it as `python <path>\bin\job`, never as bare `job` — the shebang says
  `python3`, which Windows resolves to the Microsoft Store stub
- the recipe's checks command is POSIX shell and runs under `cmd.exe`, so it
  fails every round and the PI plans against a permanently red light. Write a
  `_checks_runner.py` in the job directory and point `spec.json`'s
  `checks.command` at `.venv\Scripts\python.exe _checks_runner.py`. Per job,
  every time.

Run `--backend mock` first. It exercises the whole engine offline, free, in about
a minute, and it is where that bug shows up before any money is spent.

For days 1 to 3, plain `claude` is cheaper and easier to watch.

## Reading the result

Whatever ran it, the same three things say whether the stage is done:

```
.venv\Scripts\python.exe -m pytest -q      all green, not just the new file
git status                                 the named figures exist
```

and `provenance/claims.yaml` has an entry for every figure and every claim the
brief asked for.

A stage that reports an honest failure is worth more here than one that reports
success. If a check did not pass, the brief says what to do: write it in
`NOTES.md` and stop. Never widen a tolerance.
