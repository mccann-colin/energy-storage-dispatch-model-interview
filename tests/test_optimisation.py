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

def test_negative_asset_power_upper_bound_rejected():
    problem = (
            OptimisationProblem()
        )
    with pytest.raises(ValueError):
        problem.set_asset_power_upper_bound(-1)

def test_positive_asset_power_lower_bound_rejected():
    problem = (
            OptimisationProblem()
        )
    with pytest.raises(ValueError):
        problem.set_asset_power_lower_bound(1)
    

def test_full_soc_is_binding(bounds):
    test_price = np.array([-1,-1,-1,-1])
    expected_answer = np.array([0,0,0,0])
    
    problem = setup_solve_with_bounds(test_price, bounds)
    problem.set_asset_energy_capacity(1)
    problem.set_starting_state_of_charge(1)
    problem.add_soc_constraint()
    asset_power_decision = problem.solve_for_asset_powers()
    np.testing.assert_allclose(asset_power_decision, expected_answer)
    
def test_ramping_positive_prices(bounds):
    # Used to make sure that the SoC constraint is the behaviour that's making the other test change. 
    test_price = np.array([1, 2, 3, 4])
    expected_answer = np.array([1,1,1,1])
    problem = setup_solve_with_bounds(test_price, bounds)
    asset_power_decision = problem.solve_for_asset_powers()
    np.testing.assert_allclose(asset_power_decision, expected_answer)

def test_low_soc_is_binding(bounds):
    # Uses a ramping price series as a purely postive, flat price series is degenerate without cycling cost/ efficiencies
    test_price = np.array([1, 2, 3, 4])
    expected_answer = np.array([-1,0,0,1])
    problem = setup_solve_with_bounds(test_price, bounds)
    problem.set_asset_energy_capacity(1)
    problem.set_starting_state_of_charge(0)
    problem.add_soc_constraint()
    asset_power_decision = problem.solve_for_asset_powers()
    np.testing.assert_allclose(asset_power_decision, expected_answer)
    
