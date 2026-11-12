from datetime import datetime, timedelta

import numpy as np
import pytest

from energy_storage_dispatch_model_interview.asset import Asset
from energy_storage_dispatch_model_interview.dispatch import solve_dispatch
from energy_storage_dispatch_model_interview.price_series import PriceSeries

START = datetime(2018, 1, 1)
ONE_HOUR = timedelta(hours=1)


def hourly_prices(*prices: float) -> PriceSeries:
    """A price series of hourly prices, so 1 MW for one period is 1 MWh."""
    return PriceSeries(np.array(prices, dtype=float), START, ONE_HOUR)


def test_a_full_battery_sells_its_energy_when_the_price_is_positive():
    """One period at a positive price: a full 1 MWh battery (power is ample at 2 MW) sells all
    of it, at 1 MW for the hour, and ends empty."""
    asset = Asset(max_charge_power=2.0, max_discharge_power=2.0, energy_capacity=1.0)

    dispatch = solve_dispatch([hourly_prices(10.0)], asset, starting_state_of_charge=1.0)

    np.testing.assert_allclose(dispatch.market_powers[0], [1.0], atol=1e-9)
    np.testing.assert_allclose(dispatch.state_of_charge, [0.0], atol=1e-9)


@pytest.mark.parametrize("market_count", [0, 2])
def test_zero_or_two_markets_are_rejected(market_count):
    """Until a second market is supported, zero or two markets are refused: with two, charging
    in one and discharging in the other would be free arbitrage, as exclusivity is not modelled."""
    asset = Asset(max_charge_power=2.0, max_discharge_power=2.0, energy_capacity=1.0)
    markets = [hourly_prices(10.0)] * market_count

    with pytest.raises(ValueError):
        solve_dispatch(markets, asset, starting_state_of_charge=1.0)
