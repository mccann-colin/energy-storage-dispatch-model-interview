from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

from energy_storage_dispatch_model_interview.price_series import PriceSeries, load_price_series

HOURLY_DAY_PRICES = [
    51.89, 55.49, 51.06, 44.76, 40.07, 44.42, 50.295, 52.145,
    48.33, 44.595, 44.37, 46.1, 47.2, 45.9, 43.3, 44.8,
    52.6, 61.5, 75.2, 80.1, 70.4, 60.3, 55.5, 50.0,
]


def write_csv(path: Path, header: str, rows: list[tuple[str, float]]) -> Path:
    lines = [header] + [f"{label},{price}" for label, price in rows]
    path.write_text("\n".join(lines) + "\n")
    return path


def hourly_day_rows() -> list[tuple[str, float]]:
    return [(f"2018-01-01 {hour:02d}:00:00.000", price) for hour, price in enumerate(HOURLY_DAY_PRICES)]


def test_known_file_contents_are_read_correctly(tmp_path):
    path = write_csv(tmp_path / "prices.csv", "datetime,price", hourly_day_rows())

    series = load_price_series(path, market_interval=timedelta(hours=1))

    np.testing.assert_allclose(series.prices, HOURLY_DAY_PRICES)
    assert series.start == datetime(2018, 1, 1, 0, 0)


def test_time_steps_are_regular_whatever_the_source_labels_say(tmp_path):
    rows = hourly_day_rows()
    rows[5] = ("2018-01-01 04:00:00.000", rows[5][1])  # duplicate label
    rows[9] = ("2018-01-01 08:59:59.994", rows[9][1])  # float-storage artefact
    path = write_csv(tmp_path / "prices.csv", "datetime,price", rows)

    series = load_price_series(path, market_interval=timedelta(hours=1))

    timestamps = series.timestamps
    assert len(timestamps) == 24
    assert timestamps[0] == np.datetime64("2018-01-01T00:00:00")
    assert timestamps[-1] == np.datetime64("2018-01-01T23:00:00")
    assert (np.diff(timestamps) == np.timedelta64(1, "h")).all()


def test_time_steps_other_than_one_hour_are_read_correctly(tmp_path):
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
    path = write_csv(tmp_path / "prices.csv", "timestamps,price", hourly_day_rows())

    with pytest.raises(ValueError):
        load_price_series(path, market_interval=timedelta(hours=1))


START = datetime(2018, 1, 1)


def test_a_blank_price_is_rejected():
    prices = np.array(HOURLY_DAY_PRICES)
    prices[3] = np.nan

    with pytest.raises(ValueError):
        PriceSeries(prices, START, timedelta(hours=1))


def test_a_partial_day_is_rejected():
    forty_seven_half_hours = np.zeros(47)

    with pytest.raises(ValueError):
        PriceSeries(forty_seven_half_hours, START, timedelta(minutes=30))


def test_a_market_interval_that_does_not_divide_a_day_is_rejected():
    prices = np.zeros(24)  # 24 x 7 h is a whole number of days, but 7 h does not divide 24 h

    with pytest.raises(ValueError):
        PriceSeries(prices, START, timedelta(hours=7))


def test_an_empty_series_is_rejected():
    with pytest.raises(ValueError):
        PriceSeries(np.array([]), START, timedelta(hours=1))
