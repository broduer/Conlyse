import json
import logging
from datetime import datetime

from .helper import get_normal_timestamp
from .sort_armies import sort_armies, sort_commands, sort_warfare_units
from .sort_countries import sort_countries
from .sort_static_countries import sort_static_countries
from .sort_game import sort_game
from .sort_newspaper import NewspaperSorter
from .sort_players import sort_players
from .sort_provinces import sort_provinces, sort_buildings
from .sort_scenarios import sort_static_scenarios
from .sort_static_provinces import sort_static_provinces
from .sort_teams import sort_teams
from .sort_trades import sort_trades


def sort(game_id, data, data_requests):
    if "result" not in data:
        return
    sorted_data = {}
    states = data["result"]["states"].keys()
    day = data_requests["2"]["data"]["result"]["states"]["12"]["dayOfGame"]
    logging.debug(f"Sorting Game {game_id}")
    sorted_data["timestamp"] = datetime.fromtimestamp(get_normal_timestamp(data["result"]["timeStamp"]))
    sorted_data["map_id"] = data_requests["2"]["data"]["result"]["states"]["12"]["mapID"]
    if "12" in states:
        logging.log(5, "Sorting Game State")
        sorted_data["game"] = sort_game(game_id, data)

    if len(states) > 5:
        logging.log(5, "Sorting Static Countries")
        sorted_data["static_countries"] = sort_static_countries(sorted_data["map_id"],
                                                                data_requests["2"]["data"])
        logging.log(5, "Sorting Static Provinces")
        sorted_data["static_provinces"] = sort_static_provinces(data_requests["1"]["data"],
                                                                data_requests["2"]["data"])
        logging.log(5, "Sorting Static Scenarios")
        sorted_data["static_scenarios"] = sort_static_scenarios(data_requests["3"]["data"])

    if "1" in states:
        logging.log(5, "Sorting Countries, Teams and Players")
        sorted_data["countries"] = sort_countries(game_id, data)
        sorted_data["teams"] = sort_teams(game_id, data)
        sorted_data["players"] = sort_players(data)

    if "3" in states:
        amount_provinces = len(data['result']['states']['3']['map']['locations'][1])
        logging.log(5, f"Sorting {amount_provinces} dynamic Provinces")
        sorted_data["provinces"] = sort_provinces(game_id, data_requests["1"]["data"], data, data_requests["2"]["data"])
        sorted_data["buildings"] = sort_buildings(game_id, data)

    if "6" in states:
        amount_armies = len(data['result']['states']['6']['armies']) - 1
        logging.log(5, f"Sorting {amount_armies} Armies")
        sorted_data["armies"] = sort_armies(game_id, data)
        sorted_data["commands"] = sort_commands(game_id, data)
        sorted_data["warfare_units"] = sort_warfare_units(game_id, data)

    if "4" in states:
        logging.log(5, "Sorting Trades")
        sorted_data["trades"] = sort_trades(game_id, data)

    if "2" in states:
        logging.log(5, "Sorting Newspaper Articles")
        newspaper_sorter = NewspaperSorter(game_id, day, data, data_requests["2"]["data"])
        newspaper_sorter.run()
        sorted_data["researches"] = newspaper_sorter.researches
        sorted_data["army_losses_gains"] = newspaper_sorter.army_loses_gains

    return sorted_data


def startSort():
    data = []
    for i in range(1, 4):
        with open(f"../../Conlyse_analytics/Version 1/data{i}.json") as file:
            data.append(json.loads(file.read()))
