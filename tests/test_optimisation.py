import numpy as np
from energy_storage_dispatch_model_interview.optimistion import single_market_optimisation

def test_single_market_single_period_optimisation():
    test_price = np.array([1,-1,1,-1])
    expected_answer = np.array([1,-1,1,-1])
    asset_power_lower_bound = -1
    asset_power_upper_bound = 1
    asset_power_decision = single_market_optimisation(test_price, asset_power_lower_bound, asset_power_upper_bound)
    np.testing.assert_allclose(asset_power_decision, expected_answer)
    
