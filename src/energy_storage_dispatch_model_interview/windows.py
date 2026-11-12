from dataclasses import dataclass


@dataclass(frozen=True)
class Window:
    """One foresight window, as half-open positions in a price series.

    The dispatch for [first, committed_stop) is kept; the positions from committed_stop up to
    stop are lookahead.
    """

    first: int
    committed_stop: int
    stop: int


def rolling_windows(
    total_intervals: int, committed_intervals: int, lookahead_intervals: int
) -> list[Window]:
    """Split a series into windows that each keep `committed_intervals` and also see
    `lookahead_intervals` beyond them.

    Each window starts where the previous committed period ended, so the committed periods
    tile the series with no gap or overlap; only the lookahead overlaps the next window.
    Near the end of the series the windows are clipped to the series length.
    """
    if committed_intervals < 1:
        raise ValueError(
            f"The committed period must be at least one interval, got {committed_intervals}"
        )
    windows = []
    for first in range(0, total_intervals, committed_intervals):
        committed_stop = min(first + committed_intervals, total_intervals)
        stop = min(committed_stop + lookahead_intervals, total_intervals)
        windows.append(Window(first, committed_stop, stop))
    return windows
