from energy_storage_dispatch_model_interview.market import EnergyMarket
from energy_storage_dispatch_model_interview.optimistion import OptimisationProblem
from numpy.typing import ArrayLike
import numpy as np

def setup_optimisation_problem(prices: ArrayLike) -> "OptimisationProblem":
    problem = (
            OptimisationProblem()
            .add_market_price(prices)
            .set_asset_power_lower_bound(-2)
            .set_asset_power_upper_bound(2)
            .set_asset_energy_capacity(4)
            .set_starting_state_of_charge(2)
            .set_time_step(1)
            .add_soc_constraint()
        )
    return problem

def main():
    # Set the classes up

    hourly_market = EnergyMarket()
    hourly_market.read_price_file("market_data_Hourly data.csv")
    problem = setup_optimisation_problem(np.asarray(hourly_market._price[:24]))
    asset_power_decision = problem.solve_for_asset_powers()
    print(asset_power_decision)

if __name__ == "__main__":
    main()