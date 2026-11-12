import pytest

from energy_storage_dispatch_model_interview.windows import Window, rolling_windows


def test_windows_tile_the_series_each_with_its_lookahead():
    """The committed ranges abut and cover the series exactly. Each window also sees its
    lookahead, except where the series ends: there the last window is shorter and its
    lookahead is clipped."""
    windows = rolling_windows(total_intervals=10, committed_intervals=4, lookahead_intervals=2)

    assert windows == [Window(0, 4, 6), Window(4, 8, 10), Window(8, 10, 10)]


@pytest.mark.parametrize("committed_intervals", [0, -1], ids=["zero", "negative"])
def test_a_committed_period_below_one_interval_is_refused(committed_intervals):
    """The window start advances by the committed period, so anything below one interval would
    never move forward (or move backwards); it is refused rather than looping or returning
    nothing."""
    with pytest.raises(ValueError, match="committed"):
        rolling_windows(total_intervals=10, committed_intervals=committed_intervals,
                        lookahead_intervals=2)
