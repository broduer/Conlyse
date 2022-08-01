import json
import math
from datetime import datetime

from Bot.constants import FACTIONS


class sort:
    def __init__(self, game_id, data):
        self.game_id = game_id
        self.sorted_data = dict({})
        self.data = data
        if "result" not in data[1]:
            return
        print(self.data[1])
        states = self.data[1]["result"]["states"].keys()
        if "12" in states:
            self.sorted_data["game"] = self.sort_game(data[1])
        """
        if all([key in states for key in ["3", "12"]]):
            self.sorted_data["static_province"] = self.sort_static_provinces(data[0], data[1])
        """

        if "result" in data[2]:
            self.sorted_data["static_scenarios"] = self.sort_static_scenarios(data[2])

        if "1" in states:
            self.sorted_data["countries"] = self.sort_countries(data[1])
            self.sorted_data["teams"] = self.sort_teams(data[1])
            self.sorted_data["players"] = self.sort_players(data[1])

        if "3" in states:
            self.sorted_data["provinces"] = self.sort_provinces(data[0], data[1])

        if "4" in states:
            self.sorted_data["trades"] = self.sort_trades(data[1])

        if "2" in states:
            self.sorted_data["newspaper"] = self.sort_newspaper(data[1])

    def sort_game(self, data_2):
        data_game = data_2["result"]["states"]["12"]
        return dict({
            "game_id": self.game_id,
            "scenario_id": int(data_game["scenarioID"]),
            "map_id": int(data_game["mapID"]),
            "start_time": int(data_game["startOfGame"]),
            "end_time": getEndTime(data_game["startOfGame"], data_game["endOfGame"],
                                   1 / data_game["timeScale"]),
            "current_time": getnormaltimestamp(data_game["timeStamp"]) if not data_game["gameEnded"] else None,
            "next_day_time": getnormaltimestamp(data_game["nextDayTime"]),
            "next_heal_time": getnormaltimestamp(data_game["nextHealTime"]),
        })

    def sort_players(self, data_2):
        data_players = data_2["result"]["states"]["1"]["players"]
        players = dict({})
        for player in data_players:
            player = data_players[player]
            if "siteUserID" in player:
                if int(player["playerID"]) > 0:
                    players[int(player["playerID"])] = dict({
                        "player_id": int(player["playerID"]),
                        "site_user_id": int(player["siteUserID"]),
                        "name": player["name"],
                    })
        return players

    def sort_teams(self, data_2):
        data_teams = data_2["result"]["states"]["1"]["teams"]
        teams = dict({})
        for team in data_teams:
            team = data_teams[team]
            if "java.util.HashMap" in team:
                continue
            teams[int(team["teamID"])] = dict({
                "team_id": int(team["teamID"]),
                "leader_id": int(team["leaderID"]),
                "name": team["name"],
                "deleted": bool(team["disbanded"])
            })
        return teams

    def sort_countries(self, data_2):
        data_countries = data_2["result"]["states"]["1"]["players"]
        countries = dict({})
        for country in data_countries:
            country = data_countries[country]
            if "siteUserID" in country:
                if int(country["playerID"]) > 0:
                    countries[int(country["playerID"])] = dict({
                        "player_id": int(country["playerID"]),
                        "team_id": int(country["teamID"]),
                        "name": country["nationName"],
                        "capital_id": int(country["capitalID"]),
                        "defeated": bool(country["defeated"]),
                        "computer": bool(country["computerPlayer"]),
                        "site_user_id": int(country["siteUserID"]),
                    })
        return countries

    def sort_provinces(self, data_1, data_2):
        timestamp = data_2["result"]["states"]["3"]["timeStamp"]
        data_1_locations = data_1["locations"][1]
        data_2_locations = data_2["result"]["states"]["3"]["map"]["locations"][1]
        provinces = dict({})
        for province_2 in data_2_locations:
            province_1 = getProvincefromId(province_2["id"], data_1_locations)
            if province_1["@c"] == "p":
                if "sa" not in province_2:
                    stationary_army_id = 0
                else:
                    stationary_army_id = int(province_2["sa"])
                if "rp" not in province_2:
                    resource_production = 0
                else:
                    resource_production = int(province_2["rp"])
                if "m" not in province_2:
                    morale = 0
                else:
                    morale = int(province_2["m"])
                upgrades = dict({})
                for upgrade in province_2["us"][1]:
                    upgrades[upgrade["id"]] = dict({
                        "upgrade_id": int(upgrade["id"]),
                        "health": int(upgrade["c"]),
                    })
                provinces[province_1["id"]] = dict({
                    "province_location_id": int(province_1["id"]),
                    "owner_id": int(province_2["o"]),
                    "morale": int(morale),
                    "province_state_id": int(province_2["pst"]),
                    "stationary_army_id": stationary_army_id,
                    "victory_points": int(province_2["plv"]),
                    "resource_production": int(resource_production),
                    "tax_production": int(province_2["tp"]),
                    "current_time": datetime.fromtimestamp(getnormaltimestamp(timestamp)),
                    "map_id": int(self.data[1]["result"]["states"]["12"]["mapID"]),
                    "game_id": self.game_id,
                    "upgrades": upgrades,
                })
        return provinces

    def sort_trades(self, data_2):
        timestamp = data_2["result"]["states"]["4"]["timeStamp"]
        data_2_trades = data_2["result"]["states"]["4"]["asks"][1]
        trades = dict({})
        for resource in data_2_trades:
            for group in resource:
                if group == "ultshared.UltAskList":
                    continue
                for trade in group:
                    if trade["playerID"] == 0:
                        continue
                    trades[trade["orderID"]] = dict({
                        "order_id": int(trade["orderID"]),
                        "owner_id": int(trade["playerID"]),
                        "amount": int(trade["amount"]),
                        "resource_type": int(trade["resourceType"]),
                        "limit": int(trade["limit"]),
                        "buy": bool(trade["buy"]),
                        "current_time": datetime.fromtimestamp(getnormaltimestamp(timestamp)),
                    })
        return trades

    def sort_static_provinces(self, data_1, data_2):
        data_1_locations = data_1["locations"][1]
        data_2_locations = data_2["result"]["states"]["3"]["map"]["locations"][1]
        provinces = dict({})
        for province_2 in data_2_locations:
            province_1 = getProvincefromId(province_2["id"], data_1_locations)
            if province_2["@c"] == "p":
                if province_2["pst"] > 52:
                    typ = 1
                else:
                    typ = 2
                if "co" in province_2:
                    coastal = True
                else:
                    coastal = False
                print(province_2)
                provinces[province_2["id"]] = dict({
                    "province_location_id": int(province_2["id"]),
                    "map_id": self.data[1]["result"]["states"]["12"]["mapID"],
                    "typ": typ,
                    "name": province_2["n"],
                    "coordinate_x": int(province_1["c"]["x"]),
                    "coordinate_y": int(province_1["c"]["y"]),
                    "mainland_id": int(province_1["ci"][0]),
                    "region": int(province_1["r"]),
                    "base_production": int(province_2["bp"]),
                    "terrain_type": int(province_1["tt"]),
                    "resource_production_type": int(province_2["r"]),
                    "b": province_1["b"],
                    "coastal": coastal,
                })

            else:
                provinces[province_1["id"]] = dict({
                    "province_location_id": int(province_1["id"]),
                    "map_id": self.data[1]["result"]["states"]["12"]["mapID"],
                    "typ": 3,
                    "name": province_2["n"],
                    "coordinate_x": int(province_1["c"]["x"]),
                    "coordinate_y": int(province_1["c"]["y"]),
                    "mainland_id": None,
                    "region_id": None,
                    "base_production": None,
                    "terrain_type": int(province_1["tt"]),
                    "resource_production_type": None,
                    "b": province_1["b"],
                    "coastal": None,
                })
        return provinces

    def sort_static_scenarios(self, data_3):
        data_3_scenarios = data_3["result"]
        scenarios = dict({})
        for item in data_3_scenarios:
            if item["@c"] == "ultshared.UltScenario":
                if "scenarioSpeedUpFactor" in item["options"]:
                    speed = int(item["options"]["scenarioSpeedUpFactor"])
                else:
                    speed = 1
                scenarios[item["itemID"]] = dict({
                    "scenario_id": int(item["itemID"]),
                    "map_id": int(item["mapID"]),
                    "name": item["ingameName"],
                    "speed": speed,
                })
        return scenarios

    def sort_newspaper(self, data_2):
        # newspaper_articles = newspaper_data["result"]["articles"][1]
        researches = data_2["result"]["states"]["11"]["researchTypes"]
        countrys = data_2["result"]["states"]["1"]["players"]
        provinces = data_2["result"]["states"]["3"]["map"]["locations"][1]
        researches.pop("@c")
        articles = []
        newspaper_articles = data_2["result"]["states"]["2"]["articles"][1]
        for article in newspaper_articles:
            messages = article["messageBody"].split("<p>")
            for message in messages:
                message = message.replace(":", "")
                # Does formatting for Weapons which are lost from a country
                if "lost" in message:
                    mode = 1
                    faction = FACTIONS.get(countrys[f'{article["senderID"]}']["faction"])
                    typ = getSpecialNameCases(f"{message.split('lost')[1][3:-4].split(' over')[0]}", faction)
                    time = message.split(" ")[3]
                    count = getCombinedNumber(f"{message.split('lost')[1][1]}",
                                              f"{message.split('lost')[1][2]}") * -1
                    division = getCombinedNumber(f"{message.split('The')[1][1]}", f"{message.split('The')[1][2]}")
                    location = None
                    if "over" in message and False == ("over the" in message):
                        location = getProvincefromName(message.split("over")[1].split("\'")[1], provinces)["id"]
                    if "over the" in message:
                        location = \
                            getProvincefromName(message.split("over the ")[1].split("</p>")[0][0:-1], provinces)["id"]
                    new_article = {
                        "msg_typ": 2,
                        "country_id": article["senderID"],
                        "wtyp": getResearchID(typ, researches, mode, faction),
                        "division": division,
                        "count": count,
                        "time": datetime.fromtimestamp(getnormaltimestamp(time)),
                    }
                    if location is not None:
                        new_article["location"] = location
                    for whtyp in ["Conventional", "Nuclear", "Chemical"]:
                        if whtyp in message:
                            new_article["whtyp"] = getWarheadTyp(
                                message.split('lost')[1][3:-4].split(' over')[0].split(" ")[0])
                    articles.append(new_article)

                # If a country either builds a new Aircraft Carrier or Officer
                if "recruits new" in message or "builds new" in message:
                    faction = FACTIONS.get(countrys[f'{article["senderID"]}']["faction"])
                    if "recruits new" in message:
                        typ = f"{message.split('recruits new')[1][1:-5]}"
                        mode = 1
                    elif "builds new" in message:
                        typ = message.split('builds new')[1].split("\"")[0][1:-1]
                        mode = 2
                    else:
                        typ = "Unknown"
                        mode = 0
                    time = message.split(" ")[3]
                    articles.append({
                        "msg_typ": 2,
                        "country_id": article["senderID"],
                        "wtyp": getResearchID(typ, researches, mode, faction),
                        "count": 1,
                        "time": datetime.fromtimestamp(getnormaltimestamp(time)),
                    })
                # If a Country starts a weapon Program either nuclear or chemical
                if "According to an unnamed" in message:
                    if "nuclear" in message:
                        wtyp = 2899
                    elif "chemical" in message:
                        wtyp = 2900
                    else:
                        wtyp = 0
                    time = article["timeStamp"]
                    articles.append({
                        "msg_typ": 3,
                        "country_id": article["senderID"],
                        "wtyp": wtyp,
                        "time": datetime.fromtimestamp(getnormaltimestamp(time)),
                    })
                if "has been destroyed by" in message or "was severely damaged by" in message or "was attacked by" in message:
                    country_id = message.split("countryLink")[2].split("\'")[3]
                    faction = FACTIONS.get(countrys[country_id]["faction"])
                    typ = message.split("by ")[1].split("(")[0].split(" ")[3:-1]
                    division = getCombinedNumber(f"{message.split('by ')[1].split('(')[0].split(' ')[1][0]}",
                                                 f"{message.split('by ')[1].split('(')[0].split(' ')[1][1]}")
                    time = message.split(" ")[3]
                    count = 1
                    whtyp = None
                    wtyp = None
                    if len(typ) < 2:
                        continue
                    if "ICBM" in message:
                        wtyp = 2882
                        whtyp = 2899
                        count = -1
                    if "Cruise" in typ[1]:
                        count = -1
                        wtyp = 2840
                        whtyp = getWarheadTyp(typ[0])
                    if "Ballistic" == typ[1]:
                        count = -1
                        wtyp = 2861
                        whtyp = getWarheadTyp(typ[0])
                    if "Stealth" in typ[0]:
                        wtyp = getResearchID(f"{typ[0]} {typ[1]}", researches, 1, faction)
                        if len([article_f for article_f in articles if
                                article_f["country_id"] == int(country_id) and article_f["wtyp"] == wtyp]) < 1:
                            articles.append({
                                "msg_typ": 3,
                                "country_id": int(country_id),
                                "wtyp": wtyp,
                                "time": datetime.fromtimestamp(getnormaltimestamp(time)),
                            })
                    if count == -1:
                        if len([article_f for article_f in articles if
                                article_f["time"] == getnormaltimestamp(time) and article_f[
                                    "division"] == division]) < 1:
                            articles.append({
                                "msg_typ": 2,
                                "country_id": article["senderID"],
                                "wtyp": wtyp,
                                "whtyp": whtyp,
                                "division": division,
                                "count": count,
                                "time": datetime.fromtimestamp(getnormaltimestamp(time)),
                            })
        # print(json.dumps([article for article in articles if article.get("wtyp") == 2861],
        # print(json.dumps([article for article in articles if article.get("whtyp") == 2899], indent=2))
        # print(len([article for article in articles if article.get("whtyp") == 2899]))
        # print(json.dumps(articles, indent=2))
        return articles


def getProvincefromId(province_id, data):

    for number, province in enumerate(data):
        print(province_id, province)
        if number > 50:
            break
    return [province for province in data if int(province["id"]) == int(province_id)][0]


def getProvincefromName(name, data):
    return [province for province in data if province["n"] == name][0]


def getCombinedNumber(number_1, number_2):
    try:
        number_1 = int(number_1)
        number_2 = int(number_2)
        return int(f"{number_1}{number_2}")
    except ValueError:
        return int(f"{number_1}")


def getSpecialNameCases(typ, faction):
    if typ.startswith("Conventional") or typ.startswith("Nuclear") or typ.startswith("Chemical"):
        typ = f'{typ.split(" ")[1]} {typ.split(" ")[2]}'
    if typ.startswith("Elite"):
        typ = typ.replace("Elite", "Season")
    if "Airmobile Infantry" in typ:
        typ = typ.replace("Airmobile", "Airborne")
    if "Naval Infantry" in typ and faction != "US":
        typ = f"{typ} EU & RU"
    if "AWACS" in typ and faction != "US":
        typ = f"{typ} EU & RU"
    return typ


def getWarheadTyp(typ):
    warheads = {
        "Conventional": 2889,
        "Nuclear": 2899,
        "Chemical": 2900,
    }
    return warheads.get(typ)


def getResearchID(name, researches, mode, faction="", ):
    filtered = []
    if mode == 1:
        if faction != "":
            filtered = [research for research in researches if isName(researches[research], f"{name} {faction}")]
        if len(filtered) == 0:
            filtered = [research for research in researches if isName(researches[research], name)]
        if len(filtered) == 0:
            filtered = [research for research in researches if isName(researches[research], f"{name} 1 {faction}")]
    elif mode == 2:
        filtered = [research for research in researches if isFactionName(researches[research], name, faction)]
    else:
        return 0
    research_id = sorted(filtered, key=lambda item: researches[item]["itemID"])

    if len(research_id) == 0:
        return 0
    return int(research_id[0])


def isName(research, name):
    return research["name"] == name


def isFactionName(research, name, faction):
    if research["nameFaction1"] == name:
        if research["name"].endswith(faction):
            return True
    return False


def getEndTime(start_time, end_time, speed):
    if int(end_time) != 0:
        difference = (end_time - start_time) * speed
        new_end_time = start_time + difference
        return round(new_end_time)
    else:
        return 0


def getnormaltimestamp(timestamp):
    try:
        timestamp = int(timestamp)
        if getIntegerPlaces(timestamp) == 13:
            return round(timestamp / 1000)
        else:
            return timestamp
    except:
        return None


def getIntegerPlaces(theNumber):
    if theNumber <= 999999999999997:
        return int(math.log10(theNumber)) + 1
    else:
        counter = 15
        while theNumber >= 10 ** counter:
            counter += 1
        return counter


def getTitleCases(title):
    cases = ["reports casualties", "recruits new"]
    for case in cases:
        if case in title:
            return True
    return False


def startSort():
    data = []
    for i in range(1, 4):
        with open(f"../../Conlyse_analytics/Version 1/data{i}.json") as file:
            data.append(json.loads(file.read()))
    sort = Sort(data)
    print(sort.sorted_data)
