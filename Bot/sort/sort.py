import json
import logging
from datetime import datetime

from Bot.sort.helper import get_normal_timestamp
from Bot.sort.sort_armies import sort_armies
from Bot.sort.sort_countries import sort_countries
from Bot.sort.sort_game import sort_game
from Bot.sort.sort_newspaper import sort_newspaper
from Bot.sort.sort_players import sort_players
from Bot.sort.sort_provinces import sort_provinces, sort_buildings
from Bot.sort.sort_scenarios import sort_static_scenarios
from Bot.sort.sort_static_provinces import sort_static_provinces
from Bot.sort.sort_teams import sort_teams
from Bot.sort.sort_trades import sort_trades


def sort(game_id, data, data_requests):
    if "result" not in data:
        return
    sorted_data = {}
    states = data["result"]["states"].keys()
    logging.debug(f"Sorting Game {game_id}")
    sorted_data["timestamp"] = datetime.fromtimestamp(get_normal_timestamp(data["result"]["timeStamp"]))
    if "12" in states:
        logging.debug("Sorting Game State")
        sorted_data["game"] = sort_game(game_id, data)

    if len(states) > 5:
        logging.debug("Sorting Static Provinces")
        sorted_data["static_provinces"] = sort_static_provinces(data_requests["1"]["data"],
                                                               data_requests["2"]["data"])
        logging.debug("Sorting Static Scenarios")
        sorted_data["static_scenarios"] = sort_static_scenarios(data_requests["3"]["data"])

    if "1" in states:
        logging.debug("Sorting Countries, Teams and Players")
        sorted_data["countries"] = sort_countries(game_id, data)
        sorted_data["teams"] = sort_teams(game_id, data)
        sorted_data["players"] = sort_players(data)

    if "3" in states:
        amount_provinces = len(data['result']['states']['3']['map']['locations'][1])
        logging.debug(f"Sorting {amount_provinces} dynamic Provinces")
        sorted_data["provinces"] = sort_provinces(game_id, data_requests["1"]["data"], data, data_requests["2"]["data"])
        sorted_data["buildings"] = sort_buildings(game_id, data)

    if "6" in states:
        sorted_data["armies"] = sort_armies(game_id, data)

    if "4" in states:
        logging.debug("Sorting Trades")
        sorted_data["trades"] = sort_trades(game_id, data)

    if "2" in states:
        logging.debug("Sorting Newspaper Articles")
        sorted_data["newspaper"] = sort_newspaper(data, data_requests["2"]["data"])

    return sorted_data


def startSort():
    data = []
    for i in range(1, 4):
        with open(f"../../Conlyse_analytics/Version 1/data{i}.json") as file:
            data.append(json.loads(file.read()))
