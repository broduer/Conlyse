import json
from datetime import datetime

from helper import get_normal_timestamp, DateTimeEncoder


def sort_armies(game_id, data):
    timestamp = data["result"]["states"]["6"]["timeStamp"]
    data_armies = data["result"]["states"]["6"]["armies"]
    armies = []
    for army_id in data_armies:
        if army_id == "@c":
            continue
        army = data["result"]["states"]["6"]["armies"][army_id]

        # Get Radar Type and Size
        if "rs" in army:
            for key in army.get("rs").get("ssm"):
                try:
                    radar_type = int(key)
                    radar_size = int(army.get("rs").get("ssm").get(key))
                    break
                except ValueError:
                    continue
            else:
                radar_type = None
                radar_size = None
        else:
            radar_type = None
            radar_size = None
        armies.append({
            "army_id": int(army_id),
            "owner_id": army.get("o"),
            "province_location_id": army.get("l"),
            "presentation_warfare_id": army.get("pt"),
            "kills": army.get("k") if "k" in army else 0,
            "army_number": army.get("an"),
            "health_point": round(army.get("hp"), 2) if "hp" in army else None,
            "next_attack_time": datetime.fromtimestamp(get_normal_timestamp(army.get("na"))) if "na" in army else None,
            "next_anti_aircraft_attack_time": datetime.fromtimestamp(get_normal_timestamp(army.get("naa"))) if "naa" in army else None,
            "radar_type": radar_type,
            "radar_size": radar_size,
            "game_id": int(game_id),
            "valid_from": datetime.fromtimestamp(get_normal_timestamp(timestamp)),
        })
    return armies


def sort_commands(game_id, data):
    timestamp = data["result"]["states"]["6"]["timeStamp"]
    data_armies = data["result"]["states"]["6"]["armies"]
    commands = []
    for army_id in data_armies:
        if army_id == "@c":
            continue
        army = data["result"]["states"]["6"]["armies"][army_id]
        command = {
            "army_id": int(army_id),
            "valid_from": datetime.fromtimestamp(get_normal_timestamp(timestamp)),
            "start_time": datetime.fromtimestamp(get_normal_timestamp(timestamp)),
            "arrival_time": None,
            "game_id": int(game_id)
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
                    command["arrival_time"] = datetime.fromtimestamp(get_normal_timestamp(current_command.get("at")))
                    command["start_time"] = datetime.fromtimestamp(get_normal_timestamp(current_command.get("st")))

                case "pc":
                    if current_command["type"] == "Guard":
                        command["target_coordinate_x"] = army.get("ap").get("x")
                        command["target_coordinate_y"] = army.get("ap").get("y")
                        if current_command["approaching"]:
                            command["command_type"] = "gop"
                            command["start_time"] = datetime.fromtimestamp(
                                get_normal_timestamp(army.get("aip")["lastAirActionTime"]))
                            command["arrival_time"] = datetime.fromtimestamp(get_normal_timestamp(army.get("at")))
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
                        command["arrival_time"] = datetime.fromtimestamp(get_normal_timestamp(83247))
                        command["start_time"] = datetime.fromtimestamp(
                            get_normal_timestamp(army.get("aip")["lastAirActionTime"]))

                case "wc":
                    start_time = current_command.get("execTime") - current_command.get("waitSeconds") * 1000
                    command["start_time"] = datetime.fromtimestamp(get_normal_timestamp(start_time))
                    command["arrival_time"] = datetime.fromtimestamp(
                        get_normal_timestamp(current_command.get("execTime")))
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
                    command["arrival_time"] = datetime.fromtimestamp(get_normal_timestamp(army.get("na")))
                    if army.get("a"):
                        command["command_type"] = "go"
                        command["start_time"] = datetime.fromtimestamp(
                            get_normal_timestamp(army.get("aip")["lastAirActionTime"]))
                        command["start_coordinate_x"] = army.get("aip")["lastAirPosition"].get("x")
                        command["start_coordinate_y"] = army.get("aip")["lastAirPosition"].get("y")
                        command["target_coordinate_x"] = army.get("ap").get("x")
                        command["target_coordinate_y"] = army.get("ap").get("y")
                    else:
                        command["command_type"] = "sya"
                        command["start_coordinate_x"] = army.get("p").get("x")
                        command["start_coordinate_y"] = army.get("p").get("y")
                        command["target_coordinate_x"] = army.get("ap").get("x")
                        command["target_coordinate_y"] = army.get("ap").get("y")

        else:
            if "p" not in army:
                continue
            command["command_type"] = "sy"
            command["start_coordinate_x"] = army.get("p").get("x")
            command["start_coordinate_y"] = army.get("p").get("y")
            command["target_coordinate_x"] = army.get("p").get("x")
            command["target_coordinate_y"] = army.get("p").get("y")
        commands.append(round_coordinates(command))
    return commands


def sort_warfare_units(game_id, data):
    data_armies = data["result"]["states"]["6"]["armies"]
    warfare_units = []
    for army_id in data_armies:
        army = data["result"]["states"]["6"]["armies"][army_id]
        if army_id == "@c" or "u" not in army:
            continue
        for unit in army["u"][1]:
            warfare_units.append({
                "army_id": int(army_id),
                "warfare_id": unit["id"],
                "warfare_type_id": unit["t"],
                "size": unit["s"],
                "health_point": round(unit.get("hp"), 2) if "hp" in army else None,
                "game_id": int(game_id)
            })
    return warfare_units


def round_coordinates(command):
    return {
        **command,
        "start_coordinate_x": round(command["start_coordinate_x"]),
        "start_coordinate_y": round(command["start_coordinate_y"]),
        "target_coordinate_x": round(command["target_coordinate_x"]),
        "target_coordinate_y": round(command["target_coordinate_y"]),
    }


if "__main__" == __name__:
    with open("../../../Conlyse_analytics/Data/Version 9/data2.json", "r") as file:
        data = json.loads(file.read())
    armies = sort_armies(231, data)
    commands = sort_commands(231, data)
    warfare_units = sort_warfare_units(231, data)
    with open("../../../Conlyse_analytics/sorted_data/armies_1.json", "w") as file:
        file.write(json.dumps(armies, indent=2, cls=DateTimeEncoder))
    with open("../../../Conlyse_analytics/sorted_data/commands_1.json", "w") as file:
        file.write(json.dumps(commands, indent=2, cls=DateTimeEncoder))
    with open("../../../Conlyse_analytics/sorted_data/warfare_units_1.json", "w") as file:
        file.write(json.dumps(warfare_units, indent=2, cls=DateTimeEncoder))
