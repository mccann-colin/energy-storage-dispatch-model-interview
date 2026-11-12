# Rebuild time from a regular grid and reject incomplete price series

Status: accepted

The source timestamps are unreliable, but the files align by row position, so we regenerate time on a regular grid and ignore the source labels.

- Market 1 has 6 duplicate labels and irregular steps, all at the three spring clock changes; the same data is in the source xlsx, so it is not a CSV artefact.
- Market 2 has 6 steps of 59:59.999 instead of 1 h, from float storage of datetimes.
- Prices are also repeated or zero around some clock changes.
- Regenerate a regular grid from the first stamp and each market's interval length.
- Join the markets on that grid, which is equivalent to joining by row position.
- Reject a series with blank prices, and a loaded file whose row count is not a whole number of days.
- A loaded file must cover whole days because we assume day-ahead style trading: a full day's prices are fixed at one gate closure before the day starts, so a partial day is a data fault, not a valid input.
- A `PriceSeries` itself may cover any span of prices, so windows and short test series are allowed.
- Odd-looking values are flagged in the output, not rejected or repaired.
- The market interval is supplied by the caller; it is not read from the file or checked against it.
- Passing the wrong interval for a file (1 h for a half-hourly file) is therefore not detected: every timestamp and revenue figure would be silently wrong.
- Accepted for now. Cross-checking the first and last labels against the interval was considered and left out, since it would partly reintroduce trust in the source labels.
- This is a workaround: in practice the fix belongs upstream, at wherever the prices come from.
