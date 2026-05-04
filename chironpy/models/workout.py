from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel
import pandas as pd
from typing import Union, Optional
from chironpy import read_file, read_strava
from chironpy.metrics.vert import grade_smooth_time, elevation_gain
from chironpy.metrics.speed import multiple_fastest_distance_intervals
from chironpy.metrics.core import (
    mean_max as _mean_max,
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

    def to_pandas(self) -> pd.DataFrame:
        """Return a plain ``pd.DataFrame`` copy of this workout."""
        return pd.DataFrame(self)

    def resample(self, freq: str, interpolate: bool = False) -> "WorkoutData":
        """Return a new ``WorkoutData`` resampled to the given frequency.

        Parameters
        ----------
        freq : str
            Pandas offset alias for the target frequency (e.g. ``"5s"``, ``"1min"``).
        interpolate : bool, optional
            Linearly interpolate ``NaN`` values after resampling. Default is ``False``.

        Returns
        -------
        WorkoutData
            A new ``WorkoutData`` at the requested frequency.
        """
        df = pd.DataFrame(self).drop(columns=["time"], errors="ignore")
        df = df.resample(freq).mean(numeric_only=True)
        if interpolate:
            df = df.interpolate(method="linear")
        return WorkoutData.from_raw(df, resample=False, interpolate=False)

    def resample_records(self, freq: str) -> pd.DataFrame:
        """Resample workout records to a lower frequency using per-column aggregation rules.

        Unlike :meth:`resample`, this method applies semantically correct aggregations
        per column type: cumulative fields use ``max``, instantaneous fields use ``mean``,
        GPS coordinates use ``mean``, and ``is_moving`` uses ``any``.

        Parameters
        ----------
        freq : str
            Pandas offset alias for the target frequency (e.g. ``"10s"``, ``"1min"``).

        Returns
        -------
        pd.DataFrame
            Resampled DataFrame at the requested frequency. Only columns present in the
            source data are included.
        """
        _CUMULATIVE = {"distance"}
        _POSITIONAL = {"latitude", "longitude"}
        _BOOLEAN = {"is_moving"}
        _AVERAGE = {
            "speed", "enhanced_speed", "power", "cadence", "heartrate",
            "temperature", "grade", "elevation", "enhanced_altitude",
            "left-right balance",
        }

        df = pd.DataFrame(self).drop(columns=["time"], errors="ignore")

        agg: dict = {}
        for col in df.columns:
            if col in _CUMULATIVE:
                agg[col] = "max"
            elif col in _POSITIONAL:
                agg[col] = "mean"
            elif col in _BOOLEAN:
                agg[col] = "any"
            elif col in _AVERAGE:
                agg[col] = "mean"

        if not agg:
            return df.resample(freq).mean(numeric_only=True)

        extra = [c for c in df.columns if c not in agg]
        for col in extra:
            if pd.api.types.is_numeric_dtype(df[col]):
                agg[col] = "mean"

        return df[list(agg)].resample(freq).agg(agg)

    def rolling(self, window: int, method: str = "mean") -> pd.DataFrame:
        """Compute a rolling average or median across standard columns.

        Parameters
        ----------
        window : int
            Size of the rolling window in seconds.
        method : {"mean", "median"}, optional
            Aggregation to apply. Default is ``"mean"``.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the rolling values for each standard column.

        Raises
        ------
        ValueError
            If ``method`` is not ``"mean"`` or ``"median"``.
        """
        if method not in ("mean", "median"):
            raise ValueError(f"method must be 'mean' or 'median', got '{method!r}'")
        roller = pd.DataFrame(self)[self.standard_columns].rolling(
            window, min_periods=1
        )
        if method == "mean":
            return roller.mean()
        return roller.median()

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

    def mean_max(
        self,
        columns: Union[str, List[str]],
        monotonic: bool = False,
    ) -> pd.DataFrame:
        """Compute the mean-max (power-duration) curve for one or more columns.

        Parameters
        ----------
        columns : str or list of str
            Column name(s) to compute mean-max for (e.g. ``"speed"``,
            ``["speed", "heartrate"]``).
        monotonic : bool, optional
            Enforce a monotonically decreasing curve. Default is ``False``.

        Returns
        -------
        pd.DataFrame
            DataFrame with a ``TimedeltaIndex`` (duration) and one
            ``mean_max_{column}`` column per requested stream.
        """
        if isinstance(columns, str):
            columns = [columns]
        data = None
        for column in columns:
            result = _mean_max(self[column], monotonic=monotonic)
            if data is None:
                index = pd.to_timedelta(range(1, len(result) + 1), unit="s")
                data = pd.DataFrame(index=index)
            data["mean_max_" + column] = result
        return data

    @classmethod
    def merge_many(
        cls,
        workouts: List["WorkoutData"],
        resample: bool = True,
        interpolate: bool = False,
        drop_gaps: bool = False,
    ) -> "WorkoutData":
        """
        Merge multiple WorkoutData instances into a single WorkoutData object.

        Workouts are sorted by their start timestamp before merging. If two workouts
        overlap in time, the later workout's data takes precedence for the overlapping
        timestamps. By default, time gaps between workouts are preserved: after
        resampling to 1 Hz, all data columns are ``NaN`` during the gap while the
        ``time`` column continues to reflect real elapsed seconds.

        ``distance`` is forward-filled across gap rows (it is a cumulative metric
        that should not reset to ``NaN`` during rest).

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
        drop_gaps : bool, optional
            When ``True``, each workout is shifted to start immediately after the
            previous one ends (1 second later), so no gap rows are produced during
            resampling. The ``time`` column reflects condensed elapsed time with
            no rest periods. Default is ``False``.
            Note: with ``drop_gaps=True``, performance metrics will not account
            for rest time between workouts and should be interpreted accordingly.

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

        if drop_gaps:
            # Shift each workout to start 1 second after the previous one ends
            # so resampling produces a contiguous time range with no gap rows.
            adjusted = [frames[0]]
            for i in range(1, len(frames)):
                prev_end = adjusted[-1].index[-1]
                offset = prev_end + pd.Timedelta(seconds=1) - frames[i].index[0]
                shifted = frames[i].copy()
                shifted.index = frames[i].index + offset
                adjusted.append(shifted)
            combined = pd.concat(adjusted)
        else:
            combined = pd.concat(frames)

        # For overlapping timestamps keep the later workout's data (keep="last"
        # after sorting frames by start time means the later-starting workout's
        # rows appear later in the concatenation and therefore "win").
        combined = combined[~combined.index.duplicated(keep="last")]
        combined.sort_index(inplace=True)

        result = cls.from_raw(combined, resample=resample, interpolate=interpolate)

        # Distance is cumulative — forward-fill across gap rows so it reads as
        # a continuous total rather than NaN during rest periods.
        if "distance" in result.columns:
            df = pd.DataFrame(result)
            df["distance"] = df["distance"].ffill()
            result = cls(df)

        return result

    def merge(
        self,
        other: "WorkoutData",
        resample: bool = True,
        interpolate: bool = False,
        drop_gaps: bool = False,
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
        drop_gaps : bool, optional
            When ``True``, the workout is shifted to start immediately after
            ``self`` ends so no gap rows are produced. Default is ``False``.

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
        return WorkoutData.merge_many(
            [self, other],
            resample=resample,
            interpolate=interpolate,
            drop_gaps=drop_gaps,
        )

    def set_start_time(self, start_time: pd.Timestamp) -> "WorkoutData":
        """
        Shift the workout's datetime index so it begins at ``start_time``.

        All timestamps are shifted by the same offset, preserving the relative
        spacing between records. The ``time`` column (seconds since start) is
        recomputed from the new index.

        Parameters
        ----------
        start_time : pd.Timestamp
            The new start datetime for the workout. If timezone-naive and the
            existing index is timezone-aware, UTC is assumed.

        Returns
        -------
        WorkoutData
            A new ``WorkoutData`` with a shifted datetime index.

        Examples
        --------
        >>> import pandas as pd
        >>> data = WorkoutData.from_file("warmup.fit")
        >>> shifted = data.set_start_time(pd.Timestamp("2025-01-01 08:00:00", tz="UTC"))
        """
        if not isinstance(self.index, pd.DatetimeIndex):
            raise TypeError("set_start_time requires a DatetimeIndex.")
        start_time = pd.Timestamp(start_time)
        if self.index.tz is not None and start_time.tzinfo is None:
            start_time = start_time.tz_localize(self.index.tz)
        offset = start_time - self.index[0]
        df = pd.DataFrame(self).copy()
        df.index = self.index + offset
        df.index.name = "datetime"
        df["time"] = (df.index - df.index[0]).total_seconds().astype(int)
        return WorkoutData(df)
