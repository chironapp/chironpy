from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Gender(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    UNSPECIFIED = "UNSPECIFIED"


class UnitSystem(Enum):
    METRIC = "METRIC"
    STATUTE = "STATUTE"
    NAUTICAL = "NAUTICAL"


class ThresholdSetting(BaseModel):
    sport: str
    sub_sport: str
    power: Optional[int] = None
    speed: Optional[float] = 0.0
    heartrate: Optional[int] = None


class Athlete(BaseModel):
    # Every field carries an explicit ``= None``. Under Pydantic v1,
    # ``Optional[X]`` implied that default, so omitting it was harmless; under
    # v2 it makes the field required-but-nullable, which means a FIT file
    # carrying no ``user_profile`` message fails validation instead of
    # producing an Athlete with nothing filled in.
    name: Optional[str] = None
    gender: Optional[Gender] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    resting_heartrate: Optional[int] = None
    max_heartrate: Optional[int] = None
    unit_system: Optional[UnitSystem] = None
    threshold: Optional[ThresholdSetting] = None
    activity_class: Optional[int] = None

    @classmethod
    def from_fit_file(cls, user_profile, zones_target, sport):
        data = {}
        if user_profile is not None:
            fit_gender = user_profile.get("gender", None)
            if fit_gender == "male":
                data["gender"] = Gender.MALE
            elif fit_gender == "female":
                data["gender"] = Gender.FEMALE
            else:
                data["gender"] = Gender.UNSPECIFIED

            for setting in ["elev", "weight", "speed", "dist", "temperature", "height"]:
                if f"{setting}_setting" in user_profile:
                    if user_profile[f"{setting}_setting"] == "statute":
                        data["unit_system"] = UnitSystem.STATUTE
                    elif user_profile[f"{setting}_setting"] == "nautical":
                        data["unit_system"] = UnitSystem.NAUTICAL
                    else:
                        data["unit_system"] = UnitSystem.METRIC
                    break

            data["weight"] = user_profile.get("weight", None)
            data["height"] = user_profile.get("height", None)
            data["age"] = user_profile.get("age", None)
            data["max_heartrate"] = user_profile.get("default_max_heart_rate", None)
            data["resting_heartrate"] = user_profile.get("resting_heart_rate", None)

            activity_class = user_profile.get("activity_class", None)
            if activity_class == "level_max":
                activity_class = 100
            if activity_class is not None and not isinstance(activity_class, int):
                activity_class = None
            data["activity_class"] = activity_class

        if sport is not None and zones_target is not None:
            threshold_data = {}
            threshold_data["sport"] = sport["sport"]
            threshold_data["sub_sport"] = sport["sub_sport"]
            threshold_data["power"] = zones_target.get(
                "functional_threshold_power", None
            )
            threshold_data["heartrate"] = zones_target.get("threshold_heart_rate", None)
            data["threshold"] = threshold_data

        return cls.model_validate(data)
