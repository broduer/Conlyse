import json

import botdata
from Bot.bot import Bot
from time import sleep
import argparse

parser = argparse.ArgumentParser(prefix_chars="-")
parser.add_argument('-g', '--game_id', help='Game ID', required=True, type=int)
args = parser.parse_args()
game_data = [{}]*3


def refreshData():
    with Bot(False) as bot:
        game_data[1] = bot.scrap_dynamic(botdata.getBotData(args.game_id))
        sorted_data = bot.sort(args.game_id, game_data)
        print(sorted_data)
        botdata.setBotData(botdata.getStates(args.game_id, game_data[1]))


def refreshTokens():
    with Bot(True) as bot:
        bot.land_first_page()
        # Login to account and saving of new Tokens
        loginData = bot.loginBot(botdata.getBotData(args.game_id))
        botdata.setBotData(loginData)
        game_data[0], game_data[2] = bot.scrap_static(botdata.getBotData(args.game_id))


while True:
    with open(f"../../Conlyse_analytics/Version 5/data1.json") as file:
        game_data[0] = json.loads(file.read())
    with open(f"../../Conlyse_analytics/Version 5/data3.json") as file:
        game_data[2] = json.loads(file.read())
    refreshData()
    print(game_data[1]["result"])
    print(game_data[1]["result"]["states"].keys())
    sleep(6)
