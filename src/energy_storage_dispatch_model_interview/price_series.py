from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray


REQUIRED_HEADER = ["datetime", "price"]
ONE_DAY = timedelta(days=1)


@dataclass(frozen=True, eq=False)
class PriceSeries:
    prices: NDArray[np.float64]
    start: datetime
    market_interval: timedelta

    def __post_init__(self) -> None:
        if len(self.prices) == 0:
            raise ValueError("Price series is empty")
        if np.isnan(self.prices).any():
            raise ValueError("Price series has a blank price")
        if ONE_DAY % self.market_interval != timedelta(0):
            raise ValueError("Market interval must divide a day exactly")
        if (len(self.prices) * self.market_interval) % ONE_DAY != timedelta(0):
            raise ValueError("Price series must cover a whole number of days")

    @property
    def timestamps(self) -> NDArray[np.datetime64]:
        step = np.timedelta64(int(self.market_interval.total_seconds()), "s")
        return np.datetime64(self.start, "s") + np.arange(len(self.prices)) * step


def load_price_series(path: str | Path, market_interval: timedelta) -> PriceSeries:
    table = pd.read_csv(path)
    if list(table.columns) != REQUIRED_HEADER:
        raise ValueError(f"CSV header must be {REQUIRED_HEADER}, got {list(table.columns)}")
    return PriceSeries(
        prices=table["price"].to_numpy(dtype=np.float64),
        start=pd.to_datetime(table["datetime"].iloc[0]).to_pydatetime(),
        market_interval=market_interval,
    )
