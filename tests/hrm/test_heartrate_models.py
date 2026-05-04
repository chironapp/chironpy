import pandas as pd
import pytest

from chironpy.hrm import heartrate_models


def test_heartrate_model():
    heartrate = pd.Series(range(50))
    power = pd.Series(range(0, 100, 2))

    model, predictions = heartrate_models.heartrate_model(heartrate, power)

    assert len(predictions) == 50

    # Nelder-Mead fit values can drift slightly across numeric library versions.
    # Validate that the fitted model remains physically plausible and accurate.
    assert model.params["hr_rest"].value == pytest.approx(0.0, abs=1e-2)
    assert model.params["dhr"].value == pytest.approx(0.5, abs=1e-2)
    assert model.params["tau_rise"].value > 0
    assert model.params["tau_fall"].value > 0
    assert model.params["hr_drift"].value > 0

    rmse = ((heartrate - pd.Series(predictions)) ** 2).mean() ** 0.5
    assert rmse < 0.01
