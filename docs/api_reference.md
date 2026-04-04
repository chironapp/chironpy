# API Reference: `WorkoutData`

`WorkoutData` is the core class in `chironpy`. It subclasses `pandas.DataFrame` and represents a standardised, 1 Hz datetime-indexed activity. All standard DataFrame operations work on it directly. The class handles loading from various file formats, column normalisation, resampling, and merging of multi-file sessions.

---

## `WorkoutData` Class

`WorkoutData` is a `pd.DataFrame` subclass. Use the class methods below to construct instances — do not instantiate directly.

---

## Properties

### `standard_columns`

Returns a list of column names that belong to the chironpy schema (see [Standard Columns](#standard-columns) below).

```python
workout.standard_columns  # e.g. ['speed', 'heartrate', 'distance', 'time', ...]
```

### `extra_columns`

Returns a list of column names that are present in the DataFrame but are not part of the standard schema.

```python
workout.extra_columns  # e.g. ['left_right_balance', 'some_device_field']
```

---

## Class Methods

### `from_file(filepath, resample=True, interpolate=True) -> WorkoutData`

Load a workout from a file. Supported formats: `.fit`, `.gpx`, `.tcx`, and locally-saved Strava activity streams (`.json`).

| Parameter     | Type            | Default | Description                                           |
| ------------- | --------------- | ------- | ----------------------------------------------------- |
| `filepath`    | `str` or `Path` | —       | Path to the workout file.                             |
| `resample`    | `bool`          | `True`  | Resample data to 1 Hz.                                |
| `interpolate` | `bool`          | `True`  | Linearly interpolate missing values after resampling. |

```python
workout = WorkoutData.from_file("morning_run.fit")
```

---

### `from_strava(activity_id, access_token, refresh_token=None, client_id=None, client_secret=None, resample=True, interpolate=True) -> WorkoutData`

Load a workout by fetching activity streams from the Strava API.

| Parameter       | Type   | Default | Description                                                           |
| --------------- | ------ | ------- | --------------------------------------------------------------------- |
| `activity_id`   | `int`  | —       | Strava activity ID.                                                   |
| `access_token`  | `str`  | —       | OAuth access token.                                                   |
| `refresh_token` | `str`  | `None`  | OAuth refresh token (used to obtain a new access token when expired). |
| `client_id`     | `int`  | `None`  | Strava API client ID (required when `refresh_token` is provided).     |
| `client_secret` | `str`  | `None`  | Strava API client secret (required when `refresh_token` is provided). |
| `resample`      | `bool` | `True`  | Resample data to 1 Hz.                                                |
| `interpolate`   | `bool` | `True`  | Linearly interpolate missing values after resampling.                 |

```python
workout = WorkoutData.from_strava(activity_id=12345678, access_token="...")
```

---

### `from_raw(df, resample=True, interpolate=True) -> WorkoutData`

Construct a `WorkoutData` from an existing `pd.DataFrame`. Normalises column names (e.g. `enhanced_speed` → `speed`), optionally resamples to 1 Hz, adds the `time`, `is_moving`, and `grade` columns, and sets the index name to `datetime`.

Use this when you have a DataFrame from another source and want to convert it into the standard schema.

| Parameter     | Type           | Default | Description                                           |
| ------------- | -------------- | ------- | ----------------------------------------------------- |
| `df`          | `pd.DataFrame` | —       | Source DataFrame with a `DatetimeIndex`.              |
| `resample`    | `bool`         | `True`  | Resample data to 1 Hz.                                |
| `interpolate` | `bool`         | `True`  | Linearly interpolate missing values after resampling. |

```python
workout = WorkoutData.from_raw(my_df, resample=False)
```

### `merge_many(workouts, resample=True, interpolate=False, drop_gaps=False) -> WorkoutData`

Merge a list of `WorkoutData` instances into a single continuous `WorkoutData` object.

Workouts are automatically sorted by their start timestamp before merging. The merged result uses the earliest start time as `t=0` and the `time` column reflects **real elapsed seconds**, including any time gaps between workouts. During a gap, performance data columns (`speed`, `heartrate`, `power`, etc.) are `NaN`, while `distance` is forward-filled (it is a cumulative metric that should not reset to `NaN` during rest).

If two workouts overlap in time, the **later workout's** data takes precedence for the overlapping timestamps.

| Parameter     | Type                | Default | Description                                                                                                                                                                                                  |
| ------------- | ------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `workouts`    | `list[WorkoutData]` | —       | Workout objects to merge. Must be non-empty.                                                                                                                                                                 |
| `resample`    | `bool`              | `True`  | Resample the merged result to 1 Hz.                                                                                                                                                                          |
| `interpolate` | `bool`              | `False` | Linearly interpolate `NaN` values after resampling. Set to `True` to bridge the gap between workouts.                                                                                                        |
| `drop_gaps`   | `bool`              | `False` | When `True`, each workout is shifted to start immediately after the previous one ends (1 second later), so no gap rows are produced. The `time` column reflects condensed elapsed time with no rest periods. |

**Raises** `ValueError` if `workouts` is an empty list.

**Example:**

```python
from chironpy import WorkoutData

warmup   = WorkoutData.from_file("warmup.fit")
main     = WorkoutData.from_file("main.fit")
cooldown = WorkoutData.from_file("cooldown.fit")

# Preserve real-time gaps (default)
merged = WorkoutData.merge_many([warmup, main, cooldown])
# merged.time starts at 0 and reflects real elapsed time including gaps.
# Performance columns are NaN during the gaps; distance is forward-filled.

# Remove gaps — workouts are stitched back-to-back
merged_no_gaps = WorkoutData.merge_many([warmup, main, cooldown], drop_gaps=True)
```

---

### `merge(other, resample=True, interpolate=False, drop_gaps=False) -> WorkoutData`

Convenience instance method that merges this workout with `other`. Equivalent to calling `WorkoutData.merge_many([self, other], ...)`. All parameters are forwarded to `merge_many()`.

**Example:**

```python
warmup = WorkoutData.from_file("warmup.fit")
main   = WorkoutData.from_file("main.fit")

# Preserve the real-time gap between the two workouts
merged = warmup.merge(main)

# Stitch them back-to-back with no gap rows
merged_no_gaps = warmup.merge(main, drop_gaps=True)
```

---

### `set_start_time(start_time: pd.Timestamp) -> WorkoutData`

Shift the workout's datetime index so it begins at `start_time`. All timestamps are shifted by the same offset, preserving the relative spacing between records. The `time` column (seconds since start) is recomputed from the new index.

This is particularly useful for Strava activity streams, which are indexed from `t=0` and do not carry an absolute start timestamp.

| Parameter    | Type           | Description                             |
| ------------ | -------------- | --------------------------------------- |
| `start_time` | `pd.Timestamp` | The new start datetime for the workout. |

**Returns** a new `WorkoutData` with the shifted index; the original is unchanged.

**Example:**

```python
import pandas as pd
from chironpy import WorkoutData

warmup = WorkoutData.from_file("warmup.json")  # Strava stream — index starts at 0
warmup = warmup.set_start_time(pd.Timestamp("2025-06-01T08:45:00"))

# Now the index reflects real wall-clock time and can be merged with
# other workouts that also have absolute timestamps.
merged = WorkoutData.merge_many([warmup, main, cooldown])
```

---

## Instance Methods

### `to_pandas() -> pd.DataFrame`

Return a plain `pd.DataFrame` copy of the workout, stripping the `WorkoutData` subclass. Useful when passing data to libraries that check `type(x) is pd.DataFrame`.

```python
df = workout.to_pandas()
```

---

### `resample(freq, interpolate=False) -> WorkoutData`

Return a new `WorkoutData` resampled to the given frequency. When downsampling (e.g. to 5 s), values are averaged within each bin; `time`, `is_moving`, and `grade` are recomputed from the new index.

| Parameter     | Type   | Default | Description                                         |
| ------------- | ------ | ------- | --------------------------------------------------- |
| `freq`        | `str`  | —       | Pandas offset alias, e.g. `"5s"`, `"1min"`.         |
| `interpolate` | `bool` | `False` | Linearly interpolate `NaN` values after resampling. |

```python
smoothed = workout.resample("5s")
```

---

### `rolling(window, method="mean") -> pd.DataFrame`

Compute a rolling average or median across all standard columns. Wraps `pandas.DataFrame.rolling` applied to `workout.standard_columns`.

| Parameter | Type  | Default  | Description                                   |
| --------- | ----- | -------- | --------------------------------------------- |
| `window`  | `int` | —        | Rolling window size in seconds.               |
| `method`  | `str` | `"mean"` | Aggregation to apply: `"mean"` or `"median"`. |

**Raises** `ValueError` if `method` is not `"mean"` or `"median"`.

```python
smoothed = workout.rolling(30, method="mean")
smoothed.plot(y="speed")
```

---

### `best_intervals(windows, stream="speed") -> list[dict]`

Find the best (highest mean) contiguous intervals over one or more **time** windows.

| Parameter | Type                     | Default   | Description                                                    |
| --------- | ------------------------ | --------- | -------------------------------------------------------------- |
| `windows` | `float` or `list[float]` | —         | Window length(s) in seconds.                                   |
| `stream`  | `str`                    | `"speed"` | Column to optimise (e.g. `"speed"`, `"heartrate"`, `"power"`). |

Returns a list of dicts, one per window, each with `value`, `start_index`, and `stop_index`.

```python
# Best 60 s and 300 s power intervals
results = workout.best_intervals([60, 300], stream="power")
```

---

### `best_distance_intervals(windows, stream="speed", distance_col="distance") -> list[dict]`

Find the best (highest mean) contiguous intervals over one or more **distance** windows.

| Parameter      | Type                     | Default      | Description                 |
| -------------- | ------------------------ | ------------ | --------------------------- |
| `windows`      | `float` or `list[float]` | —            | Window length(s) in metres. |
| `stream`       | `str`                    | `"speed"`    | Column to optimise.         |
| `distance_col` | `str`                    | `"distance"` | Cumulative distance column. |

```python
results = workout.best_distance_intervals([1000, 5000], stream="speed")
```

---

### `fastest_distance_intervals(windows, distance_col="distance") -> list[dict]`

Find the fastest (shortest elapsed time) contiguous intervals over one or more **distance** windows.

| Parameter      | Type                     | Default      | Description                 |
| -------------- | ------------------------ | ------------ | --------------------------- |
| `windows`      | `float` or `list[float]` | —            | Window length(s) in metres. |
| `distance_col` | `str`                    | `"distance"` | Cumulative distance column. |

```python
results = workout.fastest_distance_intervals([1000, 5000])
```

---

### `elevation_gain(elevation_col="elevation") -> float`

Compute total elevation gain in metres.

| Parameter       | Type  | Default       | Description                   |
| --------------- | ----- | ------------- | ----------------------------- |
| `elevation_col` | `str` | `"elevation"` | Name of the elevation column. |

```python
gain = workout.elevation_gain()
```

---

### `mean_max(columns, monotonic=False) -> pd.DataFrame`

Compute the mean-max (power-duration) curve for one or more columns. Returns the highest achievable mean value for every possible window duration from 1 second to the full workout length.

| Parameter   | Type                 | Default | Description                                                                   |
| ----------- | -------------------- | ------- | ----------------------------------------------------------------------------- |
| `columns`   | `str` or `list[str]` | —       | Column(s) to compute mean-max for (e.g. `"speed"`, `["speed", "heartrate"]`). |
| `monotonic` | `bool`               | `False` | Enforce a monotonically decreasing curve.                                     |

Returns a `pd.DataFrame` with a `TimedeltaIndex` (duration axis) and one `mean_max_{column}` column per requested stream.

```python
# Single column
mms = workout.mean_max("speed")

# Multiple columns
mm = workout.mean_max(["speed", "heartrate"])
mm["mean_max_heartrate"].plot(title="Mean Max Heart Rate")
```

---

## Standard Columns

These columns are part of the chironpy schema. `standard_columns` returns those present in a given workout.

| Column                   | Type    | Unit    | Notes                                                                                                                 |
| ------------------------ | ------- | ------- | --------------------------------------------------------------------------------------------------------------------- |
| `time`                   | `int`   | seconds | Elapsed seconds since workout start (always present after `from_raw`).                                                |
| `speed`                  | `float` | m/s     | Normalised from device-specific names (`enhanced_speed`, `velocity_smooth`).                                          |
| `power`                  | `float` | Watts   |                                                                                                                       |
| `heartrate`              | `int`   | bpm     |                                                                                                                       |
| `cadence`                | `int`   | rpm     |                                                                                                                       |
| `distance`               | `float` | metres  | Cumulative. Forward-filled across gap rows in merged workouts.                                                        |
| `elevation`              | `float` | metres  | Normalised from `enhanced_altitude`, `altitude`.                                                                      |
| `latitude` / `longitude` | `float` | degrees | GPS coordinates.                                                                                                      |
| `temperature`            | `float` | °C      | Normalised from `temp`.                                                                                               |
| `grade`                  | `float` | —       | Smoothed gradient, computed from `distance` and `elevation` if not present in source. Normalised from `grade_smooth`. |
| `is_moving`              | `bool`  | —       | `True` when `speed > 0.5 m/s`. Added automatically by `from_raw`.                                                     |

---

## Usage Example

```python
import pandas as pd
from chironpy import WorkoutData

# Load a single file
workout = WorkoutData.from_file("morning_run.fit")

# Best 1 km and 5 km intervals by speed
results = workout.fastest_distance_intervals([1000, 5000])

# Merge a three-part session
warmup   = WorkoutData.from_file("warmup.json").set_start_time(pd.Timestamp("2025-06-01T08:45:00"))
main     = WorkoutData.from_file("main.json").set_start_time(pd.Timestamp("2025-06-01T09:10:00"))
cooldown = WorkoutData.from_file("cooldown.json").set_start_time(pd.Timestamp("2025-06-01T09:55:00"))

merged = WorkoutData.merge_many([warmup, main, cooldown])
print(merged.elevation_gain())
```
