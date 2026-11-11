# Solve over a rolling foresight window, not the whole series

Status: accepted

A real battery does not know years of prices in advance, so we solve in windows even though a whole-series solve is feasible (about 9 s as a MILP).

- Each solve covers a committed period plus a lookahead; only the committed period is kept.
- State of charge carries from one window into the next.
- Defaults are 24 h committed and 8 h lookahead, both configurable.
- Both must be multiples of the lowest common multiple of the market intervals.
- A whole-series solve is the special case of committed period = series length, lookahead = 0.
- Windows place no value on leftover energy, so the battery drains near window edges; accepted, measured using the special case above.
- The 24 h / 8 h defaults are an assumption, not derived from the data.
