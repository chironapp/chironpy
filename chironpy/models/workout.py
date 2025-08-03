from enum import Enum
from typing import Dict, Optional, List

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
        cls, filepath: str, resample: bool = True, interpolate: bool = True
    ) -> "WorkoutData":
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

    @classmethod
    def merge_many(cls, workouts: List["WorkoutData"]) -> "WorkoutData":
        """
        Merge multiple WorkoutData objects into a single continuous workout.
        
        Parameters
        ----------
        workouts : List[WorkoutData]
            List of WorkoutData objects to merge. Must contain at least one workout.
        
        Returns
        -------
        WorkoutData
            A new WorkoutData object containing all workouts merged in chronological order.
            
        Raises
        ------
        ValueError
            If workouts list is empty or contains non-WorkoutData objects.
        """
        if not workouts:
            raise ValueError("Cannot merge empty list of workouts")
        
        if not all(isinstance(w, WorkoutData) for w in workouts):
            raise ValueError("All items must be WorkoutData objects")
        
        if len(workouts) == 1:
            return workouts[0].copy()
        
        # Sort workouts by start time (first index value)
        sorted_workouts = sorted(workouts, key=lambda w: w.index[0])
        
        # Collect all DataFrames for concatenation
        dfs_to_concat = []
        cumulative_time_offset = 0
        
        for i, workout in enumerate(sorted_workouts):
            df = workout.copy()
            
            if i > 0:
                # Calculate time offset to make this workout continuous with previous ones
                # The new workout should start where the previous one ended
                time_offset = cumulative_time_offset
                
                # Adjust the datetime index
                time_diff = pd.Timedelta(seconds=time_offset)
                df.index = df.index + time_diff
                
                # Update the 'time' column if it exists (seconds since start)
                if 'time' in df.columns:
                    df['time'] = df['time'] + time_offset
                    
                # Update cumulative distance if it exists
                if 'distance' in df.columns and i > 0:
                    # Get the last distance from the previous combined data
                    prev_max_distance = dfs_to_concat[-1]['distance'].iloc[-1] if 'distance' in dfs_to_concat[-1].columns else 0
                    df['distance'] = df['distance'] + prev_max_distance
            
            # Update cumulative time offset for next iteration
            if 'time' in df.columns:
                cumulative_time_offset = df['time'].iloc[-1] + 1  # +1 second for next workout
            else:
                # Fallback: use the duration based on index
                duration = (df.index[-1] - df.index[0]).total_seconds()
                cumulative_time_offset += duration + 1
                
            dfs_to_concat.append(df)
        
        # Concatenate all DataFrames
        merged_df = pd.concat(dfs_to_concat, ignore_index=False)
        
        # Sort by index to ensure proper chronological order
        merged_df = merged_df.sort_index()
        
        # Create new WorkoutData from the merged DataFrame
        # Skip resampling since we already have 1Hz data
        result = cls(merged_df)
        
        # Recompute derived columns that might be affected by the merge
        
        # Recompute is_moving if speed exists
        if "speed" in result.columns:
            result["is_moving"] = result["speed"] > 0.5
            
        # Recompute grade if distance and elevation exist
        if (
            "grade" not in result.columns
            and "distance" in result.columns
            and "elevation" in result.columns
        ):
            try:
                result["grade"] = grade_smooth_time(
                    result["distance"].values, result["elevation"].values
                )
            except ImportError:
                pass  # grade_smooth_time not available
        
        return result

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
        df = df.resample("1S").mean(numeric_only=True)
        if interpolate:
            df = df.interpolate(method="linear", limit_direction="both")
        return df

    @property
    def standard_columns(self):
        return [col for col in self.columns if col in DATA_TYPES]

    @property
    def extra_columns(self):
        return [col for col in self.columns if col not in DATA_TYPES]
    
    @property
    def start_time(self):
        """Get the start time of the workout."""
        return self.index[0] if len(self) > 0 else None
    
    @property
    def end_time(self):
        """Get the end time of the workout."""
        return self.index[-1] if len(self) > 0 else None
    
    @property
    def duration(self):
        """Get the duration of the workout in seconds."""
        if len(self) == 0:
            return 0
        if 'time' in self.columns:
            return self['time'].iloc[-1] - self['time'].iloc[0]
        else:
            return (self.end_time - self.start_time).total_seconds()

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
