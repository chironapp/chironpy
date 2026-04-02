# API Reference: `WorkoutData`

The `WorkoutData` class is a core component of `chironpy`, designed to represent a standardized, time-indexed activity data structure for endurance sports analysis. It wraps a pandas `DataFrame` and enforces a schema with fixed columns (like time, speed, power, etc.) while supporting additional optional fields. The class simplifies loading, resampling, and interpolating data from various file types (e.g. FIT, GPX, TCX, or Strava).

---

## `WorkoutData` Class

### Constructor

```python
WorkoutData(data: pd.DataFrame, start_time: datetime = None)
```

- **data**: A DataFrame indexed by datetime, sampled at 1Hz, with standard columns like `speed`, `power`, `heart_rate`, `latitude`, `longitude`, etc.
- **start_time**: Optional `datetime` representing the start of the activity. If not provided, it is inferred.

---

## Core Properties

### `data`

Returns the underlying 1Hz DataFrame of the workout.

### `start_time`

Returns the start time of the workout.

---

## Class Methods

### `from_file(path: str) -> WorkoutData`

Load a workout from a `.fit`, `.gpx` or `.tcx` file or locally saved Strava streams as a `.json` file.

### `from_strava(activity_id: str, client) -> WorkoutData`

Load a workout from Strava using its API client.

### `merge_many(workouts, resample=True, interpolate=False) -> WorkoutData`

Merge a list of `WorkoutData` instances into a single continuous `WorkoutData` object.

Workouts are automatically sorted by their start timestamp before merging. The merged result uses the earliest start time as `t=0` and the `time` column reflects **real elapsed seconds**, including any time gaps between workouts. During the gap, all data columns (`speed`, `heartrate`, `power`, etc.) are `NaN`.

If two workouts overlap in time, the **later workout's** data takes precedence for the overlapping timestamps.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `workouts` | `list[WorkoutData]` | — | Workout objects to merge. Must be non-empty. |
| `resample` | `bool` | `True` | Resample the merged result to 1 Hz. |
| `interpolate` | `bool` | `False` | Linearly interpolate `NaN` values after resampling. Set to `True` to bridge the gap between workouts. |

**Raises** `ValueError` if `workouts` is an empty list.

**Example:**

```python
from chironpy import WorkoutData

warmup = WorkoutData.from_file("warmup.fit")
main   = WorkoutData.from_file("main.fit")
cooldown = WorkoutData.from_file("cooldown.fit")

merged = WorkoutData.merge_many([warmup, main, cooldown])
# merged.time starts at 0 and reflects real elapsed time including gaps.
# Data columns are NaN during the gaps (interpolate=False by default).
```

---

### `merge(other, **kwargs) -> WorkoutData`

Convenience instance method that merges this workout with `other`. Equivalent to calling `WorkoutData.merge_many([self, other], **kwargs)`.

**Example:**

```python
warmup = WorkoutData.from_file("warmup.fit")
main   = WorkoutData.from_file("main.fit")

merged = warmup.merge(main)
```

---

## Instance Methods

### `to_pandas() -> pd.DataFrame`

Returns a copy of the internal DataFrame.

### `resample(freq: str) -> WorkoutData`

Returns a new `WorkoutData` object resampled at the specified frequency (e.g. `'5S'` for 5 seconds).

### `rolling(window: int, method: str = "mean") -> pd.DataFrame`

Computes a rolling average or median across standard columns.

- **window**: Number of seconds in the rolling window.
- **method**: `"mean"` or `"median"`.

---

## Standard Columns

- `speed` (float): in m/s
- `power` (float): in Watts
- `heartrate` (int): in bpm
- `cadence` (int): in rpm
- `latitude` / `longitude` (float): GPS coordinates
- `elevation` (float): in meters
- `is_moving` (bool): inferred movement status
- `distance` (float): cumulative distance in meters
- `time` (int): relative workout duration in seconds
- `slope` (float): the grade of the sample elevation/distance

---

## Usage Example

```python
from chironpy import WorkoutData

data = WorkoutData.from_file("example.fit")
summary = workout.rolling(window=10, method="mean")
summary.plot(y=["speed", "power", "heart_rate"])
```
