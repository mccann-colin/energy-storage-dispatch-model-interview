# Slice plans

One plan per slice, agreed before any test or code (CLAUDE.md, standard 4). Plans for later slices are written when they are next up.

## Map
- Slice 1: price-series loading and validation. Done. `slice-1-price-series-loading.md`
- Slice 1b: whole-days rule moves from `PriceSeries` to the loader (do before 2b). `slice-1b-whole-days-at-loader.md`
- Slice 2a: `Asset`. `slice-2a-asset.md`
- Slice 2b: dispatch tracer bullet (needs 2a). `slice-2b-dispatch-tracer-bullet.md`
- Slice 2c: energy and power limits (needs 2b). `slice-2c-limits.md`
- Slice 3: rolling foresight window; to be split (window arithmetic, carried state of charge, end of series).
- Slice 4: results output; deletes the old `optimistion.py` and `EnergyMarket` code.
- Slice 5: second market; to be split (base interval, expansion matrix, solving).
- Slice 6: dispatch mode exclusivity.
- Slice 7: efficiencies.
- Slice 8: README and run instructions.

## Later steps (polish, only after the map above works end to end)
- Step 11: a battery with impossible limits (zero or negative power or capacity) is refused with a clear error.
- Step 12: a battery with impossible efficiencies (zero, negative or above one) is refused; goes with slice 7.
- Step 13: a starting charge that does not fit the battery (below empty or above full) is refused.
- Step 14: the battery's values can be changed without editing code. Detail in `slice-2e-load-asset.md`.

## Priority
- Reach a working two-market dispatch on the real data first; polish comes after.
