import numpy as np
from energy_storage_dispatch_model_interview.optimistion import single_market_optimisation
import pytest

@pytest.fixture
def bounds():
    return -1.0, 1.0

def test_alternating_prices(bounds):
    test_price = np.array([1,-1,1,-1])
    expected_answer = np.array([1,-1,1,-1])
    asset_power_lower_bound, asset_power_upper_bound = bounds
    asset_power_decision = single_market_optimisation(test_price, asset_power_lower_bound, asset_power_upper_bound)
    np.testing.assert_allclose(asset_power_decision, expected_answer)
    
def test_negative_prices(bounds):
    test_price = np.array([-1,-1,-1,-1])
    expected_answer = np.array([-1,-1,-1,-1])
    asset_power_lower_bound, asset_power_upper_bound = bounds
    asset_power_decision = single_market_optimisation(test_price, asset_power_lower_bound, asset_power_upper_bound)
    np.testing.assert_allclose(asset_power_decision, expected_answer)

def test_positive_prices(bounds):
    test_price = np.array([1,1,1,1])
    expected_answer = np.array([1,1,1,1])
    asset_power_lower_bound, asset_power_upper_bound = bounds
    asset_power_decision = single_market_optimisation(test_price, asset_power_lower_bound, asset_power_upper_bound)
    np.testing.assert_allclose(asset_power_decision, expected_answer)


def test_full_soc_is_binding(bounds):
    test_price = np.array([-1,-1,-1,-1])
    starting_state_of_charge = 0
    expected_answer = np.array([0,0,0,0])
    
    asset_power_lower_bound, asset_power_upper_bound = bounds
    asset_power_decision = single_market_optimisation(test_price, asset_power_lower_bound, asset_power_upper_bound, starting_state_of_charge)
    np.testing.assert_allclose(asset_power_decision, expected_answer)


def test_empty_soc_is_binding(bounds):
    test_price = np.array([1,1,1,1])
    starting_state_of_charge = 1
    expected_answer = np.array([0,0,0,0])
    
    asset_power_lower_bound, asset_power_upper_bound = bounds
    asset_power_decision = single_market_optimisation(test_price, asset_power_lower_bound, asset_power_upper_bound, starting_state_of_charge)
    np.testing.assert_allclose(asset_power_decision, expected_answer)
