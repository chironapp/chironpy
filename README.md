![chironpy](docs/img/chironpy-release-cover.jpg)

[![PyPI](https://img.shields.io/pypi/v/chironpy?style=flat-square)](https://pypi.org/project/chironpy/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/chironpy?style=flat-square)](https://pypi.org/project/chironpy/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/chironpy?style=flat-square)](https://pypi.org/project/chironpy/)
[![Tests](https://github.com/chironapp/chironpy/actions/workflows/test.yml/badge.svg)](https://github.com/chironapp/chironpy/actions/workflows/test.yml)
[![Documentation](https://img.shields.io/badge/docs-chironpy.chironapp.com-purple?style=flat-square)](https://chironpy.chironapp.com)

# chironpy

**chironpy** is a Python library for analysing endurance sports data. Load workouts from `.fit`, `.gpx`, `.tcx`, or the Strava API and analyse them with a familiar pandas-based interface — compute best intervals, elevation gain, speed, power, and more.

## Installation

```bash
# with uv (recommended)
uv add chironpy

# with pip
pip install chironpy
```

## Quickstart

```python
from chironpy import WorkoutData

# Load a workout file
data = WorkoutData.from_file("my_workout.fit")

# Best efforts — time-based and distance-based
data.best_intervals([60, 300, 1200], stream="power")
data.fastest_distance_intervals([1000, 5000, 10000])

# Elevation gain
data.elevation_gain()

# Resample to 10-second buckets
data.resample_records("10s")
```

## Key features

- **Multi-format loading** — `.fit`, `.gpx`, `.tcx`, and Strava activity streams
- **pandas-native** — `WorkoutData` subclasses `pd.DataFrame`; use any pandas method directly
- **Standardised columns** — `speed`, `power`, `heartrate`, `cadence`, `elevation`, `distance`, `latitude`, `longitude` regardless of source format
- **Best intervals** — time-based and distance-based personal bests
- **Elevation analysis** — gain, smoothed elevation, grade
- **Resampling** — downsample to any frequency with semantically correct per-column aggregations

## Documentation

Full documentation at [chironpy.chironapp.com](https://chironpy.chironapp.com)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Attribution

chironpy is a maintained fork of [sweatpy](https://github.com/GoldenCheetah/sweatpy) by [Maksym Sladkov](https://github.com/sladkovm) and [Aart Goossens](https://github.com/AartGoossens). The original project focused on cycling analysis; chironpy extends it with an emphasis on long-distance running.

With thanks to [Aaron Schroeder](https://github.com/aaron-schroeder) for work on running power and elevation metrics in [heartandsole](https://github.com/aaron-schroeder/heartandsole) and [spatialfriend](https://github.com/aaron-schroeder/spatialfriend).

## License

[MIT](docs/LICENSE)
