# Data loading

_chironpy_ has built-in support for loading these activity file formats:

- [FIT files](#helper-functions)
- [GPX files](#helper-functions)
- [TCX files](#helper-functions)

...and loading data from these services:

- [Strava](#strava)

`WorkoutData` helper functions:

- [`from_file()`](#helper-functions), that automatically determines the file format.
- [`from_strava()`](#helper-functions), that iterates over all the files in a directory.

Usage:

```python
from chironpy import WorkoutData, examples


data = WorkoutData.from_file("path/to/file.fit")

example_fit = examples(path="4078723797.fit")
example_data = WorkoutData.from_file(example_fit.path)
```

## Strava

The `WorkoutData.from_strava()` function can be used to pull data from Strava.
chiron assumes you already have an API access token. Read more about that [here](http://developers.strava.com/docs/authentication/).
If you are looking for a Python library that helps you with Strava API authentication, take a look at [stravalib](https://github.com/hozn/stravalib/) or [stravaio](https://github.com/sladkovm/stravaio).
`read_strava()` returns a [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) with column names matching _chironpy_ [nomenclature](nomenclature.md).

Usage:

```python
from chironpy import WorkoutData

data = WorkoutData.from_strava(activity_id=1234567890, access_token="some access token")
```

## Helper functions

`from_file()` works exactly as the other [legacy sweatpy](../legacy/data_loading.md) `read_*()` functions but tries to automatically determine the file format.
It raises a `ValueError` when the file format cannot be determined or is not supported.
Please note that the `from_file()` does not support passing file-like objects.

Example:

```python
import chironpy


example_tcx = chironpy.examples(path="3173437224.tcx")

data = chironpy.read_file(example_tcx.path)
```

`read_dir()` allows you to read all the files in a directory and iterate over them.
It uses `read_file()` under the hood and returns a generator.
Please note that `read_dir()` expects **all** the files in the directory to be of a supported file format.

Example:

```python
from pathlib import Path

import chironpy


directory = Path("path/to/some/dir/")

for activity in chironpy.read_dir(directory):
    # Do things with the activities
```

## Resampling

All `read_*()` functions accept a `resample` and `interpolate` argument (both `False` by default) that can trigger a resampling to 1Hz and subsequent linear interpolation of the data for files that are not sampled (consistently) at 1Hz, as some Garmin devices with "smart recording mode" do.

```python
import chironpy


example_tcx = chironpy.examples(path="3173437224.tcx")

data = chironpy.read_tcx(example_tcx.path, resample=True, interpolate=True)
```
