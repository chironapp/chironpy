import pytest

import pandas as pd

import chiron
from chiron.io import strava
from .utils import chironvcr


def test_top_level_import():
    assert chiron.read_strava == strava.read_strava


@chironvcr.use_cassette()
def test_read_strava():
    activity = chiron.read_strava(
        activity_id="3547667536", access_token="somerandomaccesstoken"
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
