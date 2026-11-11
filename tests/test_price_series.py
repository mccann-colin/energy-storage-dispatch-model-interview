from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

from energy_storage_dispatch_model_interview.price_series import PriceSeries, load_price_series

START = datetime(2018, 1, 1)

# One whole hourly day of prices (GBP/MWh). Written to CSV by the loader tests and passed
# straight to PriceSeries by the validation tests, so both seams share one known-good literal.
HOURLY_DAY_PRICES = [
    51.89, 55.49, 51.06, 44.76, 40.07, 44.42, 50.295, 52.145,
    48.33, 44.595, 44.37, 46.1, 47.2, 45.9, 43.3, 44.8,
    52.6, 61.5, 75.2, 80.1, 70.4, 60.3, 55.5, 50.0,
]


def write_csv(path: Path, header: str, rows: list[tuple[str, float | str]]) -> Path:
    lines = [header] + [f"{label},{price}" for label, price in rows]
    path.write_text("\n".join(lines) + "\n")
    return path


def hourly_day_rows() -> list[tuple[str, float]]:
    return [(f"2018-01-01 {hour:02d}:00:00.000", price) for hour, price in enumerate(HOURLY_DAY_PRICES)]


# --- Seam 2: load_price_series -------------------------------------------------------------


def test_known_file_contents_are_read_correctly(tmp_path):
    """Prices come back exactly as written, in order, and start is the first label."""
    path = write_csv(tmp_path / "prices.csv", "datetime,price", hourly_day_rows())

    series = load_price_series(path, market_interval=timedelta(hours=1))

    np.testing.assert_allclose(series.prices, HOURLY_DAY_PRICES)
    assert series.start == datetime(2018, 1, 1, 0, 0)


def test_later_labels_are_ignored_entirely(tmp_path):
    """Only the first label is used: duplicates, float artefacts and unparseable text after
    row one must not change the regular grid, nor make loading fail (ADR 0002)."""
    rows = hourly_day_rows()
    rows[5] = ("2018-01-01 04:00:00.000", rows[5][1])  # duplicate label
    rows[9] = ("2018-01-01 08:59:59.994", rows[9][1])  # float-storage artefact
    rows[12] = ("not a date", rows[12][1])  # would raise if every label were parsed
    path = write_csv(tmp_path / "prices.csv", "datetime,price", rows)

    series = load_price_series(path, market_interval=timedelta(hours=1))

    timestamps = series.timestamps
    assert len(timestamps) == 24
    assert timestamps[0] == np.datetime64("2018-01-01T00:00:00")
    assert timestamps[-1] == np.datetime64("2018-01-01T23:00:00")
    assert (np.diff(timestamps) == np.timedelta64(1, "h")).all()


def test_time_steps_other_than_one_hour_are_read_correctly(tmp_path):
    """The grid follows the market interval given, not a hardcoded hour (half-hourly here)."""
    half_hourly_prices = [float(i) for i in range(48)]
    rows = [
        (f"2018-01-01 {i // 2:02d}:{30 * (i % 2):02d}:00", price)
        for i, price in enumerate(half_hourly_prices)
    ]
    path = write_csv(tmp_path / "prices.csv", "datetime,price", rows)

    series = load_price_series(path, market_interval=timedelta(minutes=30))

    np.testing.assert_allclose(series.prices, half_hourly_prices)
    assert len(series.timestamps) == 48
    assert series.timestamps[-1] == np.datetime64("2018-01-01T23:30:00")
    assert (np.diff(series.timestamps) == np.timedelta64(30, "m")).all()


def test_wrong_header_names_are_rejected(tmp_path):
    """A file whose header is not exactly 'datetime,price' is refused, not guessed at."""
    path = write_csv(tmp_path / "prices.csv", "timestamps,price", hourly_day_rows())

    with pytest.raises(ValueError):
        load_price_series(path, market_interval=timedelta(hours=1))


def test_a_header_only_file_is_rejected(tmp_path):
    """A file with a valid header but no rows is rejected with a clear error, not a crash."""
    path = write_csv(tmp_path / "prices.csv", "datetime,price", [])

    with pytest.raises(ValueError):
        load_price_series(path, market_interval=timedelta(hours=1))


@pytest.mark.parametrize("bad_price", ["", "abc"], ids=["blank", "non-numeric"])
def test_an_unusable_price_in_the_file_is_rejected(tmp_path, bad_price):
    """A blank or non-numeric price in the CSV fails loading rather than flowing through."""
    rows: list[tuple[str, float | str]] = list(hourly_day_rows())
    rows[3] = (rows[3][0], bad_price)
    path = write_csv(tmp_path / "prices.csv", "datetime,price", rows)

    with pytest.raises(ValueError):
        load_price_series(path, market_interval=timedelta(hours=1))


# --- Seam 1: PriceSeries validation --------------------------------------------------------


def test_a_blank_price_is_rejected():
    """A price series with a missing (NaN) price is rejected, not repaired (ADR 0002)."""
    prices = np.array(HOURLY_DAY_PRICES)
    prices[3] = np.nan

    with pytest.raises(ValueError):
        PriceSeries(prices, START, timedelta(hours=1))


def test_a_partial_day_is_rejected():
    """Prices must cover whole days (day-ahead assumption): 47 half-hours is a fault."""
    forty_seven_half_hours = np.zeros(47)

    with pytest.raises(ValueError):
        PriceSeries(forty_seven_half_hours, START, timedelta(minutes=30))


def test_a_market_interval_that_does_not_divide_a_day_is_rejected():
    """The interval itself must divide a day, even when the row count happens to fit."""
    prices = np.zeros(24)  # 24 x 7 h is a whole number of days, but 7 h does not divide 24 h

    with pytest.raises(ValueError):
        PriceSeries(prices, START, timedelta(hours=7))


def test_an_empty_series_is_rejected():
    """Zero prices is technically zero whole days, but is never a usable series."""
    with pytest.raises(ValueError):
        PriceSeries(np.array([]), START, timedelta(hours=1))


def test_a_sub_second_market_interval_is_rejected():
    """Timestamps are held to whole seconds; a finer interval would silently repeat them."""
    with pytest.raises(ValueError):
        PriceSeries(np.zeros(172_800), START, timedelta(milliseconds=500))  # exactly one day


@pytest.mark.parametrize("interval", [timedelta(0), timedelta(hours=-1)], ids=["zero", "negative"])
def test_a_zero_or_negative_market_interval_is_rejected(interval):
    """An interval must move time forward; zero or negative would build a degenerate grid."""
    with pytest.raises(ValueError):
        PriceSeries(np.zeros(24), START, interval)
