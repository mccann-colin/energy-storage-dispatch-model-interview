# Slice plans

One plan per slice, agreed before any test or code (CLAUDE.md, standard 4). Plans for later slices are written when they are next up.

## Map
- Slice 1: price-series loading and validation. Done. `slice-1-price-series-loading.md`
- Slice 1b: whole-days rule moves from `PriceSeries` to the loader (do before 2b). `slice-1b-whole-days-at-loader.md`
- Slice 2a: `Asset`. `slice-2a-asset.md`
- Slice 2b: dispatch tracer bullet (needs 2a). `slice-2b-dispatch-tracer-bullet.md`
- Slice 2c: energy and power limits (needs 2b). `slice-2c-limits.md`
- Slice 3a: cutting windows (committed period plus lookahead). `slice-3a-cutting-windows.md`
- Slice 3b: rolling solve, carrying state of charge (needs 3a). `slice-3b-rolling-solve.md`
- Slice 4: results output; deletes the old `optimistion.py` and `EnergyMarket` code.
- Slice 5: second market; to be split (base interval, expansion matrix, solving).
- Slice 6: dispatch mode exclusivity.
- Slice 7: efficiencies.
- Slice 8: README and run instructions.

## Later steps (polish, only after the map above works end to end)
- Step 11: Refuse a battery with impossible limits (zero or negative power or capacity), so that a typo in the asset values fails with a clear error instead of producing a nonsense dispatch.
- Step 12: Refuse impossible efficiencies (zero, negative or above one), so that the energy balance never divides by zero or models a battery that creates energy; goes with slice 7.
- Step 13: Refuse a starting charge that does not fit the battery (below empty or above full), so that a wrong starting value is caught up front instead of reaching the solver.
- Step 14: Let the battery's values be changed without editing code, so that results can be varied and reproduced from a settings file. Detail in `slice-2e-load-asset.md`.
- Step 15: Refuse a window that lies outside the series, so that a wrong window position fails loudly instead of being silently clipped.
- Step 16: Refuse a negative lookahead, so that a window is never shorter than its committed period.
- Step 17: Share one copy of the test setup helpers (building hourly prices, comparing a dispatch with expected values), so that a change to a helper is made once and the test files cannot drift apart.

## Priority
- Reach a working two-market dispatch on the real data first; polish comes after.
