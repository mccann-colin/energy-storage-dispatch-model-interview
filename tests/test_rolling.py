from datetime import datetime, timedelta

import numpy as np
import pytest

from energy_storage_dispatch_model_interview.asset import Asset
from energy_storage_dispatch_model_interview.price_series import PriceSeries
from energy_storage_dispatch_model_interview.rolling import solve_rolling

START = datetime(2018, 1, 1)
ONE_HOUR = timedelta(hours=1)
NO_LOOKAHEAD = timedelta(0)

# Power is ample (2 MW against a 1 MWh battery), so energy is what limits each trade.
ASSET = Asset(max_charge_power=2.0, max_discharge_power=2.0, energy_capacity=1.0)


def hourly_prices(*prices: float) -> PriceSeries:
    """A price series of hourly prices, so 1 MW for one period is 1 MWh."""
    return PriceSeries(np.array(prices, dtype=float), START, ONE_HOUR)


def assert_dispatch(dispatch, expected_powers, expected_state_of_charge):
    """Compare market power and state of charge with hand-derived literals, to within 1e-9."""
    np.testing.assert_allclose(dispatch.market_powers[0], expected_powers, atol=1e-9)
    np.testing.assert_allclose(dispatch.state_of_charge, expected_state_of_charge, atol=1e-9)


def test_with_no_lookahead_the_battery_trades_inside_each_window():
    """Prices rise across all four periods, but each two-period window cannot see past itself,
    so the battery buys and sells inside every window instead of waiting for the highest price."""
    dispatch = solve_rolling(
        [hourly_prices(10.0, 20.0, 30.0, 40.0)],
        ASSET,
        starting_state_of_charge=0.0,
        committed_period=2 * ONE_HOUR,
        lookahead=NO_LOOKAHEAD,
    )

    assert_dispatch(dispatch, [-1.0, 1.0, -1.0, 1.0], [1.0, 0.0, 1.0, 0.0])


def test_enough_lookahead_matches_the_whole_series_and_the_charge_carries_over():
    """With a two-period lookahead the first window sees the top price (40) and holds its energy
    through the boundary. The second window must start from that stored 1 MWh, not from empty,
    or it could not sell at 40."""
    dispatch = solve_rolling(
        [hourly_prices(10.0, 20.0, 30.0, 40.0)],
        ASSET,
        starting_state_of_charge=0.0,
        committed_period=2 * ONE_HOUR,
        lookahead=2 * ONE_HOUR,
    )

    assert_dispatch(dispatch, [-1.0, 0.0, 0.0, 1.0], [1.0, 1.0, 1.0, 0.0])


def test_the_last_window_is_shorter_when_the_series_does_not_divide_evenly():
    """Five periods in two-period windows leave a final window of one period, which has no future
    to trade into, so it does nothing; every period still gets a dispatch."""
    dispatch = solve_rolling(
        [hourly_prices(10.0, 20.0, 30.0, 40.0, 50.0)],
        ASSET,
        starting_state_of_charge=0.0,
        committed_period=2 * ONE_HOUR,
        lookahead=NO_LOOKAHEAD,
    )

    assert_dispatch(dispatch, [-1.0, 1.0, -1.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0, 0.0])


def test_a_committed_period_as_long_as_the_series_is_the_whole_series_solve():
    """One window covering every period sees the whole series, so the battery waits and sells at
    the highest price."""
    dispatch = solve_rolling(
        [hourly_prices(10.0, 20.0, 30.0, 40.0)],
        ASSET,
        starting_state_of_charge=0.0,
        committed_period=4 * ONE_HOUR,
        lookahead=NO_LOOKAHEAD,
    )

    assert_dispatch(dispatch, [-1.0, 0.0, 0.0, 1.0], [1.0, 1.0, 1.0, 0.0])


@pytest.mark.parametrize(
    ("committed_period", "lookahead"),
    [(timedelta(minutes=90), NO_LOOKAHEAD), (ONE_HOUR, timedelta(minutes=90))],
    ids=["committed period", "lookahead"],
)
def test_a_period_that_is_not_a_whole_number_of_market_intervals_is_refused(
    committed_period, lookahead
):
    """On an hourly market a window boundary must fall on a market interval boundary: 90 minutes
    would cut a market interval in half, so it is refused rather than rounded."""
    with pytest.raises(ValueError, match="whole number"):
        solve_rolling(
            [hourly_prices(10.0, 20.0, 30.0, 40.0)],
            ASSET,
            starting_state_of_charge=0.0,
            committed_period=committed_period,
            lookahead=lookahead,
        )
