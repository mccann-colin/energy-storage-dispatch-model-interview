import numpy as np
from numpy.typing import NDArray, ArrayLike

from scipy.optimize import milp, LinearConstraint, Bounds


class OptimisationProblem:
    def __init__(self) -> None:
        self._asset_power_lower_bound = -np.inf # Measured in MW
        self._asset_power_upper_bound = np.inf # Measured in MW
        self._starting_state_of_charge = 0 # Measured in MWh
        self._asset_energy_capacity = 1 # Measured in MWh
        self._time_step = 60 # Measured in minutes
        pass

    def add_market_price(self, price:ArrayLike) -> "OptimisationProblem":
        self._prices = price
        return self

    def set_asset_power_upper_bound(self, asset_power_upper_bound: float) -> "OptimisationProblem":
        self._asset_power_upper_bound = asset_power_upper_bound
        return self

    def set_asset_power_lower_bound(self, asset_power_lower_bound: float) -> "OptimisationProblem":
        self._asset_power_lower_bound = asset_power_lower_bound
        return self

    def set_starting_state_of_charge(self, starting_state_of_charge: float) -> "OptimisationProblem":
        if starting_state_of_charge < 0.0 :
            raise ValueError(f"starting_soc needs to be >= 0, current value is {starting_state_of_charge}")
        elif starting_state_of_charge > 1.0 :
            raise ValueError(f"starting_soc needs to be <= 1, current value is {starting_state_of_charge}")
        self._starting_state_of_charge = starting_state_of_charge
        return self

    def set_asset_energy_capacity(self, asset_energy_capacity: float) -> "OptimisationProblem":
        if asset_energy_capacity <= 0:
            raise ValueError(f"energy_capacity must be > 0, current value is {asset_energy_capacity}")
        self._asset_energy_capacity = asset_energy_capacity
        return self

    def set_time_step(self, time_step: float) -> "OptimisationProblem":
        self._time_step = time_step
        return self
    
    def solve_for_asset_powers(self) -> NDarray[np.float64]:
        """Solves for asset powers which are returned as raw MW"""
        result = milp(
            c = -self._prices,
            bounds = Bounds(self._asset_power_lower_bound,self._asset_power_upper_bound)
        )
        return result.x