from datetime import datetime

from .helper import get_normal_timestamp


def sort_countries(game_id, data_2):
    data_countries = data_2["result"]["states"]["1"]["players"]
    countries = dict({})
    timestamp = data_2["result"]["states"]["1"]["timeStamp"]
    for country in data_countries:
        country = data_countries[country]
        if "siteUserID" in country:
            if int(country["playerID"]) > 0:
                countries[int(country["playerID"])] = dict({
                    "country_id": int(country["playerID"]),
                    "team_id": country["teamID"] if country["teamID"] != 0 else None,
                    "capital_id": int(country["capitalID"]),
                    "defeated": bool(country["defeated"]),
                    "computer": bool(country["computerPlayer"]),
                    "game_id": int(game_id),
                    "valid_from": datetime.fromtimestamp(get_normal_timestamp(timestamp))
                })
    return countries
