import json
import math
from datetime import datetime


def get_combined_number(number_1, number_2):
    try:
        number_1 = int(number_1)
        number_2 = int(number_2)
        return int(f"{number_1}{number_2}")
    except ValueError:
        return int(f"{number_1}")


def get_end_time(start_time, end_time, speed):
    if int(end_time) != 0:
        difference = (end_time - start_time) * speed
        new_end_time = start_time + difference
        return round(new_end_time)
    else:
        return 0


def get_normal_timestamp(timestamp):
    try:
        timestamp = int(timestamp)
        if get_integer_places(timestamp) == 13:
            return round(timestamp / 1000)
        else:
            return timestamp
    except:
        return 0


def get_integer_places(theNumber):
    if theNumber <= 999999999999997:
        return int(math.log10(theNumber)) + 1
    else:
        counter = 15
        while theNumber >= 10 ** counter:
            counter += 1
        return counter


def is_title_case(title):
    cases = ["reports casualties", "recruits new"]
    for case in cases:
        if case in title:
            return True
    return False


def compare(dict_1, dict_2, exclude_keys: list[str]) -> bool:
    for key in dict_1.keys():
        if key in exclude_keys:
            continue
        if key not in dict_2:
            return True

        if dict_1[key] != dict_2[key]:
            return True
    return False


class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime):
            return str(z)
        else:
            return super().default(z)
