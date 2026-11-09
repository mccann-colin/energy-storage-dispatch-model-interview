import numpy as np
from numpy.typing import NDArray

from scipy.optimize import milp, LinearConstraint, Bounds

def single_market_optimisation(prices: NDArray[np.float64], asset_power_lower_bound : float, asset_power_upper_bound : float) -> NDArray(np.float64):
    number_of_periods = len(prices)
    prices_for_minimisation = -prices
    asset_power_bounds = Bounds(asset_power_lower_bound, asset_power_upper_bound)

    result = milp(
        c=prices_for_minimisation,
        bounds=asset_power_bounds
    )
    return result.x