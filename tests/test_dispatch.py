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


RISING = (10.0, 20.0, 30.0, 40.0)
FALLING = (40.0, 30.0, 20.0, 10.0)


def assert_dispatch(dispatch, expected_powers, expected_state_of_charge):
    """Compare market power and state of charge with hand-derived literals, to within 1e-9."""
    np.testing.assert_allclose(dispatch.market_powers[0], expected_powers, atol=1e-9)
    np.testing.assert_allclose(dispatch.state_of_charge, expected_state_of_charge, atol=1e-9)


def test_a_full_battery_sells_its_energy_when_the_price_is_positive():
    """One period at a positive price: a full 1 MWh battery (power is ample at 2 MW) sells all
    of it, at 1 MW for the hour, and ends empty."""
    asset = Asset(max_charge_power=2.0, max_discharge_power=2.0, energy_capacity=1.0)

    dispatch = solve_dispatch([hourly_prices(10.0)], asset, starting_state_of_charge=1.0)

    np.testing.assert_allclose(dispatch.market_powers[0], [1.0], atol=1e-9)
    np.testing.assert_allclose(dispatch.state_of_charge, [0.0], atol=1e-9)


@pytest.mark.parametrize("market_count", [0, 2])
def test_zero_or_two_markets_are_rejected(market_count):
    """Exactly one market is supported: with two, charging in one and discharging in the other
    would be free arbitrage, because nothing stops charge and discharge overlapping."""
    asset = Asset(max_charge_power=2.0, max_discharge_power=2.0, energy_capacity=1.0)
    markets = [hourly_prices(10.0)] * market_count

    with pytest.raises(ValueError):
        solve_dispatch(markets, asset, starting_state_of_charge=1.0)


# --- Energy limits: power is ample (2 MW against a 1 MWh battery), so only energy binds ------


def test_the_energy_limit_binds_the_trade():
    """With rising prices and an empty 1 MWh battery, it charges in the cheapest period and sells
    in the dearest: the capacity, not the power, limits the trade."""
    asset = Asset(max_charge_power=2.0, max_discharge_power=2.0, energy_capacity=1.0)

    dispatch = solve_dispatch([hourly_prices(*RISING)], asset, starting_state_of_charge=0.0)

    assert_dispatch(dispatch, [-1.0, 0.0, 0.0, 1.0], [1.0, 1.0, 1.0, 0.0])


def test_a_full_battery_sells_first_when_prices_fall():
    """Energy binds, power is ample: a full battery cannot charge further, and prices only fall,
    so it sells all its energy in the first (dearest) period."""
    asset = Asset(max_charge_power=2.0, max_discharge_power=2.0, energy_capacity=1.0)

    dispatch = solve_dispatch([hourly_prices(*FALLING)], asset, starting_state_of_charge=1.0)

    assert_dispatch(dispatch, [1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0])


def test_an_empty_battery_does_nothing_when_prices_fall():
    """No limit binds: with prices only falling there is no spread to earn, and an empty battery
    has nothing to sell, so it never trades."""
    asset = Asset(max_charge_power=2.0, max_discharge_power=2.0, energy_capacity=1.0)

    dispatch = solve_dispatch([hourly_prices(*FALLING)], asset, starting_state_of_charge=0.0)

    assert_dispatch(dispatch, [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0])


def test_the_starting_charge_is_respected():
    """Energy binds, power is ample: a half-full battery only needs to charge the other half
    before selling the full capacity."""
    asset = Asset(max_charge_power=2.0, max_discharge_power=2.0, energy_capacity=1.0)

    dispatch = solve_dispatch([hourly_prices(*RISING)], asset, starting_state_of_charge=0.5)

    assert_dispatch(dispatch, [-0.5, 0.0, 0.0, 1.0], [1.0, 1.0, 1.0, 0.0])


# --- Power limits ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("power_limit", "expected_powers", "expected_state_of_charge"),
    [
        (1.0, [1.0, 1.0, 1.0, 1.0], [99.0, 98.0, 97.0, 96.0]),
        (2.0, [2.0, 2.0, 2.0, 2.0], [98.0, 96.0, 94.0, 92.0]),
    ],
    ids=["1 MW", "2 MW"],
)
def test_the_power_limit_binds_and_dispatch_scales_with_it(
    power_limit, expected_powers, expected_state_of_charge
):
    """With ample energy (100 MWh, starting full) and positive prices, the battery sells at its
    power limit every period; doubling the limit doubles the dispatch."""
    asset = Asset(
        max_charge_power=power_limit, max_discharge_power=power_limit, energy_capacity=100.0
    )

    dispatch = solve_dispatch([hourly_prices(*RISING)], asset, starting_state_of_charge=100.0)

    assert_dispatch(dispatch, expected_powers, expected_state_of_charge)


def test_both_limits_bind_when_the_battery_can_neither_fill_nor_empty_in_one_period():
    """At 0.5 MW a period moves 0.5 MWh, so a 1 MWh battery needs two periods to fill and two to
    empty: power and energy limits bind together."""
    asset = Asset(max_charge_power=0.5, max_discharge_power=0.5, energy_capacity=1.0)

    dispatch = solve_dispatch([hourly_prices(*RISING)], asset, starting_state_of_charge=0.0)

    assert_dispatch(dispatch, [-0.5, -0.5, 0.5, 0.5], [0.5, 1.0, 0.5, 0.0])


def test_charge_and_discharge_limits_are_separate():
    """Charging allows 2 MW and discharging only 1 MW. Charging fills the 2 MWh battery in one
    period (charge power and energy bind together); the 1 MW discharge limit then binds, so
    emptying takes two periods."""
    asset = Asset(max_charge_power=2.0, max_discharge_power=1.0, energy_capacity=2.0)

    dispatch = solve_dispatch([hourly_prices(*RISING)], asset, starting_state_of_charge=0.0)

    assert_dispatch(dispatch, [-2.0, 0.0, 1.0, 1.0], [2.0, 2.0, 1.0, 0.0])
