# TODO: write tests for WorkoutData
import numpy as np
import pandas as pd
import pytest
from datetime import datetime, timedelta

from chironpy.models.workout import WorkoutData


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_workout(
    start: datetime,
    duration_s: int,
    speed: float = 3.0,
    elevation_start: float = 100.0,
) -> WorkoutData:
    """Create a synthetic 1 Hz ``WorkoutData`` for testing."""
    times = pd.date_range(start=start, periods=duration_s, freq="1s")
    df = pd.DataFrame(
        {
            "speed": [speed] * duration_s,
            "elevation": [elevation_start + i * 0.1 for i in range(duration_s)],
            "distance": [speed * i for i in range(duration_s)],
            "heartrate": [140] * duration_s,
        },
        index=times,
    )
    return WorkoutData.from_raw(df, resample=False, interpolate=False)


# ---------------------------------------------------------------------------
# merge_many – basic error handling
# ---------------------------------------------------------------------------

def test_merge_many_empty_raises():
    with pytest.raises(ValueError, match="No workouts to merge"):
        WorkoutData.merge_many([])


# ---------------------------------------------------------------------------
# merge_many – gap preservation
# ---------------------------------------------------------------------------

def test_merge_two_time_at_second_workout_start():
    """``time`` at the first sample of the second workout equals gap + duration_of_first."""
    start1 = datetime(2023, 1, 1, 10, 0, 0)
    duration1 = 1800  # 30 min
    gap = 1800        # 30 min gap
    start2 = start1 + timedelta(seconds=duration1 + gap)
    duration2 = 1800  # 30 min

    w1 = make_workout(start1, duration1)
    w2 = make_workout(start2, duration2)

    merged = WorkoutData.merge_many([w1, w2], resample=True, interpolate=False)

    expected_time = duration1 + gap
    assert merged.loc[start2, "time"] == expected_time


def test_merge_two_total_time_span():
    """The maximum ``time`` value equals duration1 + gap + duration2 - 1."""
    start1 = datetime(2023, 1, 1, 10, 0, 0)
    duration1 = 1800
    gap = 1800
    start2 = start1 + timedelta(seconds=duration1 + gap)
    duration2 = 1800

    w1 = make_workout(start1, duration1)
    w2 = make_workout(start2, duration2)

    merged = WorkoutData.merge_many([w1, w2], resample=True, interpolate=False)

    # Inclusive range: last sample is at start1 + (duration1 + gap + duration2 - 1) s
    expected_max_time = duration1 + gap + duration2 - 1
    assert merged["time"].max() == expected_max_time


def test_merge_data_columns_nan_during_gap():
    """Data columns (speed, heartrate, …) are NaN during the inter-workout gap."""
    start1 = datetime(2023, 1, 1, 10, 0, 0)
    duration1 = 60
    gap = 60
    start2 = start1 + timedelta(seconds=duration1 + gap)
    duration2 = 60

    w1 = make_workout(start1, duration1)
    w2 = make_workout(start2, duration2)

    merged = WorkoutData.merge_many([w1, w2], resample=True, interpolate=False)

    # Timestamps strictly inside the gap (the gap is open: (end_of_w1, start_of_w2))
    gap_start = start1 + timedelta(seconds=duration1 + 1)
    gap_end = start2 - timedelta(seconds=1)
    gap_slice = merged.loc[gap_start:gap_end]

    assert not gap_slice.empty, "Expected gap rows to be present after resampling"
    assert gap_slice["speed"].isna().all()
    assert gap_slice["heartrate"].isna().all()


def test_merge_interpolate_fills_gap():
    """With ``interpolate=True`` the gap rows should not be NaN."""
    start1 = datetime(2023, 1, 1, 10, 0, 0)
    duration1 = 60
    gap = 60
    start2 = start1 + timedelta(seconds=duration1 + gap)
    duration2 = 60

    w1 = make_workout(start1, duration1)
    w2 = make_workout(start2, duration2)

    merged = WorkoutData.merge_many([w1, w2], resample=True, interpolate=True)

    gap_start = start1 + timedelta(seconds=duration1 + 1)
    gap_end = start2 - timedelta(seconds=1)
    gap_slice = merged.loc[gap_start:gap_end]

    assert not gap_slice["speed"].isna().any()


# ---------------------------------------------------------------------------
# merge_many – overlap behaviour
# ---------------------------------------------------------------------------

def test_merge_overlapping_keeps_later_workout():
    """For overlapping timestamps the later workout's values take precedence."""
    start1 = datetime(2023, 1, 1, 10, 0, 0)
    start2 = start1 + timedelta(seconds=30)  # starts 30 s into workout 1
    duration = 60

    w1 = make_workout(start1, duration, speed=1.0)
    w2 = make_workout(start2, duration, speed=5.0)

    merged = WorkoutData.merge_many([w1, w2], resample=False, interpolate=False)

    overlap_ts = start2 + timedelta(seconds=10)
    assert merged.loc[overlap_ts, "speed"] == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# merge_many – ordering with 3+ workouts
# ---------------------------------------------------------------------------

def test_merge_three_workouts_ordering():
    """Workouts are sorted by start timestamp regardless of input order."""
    start_a = datetime(2023, 1, 1, 10, 0, 0)
    start_b = start_a + timedelta(hours=1)
    start_c = start_a + timedelta(hours=2)
    duration = 300

    wa = make_workout(start_a, duration, speed=1.0)
    wb = make_workout(start_b, duration, speed=3.0)
    wc = make_workout(start_c, duration, speed=5.0)

    # Pass in reverse order
    merged = WorkoutData.merge_many([wc, wb, wa], resample=False, interpolate=False)

    assert merged.loc[start_a + timedelta(seconds=10), "speed"] == pytest.approx(1.0)
    assert merged.loc[start_b + timedelta(seconds=10), "speed"] == pytest.approx(3.0)
    assert merged.loc[start_c + timedelta(seconds=10), "speed"] == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# Downstream metrics on merged data
# ---------------------------------------------------------------------------

def test_merge_elevation_gain_no_error():
    """``elevation_gain()`` should run without error on a merged workout.

    When ``interpolate=True`` the gap rows are filled in, so the result is a
    valid non-negative number.
    """
    start1 = datetime(2023, 1, 1, 10, 0, 0)
    start2 = start1 + timedelta(hours=1)
    duration = 60

    w1 = make_workout(start1, duration)
    w2 = make_workout(start2, duration)

    merged = WorkoutData.merge_many([w1, w2], resample=True, interpolate=True)
    gain = merged.elevation_gain()
    assert gain >= 0


def test_merge_best_intervals_no_error():
    """``best_intervals()`` should run without error on a merged workout."""
    start1 = datetime(2023, 1, 1, 10, 0, 0)
    start2 = start1 + timedelta(hours=1)
    duration = 120

    w1 = make_workout(start1, duration)
    w2 = make_workout(start2, duration)

    merged = WorkoutData.merge_many([w1, w2], resample=True, interpolate=True)
    result = merged.best_intervals([60], stream="speed")
    assert len(result) == 1


# ---------------------------------------------------------------------------
# Instance method .merge()
# ---------------------------------------------------------------------------

def test_merge_instance_method_without_gap():
    """``w1.merge(w2)`` is equivalent to ``WorkoutData.merge_many([w1, w2])``."""
    start1 = datetime(2023, 1, 1, 10, 0, 0)
    start2 = start1 + timedelta(hours=1)
    duration = 60

    w1 = make_workout(start1, duration)
    w2 = make_workout(start2, duration)

    merged_classmethod = WorkoutData.merge_many([w1, w2], resample=False)
    merged_instance = w1.merge(w2, resample=False)

    pd.testing.assert_frame_equal(
        pd.DataFrame(merged_classmethod),
        pd.DataFrame(merged_instance),
    )


def test_merge_instance_method_passes_kwargs():
    """``interpolate`` kwarg is forwarded correctly through ``merge()``."""
    start1 = datetime(2023, 1, 1, 10, 0, 0)
    duration1 = 60
    gap = 30
    start2 = start1 + timedelta(seconds=duration1 + gap)
    duration2 = 60

    w1 = make_workout(start1, duration1)
    w2 = make_workout(start2, duration2)

    # With interpolate=False the gap rows must contain NaN
    merged = w1.merge(w2, resample=True, interpolate=False)
    gap_ts = start1 + timedelta(seconds=duration1 + 1)
    assert pd.isna(merged.loc[gap_ts, "speed"])

