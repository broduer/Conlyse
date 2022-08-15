from Bot.sort.helper import get_end_time, get_normal_timestamp


def sort_game(game_id, data_2):
    data_game = data_2["result"]["states"]["12"]
    return dict({
        "game_id": game_id,
        "scenario_id": int(data_game["scenarioID"]),
        "map_id": int(data_game["mapID"]),
        "start_time": int(data_game["startOfGame"]),
        "end_time": get_end_time(data_game["startOfGame"], data_game["endOfGame"],
                                 1 / data_game["timeScale"]),
        "current_time": get_normal_timestamp(data_game["timeStamp"]) if not data_game["gameEnded"] else None,
        "next_day_time": get_normal_timestamp(data_game["nextDayTime"]),
        "next_heal_time": get_normal_timestamp(data_game["nextHealTime"]),
    })