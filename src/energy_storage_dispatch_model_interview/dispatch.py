from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import scipy.sparse as sparse
from numpy.typing import NDArray
from scipy.optimize import Bounds, LinearConstraint, milp

from energy_storage_dispatch_model_interview.asset import Asset
from energy_storage_dispatch_model_interview.price_series import PriceSeries


# eq=False: the generated == would compare numpy arrays, which gives an array, not a bool.
@dataclass(frozen=True, eq=False)
class Dispatch:
    """The result of a solve.

    market_powers: one array per market, in input order; MW, discharge positive.
    state_of_charge: one value per base interval; MWh, at the end of the interval.
    """

    market_powers: tuple[NDArray[np.float64], ...]
    state_of_charge: NDArray[np.float64]


def solve_dispatch(
    markets: Sequence[PriceSeries], asset: Asset, starting_state_of_charge: float
) -> Dispatch:
    """Choose charge and discharge power to maximise revenue over the whole price series.

    The unknowns are stacked as x = [charge | discharge | state of charge], each one entry per
    interval. The energy balance A x = b ties each state of charge to the one before it.
    """
    # Exactly one market: with two, nothing here stops charging in one while discharging in the
    # other, which would be free arbitrage.
    if len(markets) != 1:
        raise ValueError(f"Exactly one market is supported, got {len(markets)}")
    market = markets[0]
    prices = market.prices
    intervals = len(prices)
    interval_hours = market.market_interval.total_seconds() / 3600

    identity = sparse.identity(intervals, format="csr")
    # State of charge in this interval minus the previous one: 1 on the diagonal, -1 just
    # below it. The balance row then reads "change in stored energy = energy in - energy out".
    state_of_charge_change = identity - sparse.eye(intervals, k=-1, format="csr")
    energy_balance = sparse.hstack(
        [
            # Charging stores less energy than it draws from the grid (efficiency <= 1)...
            -asset.charge_efficiency * interval_hours * identity,
            # ...and discharging takes more energy from the battery than it delivers.
            interval_hours / asset.discharge_efficiency * identity,
            state_of_charge_change,
        ],
        format="csr",
    )
    # The starting charge is a known constant, so it moves to the right-hand side of row one.
    right_hand_side = np.zeros(intervals)
    right_hand_side[0] = starting_state_of_charge

    # milp minimises: buying costs money, selling earns it, stored energy has no cost.
    cost = np.concatenate(
        [interval_hours * prices, -interval_hours * prices, np.zeros(intervals)]
    )
    # Each direction of power stays within its own limit, and the state of charge within
    # [0, capacity]; every unknown is non-negative.
    upper = np.concatenate(
        [
            np.full(intervals, asset.max_charge_power),
            np.full(intervals, asset.max_discharge_power),
            np.full(intervals, asset.energy_capacity),
        ]
    )

    result = milp(
        cost,
        constraints=LinearConstraint(energy_balance, right_hand_side, right_hand_side),
        bounds=Bounds(np.zeros(3 * intervals), upper),
    )
    if not result.success:
        raise RuntimeError(f"Dispatch solve failed: {result.message}")

    charge = result.x[:intervals]
    discharge = result.x[intervals : 2 * intervals]
    state_of_charge = result.x[2 * intervals :]
    return Dispatch(market_powers=(discharge - charge,), state_of_charge=state_of_charge)
