from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Optional, Union

import pandas as pd
from stravalib.client import Client

from .utils import resample_data


STREAM_TYPES = [
    "time",
    "latlng",
    "distance",
    "altitude",
    "velocity_smooth",
    "heartrate",
    "cadence",
    "watts",
    "temp",
    "moving",
    "grade_smooth",
]

COLUMN_TRANSLATIONS = {
    "altitude": "elevation",
    "velocity_smooth": "speed",
    "watts": "power",
    "temp": "temperature",
    "grade_smooth": "grade",
}


def read_local_strava(
    streams: Union[dict, str, Path],
    activity_start_date_local: Optional[datetime] = None,
    resample: bool = False,
    interpolate: bool = False,
) -> pd.DataFrame:
    """This method lets you load locally saved Strava activity stream data instead of calling the Strava API.
    Works the same as `io.read_strava`, except:
    - The `streams` dict is provided as an argument instead of fetched from Strava API streams.
    - `activity_start_date_local` is optionally provided as an argument, if omitted it is set to the current time.
    Columns names are translated to chiron terminology (e.g. "heart_rate" > "heartrate").
    Two API calls are made to the Strava API: 1 to retrieve activity metadata, 1 to retrieve the raw data ("streams").

    Args:
        streams: dict or file-like containing the raw data streams for the activity, eg:
            {
                "temp":{"data":[28,27,...],
                "series_type":"distance","original_size":1504,"resolution":"high"},
                "latlng":{"data":[[-27.291784,153.051267],[-27.29178,153.051237],...],],"series_type":"distance","original_size":1504,"resolution":"high"},
                "velocity_smooth":{"data":[0,0,2.65,...], ...},
                "cadence":{"data":[0,0,81,81,90,...], ...},
                "distance":{"data":[1.8,4.3,7.1,18.3,], ...},
                "heartrate":{"data":[92,92,96,98,...],...},
                "altitude":{"data":[7.2,7.2,7.2,7.4,8,...],...}
                "time":{"data":[0,1,2,5,10,13,...],...},...}
            }
        activity_start_date_local: The activity local start datetime, equivalent to Strava API client activity.start_date_local. Optional.
        resample: whether or not the data frame needs to be resampled to 1Hz
        interpolate: whether or not missing data in the data frame needs to be interpolated

    Returns:
        A pandas data frame with all the data.
    """
    if isinstance(streams, str):
        # If streams is a file path, read the JSON file
        with open(streams, "r") as file:
            streams = json.load(file)
    elif isinstance(streams, Path):
        # If streams is a file path, read the JSON file
        with open(streams, "r") as file:
            streams = json.load(file)

    elif not isinstance(streams, dict):
        raise ValueError("Input should be a dictionary or a path to a JSON file")

    if activity_start_date_local is None:
        start_datetime = datetime.now()
    else:
        start_datetime = activity_start_date_local

    raw_data = dict()
    for key, value in streams.items():
        if key == "latlng":
            latitude, longitude = list(zip(*value["data"]))
            raw_data["latitude"] = latitude
            raw_data["longitude"] = longitude
        else:
            try:
                key = COLUMN_TRANSLATIONS[key]
            except KeyError:
                pass
            # print(key)
            # print(value)
            # print(type(value))
            # print(value.data)
            raw_data[key] = value["data"]

    data = pd.DataFrame(raw_data)

    def time_to_datetime(time):
        return start_datetime + timedelta(seconds=time)

    data["datetime"] = data["time"].apply(time_to_datetime)

    data = data.drop(["time"], axis="columns")

    data = data.set_index("datetime")

    data = resample_data(data, resample, interpolate)

    return data
