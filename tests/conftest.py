import pandas as pd
import pytest
import os
import json
from chiron.io import strava


@pytest.fixture
def power():
    return pd.Series(range(100))
