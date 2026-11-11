# Battery dispatch model (interview exercise)

## Purpose
Python package that schedules a battery across two wholesale price markets to maximise
profit. Assessed on: sensible design, clear communication, and a codebase that is easy to
review. Brief: `2nd Round Technical Question.pdf`. Deliverables: repo link, run
instructions, reproducible results, one-paragraph approach summary.

## Branch policy
- `main` holds the author's own work. Never commit to it or merge into it without being asked.
- All AI-assisted work happens on `ai-driven-development`.

## Commands
- Setup: `uv sync` (Python 3.14, locked in `uv.lock`)
- Tests: `uv run pytest`
- Types: `uv run mypy src`

## Decisions
- Domain conventions (units, sign convention, modelling assumptions) live in `docs/adr/`.
  Read them before changing model code. Propose a new ADR rather than silently changing
  a convention.

## Engineering standards
1. Readability first: clear names, small functions, no clever tricks. A reviewer should
   follow the code without a walkthrough.
2. Small, reviewable changes: one concern per commit; no drive-by refactors.
3. Test-driven: write a failing test first, then the minimal code to pass it, then
   refactor (use the `tdd` skill). No behaviour change without a test.

## Working with the author
- The author is learning: explain why a design is good, and link to control and
  biological-modelling analogies where they help.
- When asked to "advise" or "suggest", don't edit code. Edit only when asked to implement.
