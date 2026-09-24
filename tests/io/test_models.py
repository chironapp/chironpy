import pytest
from pydantic import ValidationError

from chironpy.io.models import Athlete, Gender, ThresholdSetting, UnitSystem


def test_athlete_from_fit_file_with_no_user_profile():
    """A FIT file carrying no ``user_profile`` message must still decode.

    Plenty of valid files have no athlete profile at all. Before every field
    carried an explicit ``= None``, ``model_validate({})`` raised eight
    "Field required" errors here, and a caller reading such a file with
    ``metadata=True`` saw it fail as though the file were corrupt.
    """
    athlete = Athlete.from_fit_file(None, None, None)

    assert athlete.name is None
    assert athlete.gender is None
    assert athlete.age is None
    assert athlete.weight is None
    assert athlete.height is None
    assert athlete.resting_heartrate is None
    assert athlete.max_heartrate is None
    assert athlete.unit_system is None
    assert athlete.threshold is None
    assert athlete.activity_class is None


def test_athlete_accepts_an_empty_payload():
    assert Athlete.model_validate({}) == Athlete()


def test_athlete_from_fit_file_reads_a_user_profile():
    athlete = Athlete.from_fit_file(
        {
            "gender": "female",
            "age": 34,
            "weight": 61.5,
            "height": 1.7,
            "default_max_heart_rate": 190,
            "resting_heart_rate": 48,
            "activity_class": 75,
            "weight_setting": "metric",
        },
        None,
        None,
    )

    assert athlete.gender is Gender.FEMALE
    assert athlete.age == 34
    assert athlete.weight == 61.5
    assert athlete.height == 1.7
    assert athlete.max_heartrate == 190
    assert athlete.resting_heartrate == 48
    assert athlete.activity_class == 75
    assert athlete.unit_system is UnitSystem.METRIC


def test_athlete_gender_falls_back_to_unspecified():
    athlete = Athlete.from_fit_file({"gender": None}, None, None)

    assert athlete.gender is Gender.UNSPECIFIED


def test_athlete_activity_class_level_max_becomes_a_number():
    athlete = Athlete.from_fit_file({"activity_class": "level_max"}, None, None)

    assert athlete.activity_class == 100


def test_athlete_discards_a_non_numeric_activity_class():
    athlete = Athlete.from_fit_file({"activity_class": "unexpected"}, None, None)

    assert athlete.activity_class is None


def test_athlete_threshold_needs_both_sport_and_zones():
    """The threshold is only built when the file carries both messages."""
    sport = {"sport": "running", "sub_sport": "generic"}
    zones = {"functional_threshold_power": 280, "threshold_heart_rate": 172}

    assert Athlete.from_fit_file(None, zones, None).threshold is None
    assert Athlete.from_fit_file(None, None, sport).threshold is None

    threshold = Athlete.from_fit_file(None, zones, sport).threshold
    assert threshold is not None
    assert threshold.sport == "running"
    assert threshold.sub_sport == "generic"
    assert threshold.power == 280
    assert threshold.heartrate == 172


def test_threshold_setting_tolerates_absent_power_and_heartrate():
    """A zones_target message need not carry either value."""
    threshold = ThresholdSetting(sport="cycling", sub_sport="generic")

    assert threshold.power is None
    assert threshold.heartrate is None
    assert threshold.speed == 0.0


def test_threshold_setting_still_requires_a_sport():
    with pytest.raises(ValidationError):
        ThresholdSetting(sub_sport="generic")
