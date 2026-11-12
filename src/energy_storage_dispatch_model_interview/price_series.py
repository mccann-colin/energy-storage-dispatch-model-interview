from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

# Mandated CSV header (ADR 0002): by-name columns, so column order never matters.
REQUIRED_HEADER = ("datetime", "price")

ONE_SECOND = timedelta(seconds=1)
ONE_DAY = timedelta(days=1)


# frozen: a PriceSeries cannot be changed after it is built, so a valid one stays valid.
# eq=False: the generated == would compare numpy arrays, which gives an array, not a bool.
@dataclass(frozen=True, eq=False)
class PriceSeries:
    """One market's prices on a regular grid.

    Validation runs once, in __post_init__: any PriceSeries that exists is valid, so later
    code never re-checks it. `start` is naive wall-clock time and is never converted.
    """

    prices: NDArray[np.float64]
    start: datetime
    market_interval: timedelta

    def __post_init__(self) -> None:
        if len(self.prices) == 0:
            raise ValueError("Price series is empty")
        if np.isnan(self.prices).any():
            raise ValueError("Price series has a blank price")
        if self.market_interval <= timedelta(0):
            raise ValueError("Market interval must be positive")
        # Whole seconds only, so `timestamps` below can use exact integer seconds.
        if self.market_interval % ONE_SECOND != timedelta(0):
            raise ValueError("Market interval must be a whole number of seconds")
        # timedelta % timedelta is the remainder: zero means the interval divides a day exactly.
        if ONE_DAY % self.market_interval != timedelta(0):
            raise ValueError("Market interval must divide a day exactly")

    @property
    def timestamps(self) -> NDArray[np.datetime64]:
        """Regular grid rebuilt from `start` and `market_interval`; source labels play no part."""
        step = np.timedelta64(int(self.market_interval.total_seconds()), "s")
        return np.datetime64(self.start, "s") + np.arange(len(self.prices)) * step


def load_price_series(path: str | Path, market_interval: timedelta) -> PriceSeries:
    """Read a `datetime,price` CSV into a PriceSeries.

    Only the first label is used (as `start`); later labels are never parsed (ADR 0002).
    The file must cover whole days (ADR 0002).
    `market_interval` is supplied by the caller and is not checked against the file.
    """
    table = pd.read_csv(path)
    if tuple(table.columns) != REQUIRED_HEADER:
        raise ValueError(f"CSV header must be {REQUIRED_HEADER}, got {tuple(table.columns)}")
    if table.empty:
        raise ValueError("CSV has a header but no rows")
    # Day-ahead assumption (ADR 0002): a loaded file covers whole days, never a partial day.
    if (len(table) * market_interval) % ONE_DAY != timedelta(0):
        raise ValueError("CSV must cover a whole number of days")
    return PriceSeries(
        # A blank price becomes NaN (rejected by PriceSeries); non-numeric text raises here.
        prices=table["price"].to_numpy(dtype=np.float64),
        start=pd.to_datetime(table["datetime"].iloc[0]).to_pydatetime(),
        market_interval=market_interval,
    )
