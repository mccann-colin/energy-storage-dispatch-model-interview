from collections.abc import Sequence
from datetime import timedelta

import numpy as np
from numpy.typing import NDArray

from energy_storage_dispatch_model_interview.asset import Asset
from energy_storage_dispatch_model_interview.dispatch import Dispatch, solve_dispatch
from energy_storage_dispatch_model_interview.price_series import PriceSeries
from energy_storage_dispatch_model_interview.windows import rolling_windows


def solve_rolling(
    markets: Sequence[PriceSeries],
    asset: Asset,
    starting_state_of_charge: float,
    committed_period: timedelta,
    lookahead: timedelta,
) -> Dispatch:
    """Solve a long series one foresight window at a time.

    Each window is solved on its own, but only its committed period is kept; the lookahead
    just helps the battery decide what to do in the committed period.
    """
    market_interval = markets[0].market_interval
    windows = rolling_windows(
        total_intervals=len(markets[0].prices),
        committed_intervals=_count_intervals(committed_period, market_interval, "committed period"),
        lookahead_intervals=_count_intervals(lookahead, market_interval, "lookahead"),
    )

    kept_powers: list[list[NDArray[np.float64]]] = [[] for _ in markets]  # one list per market
    kept_states: list[NDArray[np.float64]] = []
    state_of_charge = starting_state_of_charge
    for window in windows:
        window_markets = [market.window(window.first, window.stop) for market in markets]
        dispatch = solve_dispatch(window_markets, asset, state_of_charge)
        committed_intervals = window.committed_stop - window.first
        for market_index, powers in enumerate(dispatch.market_powers):
            kept_powers[market_index].append(powers[:committed_intervals])
        kept_states.append(dispatch.state_of_charge[:committed_intervals])
        # The next window starts from the last state of charge we kept.
        state_of_charge = float(kept_states[-1][-1])

    return Dispatch(
        market_powers=tuple(np.concatenate(parts) for parts in kept_powers),
        state_of_charge=np.concatenate(kept_states),
    )


def _count_intervals(period: timedelta, market_interval: timedelta, name: str) -> int:
    """How many market intervals fit in `period`, which must be an exact multiple of one.

    A window boundary has to fall between market intervals: a commitment to a market is held
    for its whole interval, so a window must never cut one in half.
    """
    count, remainder = divmod(period, market_interval)
    if remainder != timedelta(0):
        raise ValueError(
            f"The {name} must be a whole number of market intervals ({market_interval}), "
            f"got {period}"
        )
    return count
