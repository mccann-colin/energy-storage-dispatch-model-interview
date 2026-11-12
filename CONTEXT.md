# Battery dispatch

A model that schedules a battery's charging and discharging across wholesale electricity markets to maximise profit.

## Language

**Asset**:
The battery being dispatched.
_Avoid_: Unit, plant

**State of charge**:
The energy stored in the asset, in MWh, at the end of a base interval.
_Avoid_: SoC, charge level, charge (clashes with charging)

**Market power**:
The net power committed to one market over a market interval, in MW; discharge is positive.
_Avoid_: Position, dispatch (that means the whole result)

**Dispatch**:
The result of a solve: the market power and state of charge chosen for every interval.
_Avoid_: Schedule, solution

**Market**:
A wholesale electricity market with its own price series and its own market interval. The battery buys or sells energy into it.
_Avoid_: Exchange, venue

**Market interval**:
The fixed period for which a market publishes one price. Capacity committed to a market is held for the whole of its market interval.
_Avoid_: Settlement period, resolution

**Price series**:
The ordered prices of one market, one per market interval, over any span. A series with a blank price is rejected, not repaired; a file loaded as a series must cover whole days.
_Avoid_: Price file, price data

**Base interval**:
The model's own time resolution, equal to the highest common factor of all market intervals. State of charge is tracked once per base interval, and every market boundary falls on a base interval boundary.
_Avoid_: Time step, timestep, tick

**Dispatch mode**:
Whether the battery is charging or discharging in a base interval. Exactly one applies per base interval, across all markets together; power may still be split across markets in the same direction.
_Avoid_: State (overloaded with state of charge), direction

**Foresight window**:
The stretch of future prices the battery is assumed to know when it chooses its dispatch: a committed period followed by a lookahead. Each solve covers one foresight window, and the next solve starts from the state of charge at the end of the committed period. Prices beyond the window are unknown.
_Avoid_: Rolling horizon, perfect foresight

**Committed period**:
The part of a foresight window whose dispatch is kept.
_Avoid_: Applied block, step

**Lookahead**:
The part of a foresight window beyond the committed period; it informs the committed dispatch and is then discarded.
_Avoid_: Horizon, forecast
