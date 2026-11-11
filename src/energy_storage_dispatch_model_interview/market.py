import pandas as pd
import numpy as np
from numpy.typing import NDArray, ArrayLike

class EnergyMarket:
    def __init__(self) -> None:
        self._file_df: pd.DataFrame | None = None
        self._price: NDArray[np.float64] | None = None

    def read_price_file(self, file_path: str):
        self._file_df = pd.read_csv(file_path)
        self._price = np.asarray(self._file_df["price"])
        self._timestamps = np.asarray(self._file_df["timestamps"])
        return self





