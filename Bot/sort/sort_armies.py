import json
from datetime import datetime

from Bot.sort.helper import get_normal_timestamp, DateTimeEncoder


def sort_armies(game_id, data):
    timestamp = data["result"]["states"]["6"]["timeStamp"]
    data_armies = data["result"]["states"]["6"]["armies"]
    armies = {}
    for army_id in data_armies:
        if army_id == "@c":
            continue
        army = data["result"]["states"]["6"]["armies"][army_id]
        armies[int(army_id)] = {
            "army_id": int(army_id),
            "owner_id": army.get("o"),
            "province_location_id": army.get("l"),
            "presentation_warfare_id": army.get("pt"),
            "kl": army.get("k"),
            "army_number": army.get("an"),
            "health_point": army.get("hp"),
            "next_attack_time": datetime.fromtimestamp(get_normal_timestamp(army.get("na"))),
            "last_anti_air_attack_time": datetime.fromtimestamp(get_normal_timestamp(army.get("laa"))),
            "radar_type": list(army.get("rs").get("ssm").keys())[0] if "rs" in army else None,
            "radar_size": list(army.get("rs").get("ssm").values())[0] if "rs" in army else None,
            "game_id": game_id,
            "valid_from": datetime.fromtimestamp(get_normal_timestamp(timestamp)),
        }
        armies[int(army_id)]["units"] = get_warfare_units(army["u"][1]) if "u" in army else None
        command = get_command(timestamp, game_id, army_id, army)
        if command:
            armies[int(army_id)]["command"] = round_coordinates(command)
    return armies


def round_coordinates(command):
    return {
        **command,
        "start_coordinate_x": round(command["start_coordinate_x"]),
        "start_coordinate_y": round(command["start_coordinate_y"]),
        "target_coordinate_x": round(command["target_coordinate_x"]),
        "target_coordinate_y": round(command["target_coordinate_y"]),
    }


def get_warfare_units(data):
    units = []
    for unit in data:
        units.append({
            "warfare_id": unit["id"],
            "warfare_type_id": unit["t"],
            "size": unit["s"],
            "health_point": unit["hp"],
        })
    return units


def get_command(timestamp, game_id, army_id, army):
    command = {
        "army_id": int(army_id),
        "valid_from": datetime.fromtimestamp(get_normal_timestamp(timestamp)),
        "game_id": game_id
    }
    if army.get("os"):
        command["transport_level"] = 0
    elif army.get("a"):
        command["transport_level"] = 2
    else:
        command["transport_level"] = 1
    if "c" in army:
        current_command = army.get("c")[1][0]
        match current_command["@c"]:
            case "gc":
                command["command_type"] = "go"
                command["start_coordinate_x"] = current_command.get("sp").get("x")
                command["start_coordinate_y"] = current_command.get("sp").get("y")
                command["target_coordinate_x"] = current_command.get("tp").get("x")
                command["target_coordinate_y"] = current_command.get("tp").get("y")
                command["start_time"] = datetime.fromtimestamp(get_normal_timestamp(current_command.get("st")))
                command["arrival_time"] = datetime.fromtimestamp(get_normal_timestamp(current_command.get("at")))

            case "pc":
                if current_command["type"] == "Guard":
                    command["target_coordinate_x"] = army.get("ap").get("x")
                    command["target_coordinate_y"] = army.get("ap").get("y")
                    if current_command["approaching"]:
                        command["command_type"] = "gop"
                        command["start_time"] = datetime.fromtimestamp(
                            get_normal_timestamp(army.get("aip")["lastAirActionTime"]))
                        command["arrival_time"] = datetime.fromtimestamp(get_normal_timestamp(army.get("at"))),
                        command["start_coordinate_x"] = army.get("aip")["lastAirPosition"].get("x")
                        command["start_coordinate_y"] = army.get("aip")["lastAirPosition"].get("y")
                    else:
                        command["command_type"] = "syp"
                        command["start_coordinate_x"] = army.get("ap").get("x")
                        command["start_coordinate_y"] = army.get("ap").get("y")
                elif current_command["type"] == "AirplaneRelocation":
                    command["start_coordinate_x"] = army.get("aip")["lastAirPosition"].get("x")
                    command["start_coordinate_y"] = army.get("aip")["lastAirPosition"].get("y")
                    command["target_coordinate_x"] = army.get("ap").get("x")
                    command["target_coordinate_y"] = army.get("ap").get("y")
                    command["arrival_time"] = datetime.fromtimestamp(get_normal_timestamp(current_command.get("at")))
                    command["start_time"] = datetime.fromtimestamp(
                        get_normal_timestamp(army.get("aip")["lastAirActionTime"]))

            case "wc":
                start_time = current_command.get("execTime") - current_command.get("waitSeconds") * 1000
                command["start_time"] = datetime.fromtimestamp(get_normal_timestamp(start_time))
                command["arrival_time"] = datetime.fromtimestamp(
                    get_normal_timestamp(current_command.get("execTime"))),
                if "ap" in army:
                    command["command_type"] = "go"
                    command["start_coordinate_x"] = army.get("ap").get("x")
                    command["start_coordinate_y"] = army.get("ap").get("y")
                    command["target_coordinate_x"] = army.get("p").get("x")
                    command["target_coordinate_y"] = army.get("p").get("y")
                else:
                    command["command_type"] = "sy"
                    command["start_coordinate_x"] = army.get("p").get("x")
                    command["start_coordinate_y"] = army.get("p").get("y")
                    command["target_coordinate_x"] = army.get("p").get("x")
                    command["target_coordinate_y"] = army.get("p").get("y")

            case "ac":
                command["arrival_time"] = datetime.fromtimestamp(get_normal_timestamp(army.get("na"))),
                if army.get("a"):
                    command["start_time"] = datetime.fromtimestamp(
                        get_normal_timestamp(army.get("aip")["lastAirActionTime"]))
                    command["start_coordinate_x"] = army.get("aip")["lastAirPosition"].get("x")
                    command["start_coordinate_y"] = army.get("aip")["lastAirPosition"].get("y")
                    command["target_coordinate_x"] = army.get("ap").get("x")
                    command["target_coordinate_y"] = army.get("ap").get("y")
                else:
                    command["start_coordinate_x"] = army.get("p").get("x")
                    command["start_coordinate_y"] = army.get("p").get("y")
                    command["target_coordinate_x"] = army.get("ap").get("x")
                    command["target_coordinate_y"] = army.get("ap").get("y")

    else:
        if "p" not in army:
            return None
        command["command_type"] = "sy"
        command["start_coordinate_x"] = army.get("p").get("x")
        command["start_coordinate_y"] = army.get("p").get("y")
        command["target_coordinate_x"] = army.get("p").get("x")
        command["target_coordinate_y"] = army.get("p").get("y")
    return command


if "__main__" == __name__:
    with open("../../../Conlyse_analytics/Data/Version 9/data2.json", "r") as file:
        data = json.loads(file.read())
    armies = sort_armies(231, data)
    with open("../../../Conlyse_analytics/sorted_data/armies_1.json", "w") as file:
        file.write(json.dumps(armies, indent=2, cls=DateTimeEncoder))
