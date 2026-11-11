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

def calculate_new_state_of_charge(initial_state_of_charge: float, asset_powers: ArrayLike) -> float:
    new_state_of_charge = initial_state_of_charge + asset_powers.sum()
    return new_state_of_charge

def run_single_day(starting_index: int, hourly_market: "EnergyMarket"):
    num_time_steps = 24 # Number of timesteps.
    additional_horizon = 8 # Adds data to the starting index

    # When we get to the end of the price series, we don't use additional data
    end_index = starting_index + num_time_steps + additional_horizon
    if end_index > len(hourly_market._price):
        end_index = len(hourly_market._price)


    problem = setup_optimisation_problem(np.asarray(hourly_market._price[starting_index:end_index]))
    asset_power_decision = problem.solve_for_asset_powers()
    # We don't return the all the information so that we don't leave SoC in a bad position for the next set of data. 
    return asset_power_decision[:num_time_steps]

def main():
    # Set the classes up

    hourly_market = EnergyMarket()
    hourly_market.read_price_file("market_data_Hourly data.csv")

    # setup a list to put in multiple asset power outcomes into
    asset_power_decisions = []

    # figure out how many days we need to run for. 
    num_timestamps = len(hourly_market._price)
    for n in range(0, num_timestamps, 24):
        daily_power_decisions = run_single_day(n, hourly_market)
        asset_power_decisions.append(daily_power_decisions)

    full_horizon_asset_power_decisions = np.concatenate(asset_power_decisions)

    print(full_horizon_asset_power_decisions[:100])
if __name__ == "__main__":
    main()