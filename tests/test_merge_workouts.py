"""Integration tests for WorkoutData.merge_many() / merge() using the
three-part Strava session example files, mirroring the steps in
lab/merge_workouts.ipynb.
"""

import pandas as pd
import pytest

import chironpy
from chironpy.models.workout import WorkoutData


# ---------------------------------------------------------------------------
# Known start times for the three example activities
# ---------------------------------------------------------------------------

WARM_UP_START = pd.Timestamp("2026-02-23T18:45:34")
TRACK_START = pd.Timestamp("2026-02-23T19:27:33")
WARM_DOWN_START = pd.Timestamp("2026-02-23T19:48:10")


# ---------------------------------------------------------------------------
# Module-scoped fixtures — load once for the whole test module
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def workout_a():
    example = chironpy.examples(path="strava_17497731832_warm_up.json")
    return WorkoutData.from_file(example).set_start_time(WARM_UP_START)


@pytest.fixture(scope="module")
def workout_b():
    example = chironpy.examples(path="strava_17497955000_track_workout.json")
    return WorkoutData.from_file(example).set_start_time(TRACK_START)


@pytest.fixture(scope="module")
def workout_c():
    example = chironpy.examples(path="strava_17498168651_warm_down.json")
    return WorkoutData.from_file(example).set_start_time(WARM_DOWN_START)


@pytest.fixture(scope="module")
def merged(workout_a, workout_b, workout_c):
    return WorkoutData.merge_many([workout_a, workout_b, workout_c])


@pytest.fixture(scope="module")
def merged_no_gaps(workout_a, workout_b, workout_c):
    return WorkoutData.merge_many([workout_a, workout_b, workout_c], drop_gaps=True)


# ---------------------------------------------------------------------------
# Gap preservation — distance forward-filled; performance channels are NaN
# ---------------------------------------------------------------------------


def test_distance_forward_filled_during_gap(merged, workout_a, workout_b):
    """``distance`` is cumulative and must be forward-filled, not NaN, in gap rows."""
    gap_rows = merged.loc[
        workout_a.index[-1]
        + pd.Timedelta(seconds=1) : workout_b.index[0]
        - pd.Timedelta(seconds=1)
    ]
    assert not gap_rows.empty, "Expected resampled NaN rows in the gap"
    assert (
        not gap_rows["distance"].isna().any()
    ), "distance must be forward-filled (not NaN) during gap rows"


def test_speed_and_heartrate_nan_during_gap(merged, workout_a, workout_b):
    """Performance channels (speed, heartrate) must be NaN in gap rows."""
    gap_rows = merged.loc[
        workout_a.index[-1]
        + pd.Timedelta(seconds=1) : workout_b.index[0]
        - pd.Timedelta(seconds=1)
    ]
    assert not gap_rows.empty, "Expected resampled NaN rows in the gap"
    assert gap_rows["speed"].isna().all(), "speed must be NaN during gap rows"
    assert gap_rows["heartrate"].isna().all(), "heartrate must be NaN during gap rows"


# ---------------------------------------------------------------------------
# drop_gaps=True — no gap rows, contiguous timestamps, correct row count
# ---------------------------------------------------------------------------


def test_drop_gaps_produces_contiguous_timestamps(merged_no_gaps):
    """With ``drop_gaps=True`` every pair of consecutive timestamps is 1 second apart."""
    diffs = merged_no_gaps.index.to_series().diff().dropna()
    assert (
        diffs == pd.Timedelta(seconds=1)
    ).all(), (
        "With drop_gaps=True all consecutive timestamps must be exactly 1 second apart"
    )


def test_drop_gaps_row_count_equals_sum_of_sources(
    merged_no_gaps, workout_a, workout_b, workout_c
):
    """Row count with ``drop_gaps=True`` equals the sum of source workout row counts."""
    expected = len(workout_a) + len(workout_b) + len(workout_c)
    assert len(merged_no_gaps) == expected


# ---------------------------------------------------------------------------
# Ordering — workouts sorted by start time regardless of input order
# ---------------------------------------------------------------------------


def test_merge_ordering_regardless_of_input_order(
    merged, workout_a, workout_b, workout_c
):
    """Workouts are sorted by start timestamp regardless of the order passed in."""
    merged_reversed = WorkoutData.merge_many([workout_c, workout_b, workout_a])
    pd.testing.assert_frame_equal(
        pd.DataFrame(merged).reset_index(drop=True),
        pd.DataFrame(merged_reversed).reset_index(drop=True),
    )


# ---------------------------------------------------------------------------
# Overlap — later-starting workout overwrites clashing timestamps
# ---------------------------------------------------------------------------


def test_overlapping_later_workout_values_take_precedence(workout_a, workout_b):
    """When workouts overlap, values from the later-starting workout win.

    workout_b is artificially shifted to start 5 min before workout_a ends,
    creating a ~5-minute overlap window.  At a timestamp inside that window,
    the merged value must match workout_b's value (not workout_a's).
    No exception should be raised.
    """
    # Shift workout_b to start 5 min before workout_a ends -> creates overlap
    overlap_start = workout_a.index[-1] - pd.Timedelta(minutes=5)
    workout_b_overlapping = workout_b.set_start_time(overlap_start)

    # Must not raise
    merged = WorkoutData.merge_many([workout_a, workout_b_overlapping])

    # Sample 60 s into the overlap region — both workouts have data here,
    # but workout_b_overlapping starts later so its values must win.
    sample_ts = overlap_start + pd.Timedelta(seconds=60)
    assert (
        sample_ts in merged.index
    ), "Expected merged to contain a row at the sample timestamp"
    assert (
        sample_ts in workout_b_overlapping.index
    ), "Expected workout_b_overlapping to contain a row at the sample timestamp"
    assert merged.loc[sample_ts, "speed"] == pytest.approx(
        workout_b_overlapping.loc[sample_ts, "speed"]
    )
