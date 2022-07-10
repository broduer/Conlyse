import json
from os.path import exists
from os import path

folder_path = path.dirname(path.realpath(__file__))
file_path = "/".join(folder_path.split("/")[0:-1]) + "/Bot_Data.json"


def getBotData(game_id):
    if exists(file_path):
        with open(file_path) as file:
            try:
                data_json = json.loads(file.read())
            except ValueError:
                print("Error: Bot_Data File couldn't load")
                exit()
        if str(game_id) in data_json:
            return data_json[str(game_id)]
        print(f"Error: {game_id} not in Bot_Data File")
        exit()
    else:
        print("Error: Bot_Data File doesn't exists")


def setBotData(data):
    if exists(file_path):
        with open(file_path, "r") as file:
            try:
                data_json = json.loads(file.read())
            except ValueError:
                print("Error: Bot_Data File couldn't load")
                exit()
        if "stateIDs" in data:
            stateIDs = {**data_json.get(data["game_id"]).get("stateIDs"), **data.get("stateIDs")}
            tstamps = {**data_json.get(data["game_id"]).get("tstamps"), **data.get("tstamps")}
            data_json[data["game_id"]] = {**data_json[data["game_id"]], **data, "stateIDs": stateIDs, "tstamps": tstamps}
        else:
            data_json[data["game_id"]] = {**data_json[data["game_id"]], **data}
        with open(file_path, "w") as file:
            try:
                data = json.dumps(data_json, indent=2)
                file.write(data)
            except TypeError:
                return


def getStates(game_id, data):
    stateIDs = {}
    tstamps = {}
    if "states" in data["result"]:
        for state in data["result"]["states"]:
            if data["result"]["states"][state] == "java.util.HashMap":
                continue
            stateIDs[state] = data["result"]["states"][state]["stateID"]
            tstamps[state] = data["result"]["states"][state]["timeStamp"]
        return {"game_id": str(game_id), "stateIDs": stateIDs, "tstamps": tstamps}

    else:
        return {"game_id": str(game_id)}
