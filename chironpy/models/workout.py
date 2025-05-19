from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel
import pandas as pd
from typing import Union, Optional
from chironpy import read_file, read_strava
from chironpy.metrics.vert import grade_smooth_time
from chironpy.constants import DataTypeEnum, DataTypeEnumExtended

DATA_TYPES = (
    {member.value for member in DataTypeEnum}
    | {member.value for member in DataTypeEnumExtended}
)

class WorkoutData(pd.DataFrame):
    @classmethod
    def from_file(cls, filepath: str, resample: bool = True, interpolate: bool = True) -> "WorkoutData":
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
        interpolate: bool = True
    ) -> "WorkoutData":
        df = read_strava(
            activity_id=activity_id,
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            resample=False,
            interpolate=False
        )
        return cls.from_raw(df, resample=resample, interpolate=interpolate)

    @classmethod
    def from_raw(cls, df: pd.DataFrame, resample: bool = True, interpolate: bool = True) -> "WorkoutData":
        df = df.copy()
        df = cls._normalize_columns(df)
        if resample:
            df = cls._resample(df, interpolate=interpolate)
        # Add DATA_TYPES.time column: integer seconds since workout start
        if isinstance(df.index, pd.DatetimeIndex):
            start_time = df.index[0]
            df[(DataTypeEnum.time if hasattr(DataTypeEnum, "time") else "time")] = (df.index - start_time).total_seconds().astype(int)
            # rename index from 'time' to 'datetime'
            df.index.name = "datetime"
        # Add is_moving column if speed exists
        if "speed" in df.columns:
            # Consider moving if speed > 0.5 m/s (adjust threshold as needed)
            # TODO: add a parameter to set the threshold
            # TODO: consider a rolling window to account for GPS errors
            df["is_moving"] = df["speed"] > 0.5
        # Add grade column if missing and distance & elevation exist
        if "grade" not in df.columns and "distance" in df.columns and "elevation" in df.columns:
            try:
                df["grade"] = grade_smooth_time(df["distance"].values, df["elevation"].values)
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
