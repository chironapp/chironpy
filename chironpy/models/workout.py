from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel
import pandas as pd
from typing import Union, Optional
from chironpy import read_file, read_strava
from chironpy.metrics.vert import grade_smooth_time, elevation_gain
from chironpy.metrics.speed import multiple_fastest_distance_intervals
from chironpy.metrics.core import (
    multiple_best_distance_intervals,
    multiple_best_intervals,
)
from chironpy.constants import DataTypeEnum, DataTypeEnumExtended

DATA_TYPES = {member.value for member in DataTypeEnum} | {
    member.value for member in DataTypeEnumExtended
}


class WorkoutData(pd.DataFrame):
    @classmethod
    def from_file(
        cls, filepath, resample: bool = True, interpolate: bool = True
    ) -> "WorkoutData":
        if hasattr(filepath, "path"):
            filepath = filepath.path
        df = read_file(filepath, resample=False, interpolate=False)
        return cls.from_raw(df, resample=resample, interpolate=interpolate)

    @classmethod
    def from_strava(
        cls,
        activity_id: int,
        access_token: str,
        refresh_token: Optional[str] = None,
        client_id: Optional[int] = None,
        client_secret: Optional[str] = None,
        resample: bool = True,
        interpolate: bool = True,
    ) -> "WorkoutData":
        df = read_strava(
            activity_id=activity_id,
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            resample=False,
            interpolate=False,
        )
        return cls.from_raw(df, resample=resample, interpolate=interpolate)

    @classmethod
    def from_raw(
        cls, df: pd.DataFrame, resample: bool = True, interpolate: bool = True
    ) -> "WorkoutData":
        df = df.copy()
        df = cls._normalize_columns(df)
        if resample:
            df = cls._resample(df, interpolate=interpolate)
        # Add DATA_TYPES.time column: integer seconds since workout start
        if isinstance(df.index, pd.DatetimeIndex):
            start_time = df.index[0]
            df[(DataTypeEnum.time if hasattr(DataTypeEnum, "time") else "time")] = (
                (df.index - start_time).total_seconds().astype(int)
            )
            # rename index from 'time' to 'datetime'
            df.index.name = "datetime"
        # Add is_moving column if speed exists
        if "speed" in df.columns:
            # Consider moving if speed > 0.5 m/s (adjust threshold as needed)
            # TODO: add a parameter to set the threshold
            # TODO: consider a rolling window to account for GPS errors
            df["is_moving"] = df["speed"] > 0.5
        # Add grade column if missing and distance & elevation exist
        if (
            "grade" not in df.columns
            and "distance" in df.columns
            and "elevation" in df.columns
        ):
            try:
                df["grade"] = grade_smooth_time(
                    df["distance"].values, df["elevation"].values
                )
            except ImportError:
                pass  # grade_smooth_time not available
        return cls(df)

    @staticmethod
    def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        rename_map = {
            "enhanced_speed": "speed",
            "enhanced_altitude": "elevation",
            "altitude": "elevation",
            "velocity_smooth": "speed",
            "watts": "power",
            "temp": "temperature",
            "grade_smooth": "grade",
        }
        for src, dst in rename_map.items():
            if dst not in df.columns and src in df.columns:
                df[dst] = df[src]
                df.drop(columns=[src], inplace=True)
        return df

    @staticmethod
    def _resample(df: pd.DataFrame, interpolate: bool = True) -> pd.DataFrame:
        df = df.copy()
        # If index is datetime and 'time' column doesn't exist, move index to 'time'
        if isinstance(df.index, pd.DatetimeIndex) and "time" not in df.columns:
            df["time"] = df.index
        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)
        df = df.resample("1s").mean(numeric_only=True)
        if interpolate:
            df = df.interpolate(method="linear", limit_direction="both")
        return df

    @property
    def standard_columns(self):
        return [col for col in self.columns if col in DATA_TYPES]

    @property
    def extra_columns(self):
        return [col for col in self.columns if col not in DATA_TYPES]

    def best_distance_intervals(
        self, windows, stream="speed", distance_col="distance", **kwargs
    ):
        """
        Compute best intervals for a list of distance windows.

        Parameters
        ----------
        windows : list of float or float
            List of distance windows (in meters).
            If a single float, compute the best interval for that distance.
            If a list, compute the best intervals for each distance in the list.
        stream : str
            Name of the column to use as the stream (e.g., "speed", "heartrate").
        distance_col : str
            Name of the column to use as cumulative distance.

        Returns
        -------
        list of dict
            Each dict contains 'value', 'start_index', 'stop_index' for the window.
        """
        if isinstance(windows, (int, float)):
            windows = [windows]
        if not isinstance(windows, list):
            raise ValueError("windows must be a list of distances or a single distance")
        if stream not in self.columns:
            raise ValueError(f"Stream '{stream}' not found in DataFrame columns.")
        if distance_col not in self.columns:
            raise ValueError(
                f"Distance column '{distance_col}' not found in DataFrame columns."
            )
        y = self[stream].values
        distance = self[distance_col].values
        return multiple_best_distance_intervals(y, distance, windows, **kwargs)

    def fastest_distance_intervals(self, windows, distance_col="distance", **kwargs):
        """
        Compute fastest intervals for a list of distance windows.

        Parameters
        ----------
        windows : list of float or float
            List of distance windows (in meters).
            If a single float, compute the fastest interval for that distance.
            If a list, compute the fastest intervals for each distance in the list.
        distance_col : str
            Name of the column to use as cumulative distance.

        Returns
        -------
        list of dict
            Each dict contains 'value', 'start_index', 'stop_index' for the window.
        """
        if isinstance(windows, (int, float)):
            windows = [windows]
        if not isinstance(windows, list):
            raise ValueError("windows must be a list of distances or a single distance")
        if distance_col not in self.columns:
            raise ValueError(
                f"Distance column '{distance_col}' not found in DataFrame columns."
            )
        distance = self[distance_col]
        return multiple_fastest_distance_intervals(distance, windows, **kwargs)

    def best_intervals(self, windows, stream="speed", **kwargs):
        """
        Compute best intervals for a list of time windows.

        Parameters
        ----------
        windows : list of float or float
            List of time windows (in seconds).
            If a single float, compute the best interval for that time.
            If a list, compute the best intervals for each time in the list.
        stream : str
            Name of the column to use as the stream (e.g., "speed", "heartrate").

        Returns
        -------
        list of dict
            Each dict contains 'value', 'start_index', 'stop_index' for the window.
        """
        if isinstance(windows, (int, float)):
            windows = [windows]
        if not isinstance(windows, list):
            raise ValueError("windows must be a list of times or a single time")
        if stream not in self.columns:
            raise ValueError(f"Stream '{stream}' not found in DataFrame columns.")
        y = self[stream].values
        return multiple_best_intervals(y, windows, **kwargs)

    def elevation_gain(self, elevation_col="elevation"):
        """
        Compute the total elevation gain.

        Parameters
        ----------
        elevation_col : str
            Name of the column to use as elevation.

        Returns
        -------
        float
            Total elevation gain in meters.
        """
        if elevation_col not in self.columns:
            raise ValueError(
                f"Elevation column '{elevation_col}' not found in DataFrame columns."
            )
        return elevation_gain(self[elevation_col].values)

    @classmethod
    def merge_many(
        cls,
        workouts: List["WorkoutData"],
        resample: bool = True,
        interpolate: bool = False,
    ) -> "WorkoutData":
        """
        Merge multiple WorkoutData instances into a single WorkoutData object.

        Workouts are sorted by their start timestamp before merging. If two workouts
        overlap in time, the later workout's data takes precedence for the overlapping
        timestamps. Time gaps between workouts are preserved: after resampling to 1 Hz,
        all data columns (speed, heart rate, power, etc.) are ``NaN`` during the gap
        while the ``time`` column continues to reflect real elapsed seconds (including
        the gap period).

        Parameters
        ----------
        workouts : list of WorkoutData
            The workout objects to merge. Must contain at least one element.
        resample : bool, optional
            Whether to resample the merged result to 1 Hz. Default is ``True``.
        interpolate : bool, optional
            Whether to linearly interpolate ``NaN`` values after resampling.
            Default is ``False``, which preserves ``NaN`` values in the time gaps
            between workouts.

        Returns
        -------
        WorkoutData
            A new ``WorkoutData`` object representing the merged workout.

        Raises
        ------
        ValueError
            If ``workouts`` is an empty list.

        Examples
        --------
        Merge a warm-up and a main set recorded as separate files:

        >>> warmup = WorkoutData.from_file("warmup.fit")
        >>> main = WorkoutData.from_file("main.fit")
        >>> merged = WorkoutData.merge_many([warmup, main])

        The ``time`` column of *merged* starts at 0 and increases continuously,
        including the gap between the two workouts. Data columns are ``NaN``
        during the gap (when ``interpolate=False``).
        """
        if not workouts:
            raise ValueError("No workouts to merge.")

        # Strip the derived `time` column so _resample can correctly re-index
        # from the DatetimeIndex. Also convert to plain DataFrames to avoid
        # recursion issues with the WorkoutData subclass during concat.
        frames = []
        for w in workouts:
            df = pd.DataFrame(w).drop(columns=["time"], errors="ignore")
            frames.append(df)

        # Sort ascending by each workout's first timestamp
        frames.sort(key=lambda df: df.index[0])

        combined = pd.concat(frames)

        # For overlapping timestamps keep the later workout's data (keep="last"
        # after sorting frames by start time means the later-starting workout's
        # rows appear later in the concatenation and therefore "win").
        combined = combined[~combined.index.duplicated(keep="last")]
        combined.sort_index(inplace=True)

        return cls.from_raw(combined, resample=resample, interpolate=interpolate)

    def merge(
        self,
        other: "WorkoutData",
        resample: bool = True,
        interpolate: bool = False,
    ) -> "WorkoutData":
        """
        Merge this workout with another ``WorkoutData`` object.

        This is a convenience wrapper around :meth:`merge_many`.

        Parameters
        ----------
        other : WorkoutData
            The other workout to merge with.
        resample : bool, optional
            Whether to resample the merged result to 1 Hz. Default is ``True``.
        interpolate : bool, optional
            Whether to linearly interpolate ``NaN`` values after resampling.
            Default is ``False``, which preserves ``NaN`` values in the time gap
            between workouts.

        Returns
        -------
        WorkoutData
            A new ``WorkoutData`` object representing the merged workout.

        Examples
        --------
        >>> warmup = WorkoutData.from_file("warmup.fit")
        >>> main = WorkoutData.from_file("main.fit")
        >>> merged = warmup.merge(main)
        """
        return WorkoutData.merge_many([self, other], resample=resample, interpolate=interpolate)
