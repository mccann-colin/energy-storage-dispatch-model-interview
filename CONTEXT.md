# Battery dispatch

A model that schedules a battery's charging and discharging across wholesale electricity markets to maximise profit.

## Language

**Market**:
A wholesale electricity market with its own price series and its own market interval. The battery buys or sells energy into it.
_Avoid_: Exchange, venue

**Market interval**:
The fixed period for which a market publishes one price. Capacity committed to a market is held for the whole of its market interval.
_Avoid_: Settlement period, resolution

**Price series**:
The ordered prices of one market, one per market interval, covering a whole number of days. A series with a blank price or an incomplete day is rejected, not repaired.
_Avoid_: Price file, price data

**Base interval**:
The model's own time resolution, equal to the highest common factor of all market intervals. State of charge is tracked once per base interval, and every market boundary falls on a base interval boundary.
_Avoid_: Time step, timestep, tick

**Dispatch mode**:
Whether the battery is charging or discharging in a base interval. Exactly one applies per base interval, across all markets together; power may still be split across markets in the same direction.
_Avoid_: State (overloaded with state of charge), direction

**Foresight window**:
The stretch of future prices the battery is assumed to know when it chooses its dispatch. Each solve covers one foresight window, only its earliest part is kept, and the next solve starts from the resulting state of charge. Prices beyond the window are unknown.
_Avoid_: Rolling horizon, lookahead, perfect foresight
