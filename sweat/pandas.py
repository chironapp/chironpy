from typing import List, Union

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from .constants import DataTypeEnum
from .metrics import core


@pd.api.extensions.register_dataframe_accessor("sweat")
class SweatAccessor:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        if not isinstance(obj.index, (pd.DatetimeIndex, pd.TimedeltaIndex)):
            raise AttributeError("DataFrame Index should be a DateTimeIndex.")

        if not all(obj.index.to_series().diff()[1:] == np.timedelta64(1, "s")):
            raise AttributeError(
                "Data is not sampled at a regular 1s interval. Consider resampling first."
            )

        for data_type in DataTypeEnum:
            # @TODO figure out which columns need to be numeric continue
            continue
            try:
                if not is_numeric_dtype(obj[data_type.value]):
                    raise AttributeError(f"Column {data_type.value} is not numeric")
            except KeyError:
                continue

    def mean_max(self, columns):
        raise NotImplemented()

    def mean_max(self, columns: Union[List, str]) -> pd.DataFrame:
        if isinstance(columns, str):
            columns = [columns]

        data = None
        for column in columns:
            result = core.mean_max(self._obj[column])

            if data is None:
                index = pd.to_timedelta(range(len(result)), unit="s")
                data = pd.DataFrame(index=index)

            data["mean_max_" + column] = result

        return data

    def to_timedelta_index(self):
        """This method converts the index to a relative TimedeltaIndex, returning a copy of the data frame with the new index.

        Returns:
            A pandas data frame with a TimedeltaIndex.
        """
        return self._obj.set_index(self._obj.index - self._obj.index[0])


@pd.api.extensions.register_series_accessor("sweat")
class SweatSeriesAccessor:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        if not isinstance(obj.index, pd.DatetimeIndex):
            raise AttributeError("DataFrame Index should be a DateTimeIndex.")

        if not all(obj.index.to_series().diff()[1:] == np.timedelta64(1, "s")):
            raise AttributeError(
                "Data is not sampled at a regular 1s interval. Consider resampling first."
            )

        if not is_numeric_dtype(obj):
            raise AttributeError(f"Series dtype should be numeric")

    def mean_max(self) -> pd.Series:
        result = core.mean_max(self._obj)
        index = pd.to_timedelta(range(len(result)), unit="s")
        return pd.Series(result, index=index, name="mean_max_" + self._obj.name)

    def time_in_zone(self):
        raise NotImplemented()

    def to_timedelta_index(self):
        """This method converts the index to a relative TimedeltaIndex, returning a copy of the series with the new index.

        Returns:
            A pandas series with a TimedeltaIndex.
        """
        index = self._obj.index - self._obj.index[0]
        return pd.Series(self._obj, index=index)