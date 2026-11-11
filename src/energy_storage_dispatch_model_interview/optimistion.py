import numpy as np
from numpy.typing import NDArray, ArrayLike
from scipy.optimize import milp, LinearConstraint, Bounds


class OptimisationProblem:
    def __init__(self) -> None:
        self._asset_power_lower_bound = -np.inf # Measured in MW
        self._asset_power_upper_bound = np.inf # Measured in MW
        self._starting_state_of_charge = 0 # Measured in MWh
        self._asset_energy_capacity = 1 # Measured in MWh
        self._time_step = 1 # Measured in hours
        self._num_of_time_periods = 1
        self._constraints: list[LinearConstraint] = []
        pass

    def add_market_price(self, price:ArrayLike) -> "OptimisationProblem":
        self._prices = price
        self._num_of_time_periods = max(self._num_of_time_periods, len(price))
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
        elif starting_state_of_charge > self._asset_energy_capacity:
            raise ValueError(f"starting_soc needs to be <= {self._asset_energy_capacity}, current value is {starting_state_of_charge}")
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

    def add_soc_constraint(self) -> "OptimisationProblem":
        starting_energy = self._starting_state_of_charge
        capacity = self._asset_energy_capacity
        n_periods = self._num_of_time_periods
        length_of_period = self._time_step

        # Make a matrix that takes the cumulative sum of the asset powers * time and applies it to the state of charge. 
        energy_discharged_matrix = length_of_period * np.tril(np.ones((n_periods, n_periods)))
        self._constraints.append(
            LinearConstraint(energy_discharged_matrix, starting_energy - capacity, starting_energy)
        )
        return self
    
    def solve_for_asset_powers(self) -> NDArray[np.float64]:
        """Solves for asset powers which are returned as raw MW"""
        result = milp(
            c = -self._prices,
            bounds = Bounds(self._asset_power_lower_bound,self._asset_power_upper_bound),
            constraints=self._constraints
        )
        market_power = result.x
        return market_power