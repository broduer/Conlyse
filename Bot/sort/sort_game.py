from datetime import datetime

from helper import get_end_time, get_normal_timestamp


def sort_game(game_id, data_2):
    data_game = data_2["result"]["states"]["12"]
    day = data_game["dayOfGame"]
    start_time = get_normal_timestamp(data_game["nextDayTime"]) - (day + 1) * data_game["timeScale"] * 24 * 3600
    return dict({
        "game_id": game_id,
        "scenario_id": int(data_game["scenarioID"]),
        "map_id": int(data_game["mapID"]),
        "start_time": datetime.fromtimestamp(start_time),
        "end_time": datetime.fromtimestamp(
            get_end_time(data_game["startOfGame"], data_game["endOfGame"], 1 / data_game["timeScale"]))
        if data_game["gameEnded"] else None,
        "current_time": datetime.fromtimestamp(get_normal_timestamp(data_game["timeStamp"])) if not data_game["gameEnded"] else None,
        "next_day_time": datetime.fromtimestamp(get_normal_timestamp(data_game["nextDayTime"])),
        "next_heal_time": datetime.fromtimestamp(get_normal_timestamp(data_game["nextHealTime"])) if data_game["nextHealTime"] != 0 else None,
    })