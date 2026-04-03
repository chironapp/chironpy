from enum import Enum


class DataTypeEnum(str, Enum):
    latitude = "latitude"
    longitude = "longitude"
    speed = "speed"
    enhanced_speed = "enhanced_speed"
    power = "power"
    left_right_balance = "left-right balance"
    elevation = "elevation"
    enhanced_altitude = "enhanced_altitude"
    cadence = "cadence"
    heartrate = "heartrate"
    temperature = "temperature"
    distance = "distance"


class DataTypeEnumExtended(str, Enum):
    is_moving = "is_moving"
    grade = "grade"
    time = "time"
