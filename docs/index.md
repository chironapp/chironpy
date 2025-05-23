# chironpy

**Endurance sports analysis library for Python**

## Introduction

**chironpy** is a Python library designed for analyzing endurance sports data. It supports various file formats, including .fit, .gpx, .json and the Strava API, providing a standardized interface for processing and analyzing workout data.

The project is currently **very beta** state-features might be added, removed or changed in backwards incompatible ways. A stable version will be released when ready. Get in touch with the maintainers or create an issue if you have problems/questions/feature requests/special use cases.

> **This is a maintained fork of the original [sweatpy](https://github.com/GoldenCheetah/sweatpy) project, which no longer seems to be maintained.**

Documentation for the original project can be found [here](https://github.com/GoldenCheetah/sweatpy/blob/master/docs/docs/index.md). The original `sweatpy` functions were generally targeted at analysing cycling workouts, `chironpy` emphasizes long distance running, though there is plenty of overlap so `sweatpy` was a great starting point.

## Installation

This library can be installed from [PyPI](https://pypi.org/project/chironpy/):

```bash
pip install chironpy
```

## The `WorkoutData` Class

At the core of chironpy is the `WorkoutData` class. It provides a standardized structure for representing workouts and includes built-in methods for computing metrics, smoothing data, and extracting performance intervals.

### Key Features

- Standardized data structure from multiple supported file formats (e.g. `.fit`, `.gpx`) and the Strava API.
- Wraps the `pandas.DataFrame` so can be analysed and manipulated like a `df`.
- Standardized columns for `speed`, `power`, `heartrate`, `cadence`, etc. See supported columns in [nomenclature](features/nomenclature.md)
- Resamples actvity data at 1Hz by default for clean time-series analysis.
- Smoothing and bad data removal for clean time-series analysis.
- Built-in metric computations like best time or distance based intervals, elevation gain.

### Example

```python
from chironpy import WorkoutData

# Load workout from file
data = WorkoutData.from_file("path/to/file.fit")

# Compute elevation gain
gain = data.elevation_gain()

# Get best intervals (time-based intervals)
durations = [30, 60, 120, 180, 300, 600, 1200, 1800, 3600] # in seconds
max_hr = data.best_intervals(durations, "heartrate")

# Get best intervals (disatnce-based intervals)
distances = [1000, 5000, 10000, 21100] # in metres
max_hr_by_distance = data.best_distance_intervals(distances, "heartrate")
fastest = data.fastest_distance_intervals(distances)

```

More information about running metrics can be found [here](features/running_metrics.md).

The data frames that are returned by chironpy `WorkoutData` when loading files is similar for different file types. Read more about this standardization [here](features/nomenclature.md).

## The `Workout` class (FUTURE)

A future release will introduce a top-level `Workout` class. The `WorkoutData` class shall be provided as an attribute of new class. The `Workout` class extends workout data with context such as athlete data (ie training zones, threshold) to provide and other handy features.

```python
from chironpy import Workout, Athlete

workout = Workout.from_file("path/to/file.fit")
data = workout.data # this is the WorkoutData object

# Example usage
workout.sport
workout.create_athlete(Athlete(name="Clive Gross"))
workout.athlete # this is the Athlete object
workout.laps # this is a Laps object (pandas.DataFrame)
workout.time_in_zones
workout.data['power'] # Skiba running power
workout.stress_score

```

## Legacy Support

The original `sweatpy` data and analysis functions are still supported. See:

- [Legacy Data Loading](legacy/data_loading.md)
- [Legacy Power Analysis](legacy/Power%20duration%20modelling.ipynb)

loading functions and
chironpy supports loading .fit, .tcx and .gpx files. To load a .fit file:

## Contributing

See [contributing](contributing.md).

## Contributors

- [Clive Gross](https://github.com/clivegross)
- [Chiron - The endurance training platform](https://github.com/chironapp)

Original authors ([sweatpy](https://github.com/GoldenCheetah/sweatpy)):

- [Maksym Sladkov](https://github.com/sladkovm) - Original author (sweatpy)
- [Aart Goossens](https://github.com/AartGoossens) - Original author (sweatpy)

With thanks to:

- [Aaron Schroeder](https://github.com/aaron-schroeder) for work on running power and elevation metrics published in [heartandsole](https://github.com/aaron-schroeder/heartandsole) and [spatialfriend](https://github.com/aaron-schroeder/spatialfriend).

## Changelog

See [CHANGELOG.md](changelog.md) for a full list of changes and version history.

## License

See [LICENSE](LICENSE) file.
