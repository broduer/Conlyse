import json
import os.path

from Bot_Manager import manager_helper

import botdatagetter
from Bot_v2.bot import Bot
from time import time
import argparse

from Bot_v2.fastrequest import fastrequest
from Bot_v2.fastsort import fastsort
from Bot_v2.sql.fastsql_filler import Filler

parser = argparse.ArgumentParser(prefix_chars="-")
parser.add_argument('-g', '--game_id', help='Game ID', required=True, type=int)
parser.add_argument('-f', '--fast', help='Fast Login',  nargs='?', default=False, const=True)
args = parser.parse_args()

time1 = time()
browser = True

if args.fast:
    with open(f"fastlogin_{args.game_id}.json", "r") as file:
        logindata = json.loads(file.read())
    data = fastrequest(logindata).data
    sorted_data = fastsort(data).sorted_data
    Filler(sorted_data)


else:
    with Bot(browser) as bot:
        if browser:
            bot.land_first_page()
            loginData = bot.loginBot(botdatagetter.getBotData(args.game_id))
        time2 = time()
        data = bot.scrap(loginData)
        sorted_data = bot.sort(data)
        time3 = time()
        time4 = time()
        bot.fillSQL(sorted_data)
        if sorted_data["game"]["end_time"] is int:
            manager_helper.Helper().removeData(sorted_data["game"]["game_id"])
            if os.path.exists(f"fastlogin_{sorted_data['game']['game_id']}.json"):
                os.remove(f"fastlogin_{sorted_data['game']['game_id']}.json")
