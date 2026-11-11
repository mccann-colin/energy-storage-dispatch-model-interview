from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    """The battery being dispatched. Powers in MW, capacity in MWh.

    An efficiency is the fraction of energy retained (1.0 is lossless), not the fraction lost.
    """

    max_charge_power: float
    max_discharge_power: float
    energy_capacity: float
    charge_efficiency: float = 1.0
    discharge_efficiency: float = 1.0
