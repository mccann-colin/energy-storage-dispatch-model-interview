import numpy as np
from numpy.typing import NDArray, ArrayLike

from scipy.optimize import milp, LinearConstraint, Bounds


class OptimisationProblem:
    def __init__(self) -> None:
        self._asset_power_lower_bound = -np.inf
        self._asset_power_upper_bound = np.inf
        pass

    def add_market_price(self, price:ArrayLike) -> "OptimisationProblem":
        self._prices = price
        return self

    def set_asset_power_upper_bound(self, asset_power_upper_bound: Float) -> "OptimisationProblem":
        self._asset_power_upper_bound = asset_power_upper_bound
        return self

    def set_asset_power_lower_bound(self, asset_power_lower_bound: Float) -> "OptimisationProblem":
        self._asset_power_lower_bound = asset_power_lower_bound
        return self

    def solve_for_asset_powers(self) -> NDarray[np.float64]:
        result = milp(
            c = -self._prices,
            bounds = Bounds(self._asset_power_lower_bound,self._asset_power_upper_bound)
        )
        return result.x