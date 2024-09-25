from datetime import datetime
import json
import pytest

import pandas as pd

import sweat
from sweat.io import local_strava
from sweat.examples.utils import FileTypeEnum


def test_top_level_import():
    assert sweat.read_local_strava == local_strava.read_local_strava


@pytest.mark.parametrize(
    "example", [(i) for i in sweat.examples(file_type=FileTypeEnum.json, course=False)]
)
def test_read_local_strava(example):
    # Load example.path JSON file into a dict
    with open(example.path, 'r') as file:
        streams = json.load(file)

    activity = sweat.read_local_strava(
        streams, activity_start_date_local=datetime.now()
    )

    assert isinstance(activity, pd.DataFrame)
    assert isinstance(activity.index, pd.DatetimeIndex)
    columns = set(
        [
            "elevation",
            "speed",
            "cadence",
            "grade",
            "heartrate",
            "power",
            "temperature",
            "distance",
            "moving",
            "latitude",
            "longitude",
        ]
    )
    assert columns == set(activity.columns.tolist())
