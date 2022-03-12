from datetime import datetime

from Bot_v2.constants import FACTIONS
from Bot_v2.sort import getSpecialNameCases, getCombinedNumber, getProvincefromName, getResearchID, getnormaltimestamp, \
    getWarheadTyp, getEndTime


class fastsort:
    def __init__(self, data):
        self.sorted_data = {
            "game": self.sort_game(data),
            "newspaper": self.sort_newspaper(data)
        }

    def sort_game(self, data_2):
        data_game = data_2["result"]["states"]["12"]
        return dict({
            "game_id": int(data_2["result"]["states"]["13"]["gameID"]),
            "scenario_id": int(data_game["scenarioID"]),
            "map_id": int(data_game["mapID"]),
            "start_time": int(data_game["startOfGame"]),
            "end_time": getEndTime(data_game["startOfGame"], data_2["result"]["states"]["12"]["endOfGame"],
                                   1 / data_2["result"]["states"]["12"]["timeScale"]),
            "current_time": getnormaltimestamp(data_game["timeStamp"]) if not data_2["result"]["states"]["12"][
                "gameEnded"] else None,
            "next_day_time": getnormaltimestamp(data_game["nextDayTime"]),
            "next_heal_time": getnormaltimestamp(data_game["nextHealTime"]),
        })

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
