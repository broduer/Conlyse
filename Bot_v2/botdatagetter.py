import json
import os
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
        for bot_data in data_json:
            bot_data = data_json[bot_data]
            if bot_data["game_id"] == game_id:
                return bot_data
        print(f"Error: {game_id} not in Bot_Data File")
        exit()
    else:
        print("Error: Bot_Data File doesn't exists")
