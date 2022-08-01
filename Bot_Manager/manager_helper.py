from os.path import exists
import datetime
import json
import sys
import os
import getpass

class Helper():
    def __init__(self):
        self.locate_python = sys.executable
        folder_path = os.path.dirname(os.path.realpath(__file__))
        self.run_path = "/".join(folder_path.split("/")[0:-1]) + "/Bot_v2/run.py"
        self.bot_data_path = "/".join(folder_path.split("/")[0:-1]) + "/Bot_Data.json"

    def writeData(self, game_id, bot_username, bot_password, interval, fast_interval):
        if exists(self.bot_data_path):
            with open(self.bot_data_path, "r") as file:
                try:
                    data_json = json.loads(file.read())
                except ValueError:
                    pass
        with open(self.bot_data_path, "w") as file:
            try:
                data_json
            except NameError:
                data_json = dict({})
            data_json[game_id] = dict({
                "game_id": game_id,
                "bot_username": bot_username,
                "bot_password": bot_password,
            })
            file.write(json.dumps(data_json, indent=2))

    def removeData(self, game_id):
        if exists(self.bot_data_path):
            with open(self.bot_data_path, "r") as file:
                try:
                    data_json = json.loads(file.read())
                except ValueError:
                    return f"Error: Cant load File"
        else:
            return
        try:
            data_json.pop(f"{game_id}")
            with open(self.bot_data_path, "w") as file:
                file.write(json.dumps(data_json, indent=2))
            return f"Deleted {game_id} successfully"
        except:
            return f"Couldn't delete {game_id}"

    def listData(self):
        if exists(self.bot_data_path):
            with open(self.bot_data_path, "r") as file:
                try:
                    data_json = json.loads(file.read())
                except ValueError:
                    return f"Error: Cant load File"
            for bot_data in data_json:
                bot_data = data_json[bot_data]
                normal_sch = "Unknown"
                fast_sch = "Unknown"
                print(
                    f'{bot_data["game_id"]}: Username = {bot_data["bot_username"]}, Password = {bot_data["bot_password"]}, Next normal run: {normal_sch}, Next fast run: {fast_sch}'
                )
        else:
            return f"Error: No Bot_Data File"
