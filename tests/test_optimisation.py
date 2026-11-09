import numpy as np
from energy_storage_dispatch_model_interview.optimistion import OptimisationProblem
import pytest

@pytest.fixture
def bounds():
    return -1.0, 1.0

def setup_solve_with_bounds(prices, bounds) -> "OptimisationProblem":
    lower, upper = bounds
    problem = (
        OptimisationProblem()
        .add_market_price(prices)
        .set_asset_power_lower_bound(lower)
        .set_asset_power_upper_bound(upper)
    )
    return problem


def test_alternating_prices(bounds):
    test_price = np.array([1,-1,1,-1])
    expected_answer = np.array([1,-1,1,-1])
    problem = setup_solve_with_bounds(test_price, bounds)

    asset_power_decision = problem.solve_for_asset_powers()
    np.testing.assert_allclose(asset_power_decision, expected_answer)
    
def test_negative_prices(bounds):
    test_price = np.array([-1,-1,-1,-1])
    expected_answer = np.array([-1,-1,-1,-1])
    problem = setup_solve_with_bounds(test_price, bounds)

    asset_power_decision = problem.solve_for_asset_powers()
    np.testing.assert_allclose(asset_power_decision, expected_answer)
    

def test_positive_prices(bounds):
    test_price = np.array([1,1,1,1])
    expected_answer = np.array([1,1,1,1])
    problem = setup_solve_with_bounds(test_price, bounds)

    asset_power_decision = problem.solve_for_asset_powers()
    np.testing.assert_allclose(asset_power_decision, expected_answer)
    


def test_full_soc_is_binding(bounds):
    test_price = np.array([-1,-1,-1,-1])
    starting_state_of_charge = 0
    expected_answer = np.array([0,0,0,0])
    
    problem = setup_solve_with_bounds(test_price, bounds)

    asset_power_decision = problem.solve_for_asset_powers()
    np.testing.assert_allclose(asset_power_decision, expected_answer)
    


def test_empty_soc_is_binding(bounds):
    test_price = np.array([1,1,1,1])
    starting_state_of_charge = 1
    expected_answer = np.array([0,0,0,0])
    
    problem = setup_solve_with_bounds(test_price, bounds)

    asset_power_decision = problem.solve_for_asset_powers()
    np.testing.assert_allclose(asset_power_decision, expected_answer)
    
