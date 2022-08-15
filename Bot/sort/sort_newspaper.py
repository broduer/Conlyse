from datetime import datetime

from Bot.constants import FACTIONS
from Bot.sort.helper import get_province_from_name, get_normal_timestamp, get_combined_number


def sort_newspaper(data_2, data_2_old):
    # newspaper_articles = newspaper_data["result"]["articles"][1]
    researches = data_2_old["result"]["states"]["11"]["researchTypes"]
    if "@c" in researches:
        researches.pop("@c")
    countrys = data_2_old["result"]["states"]["1"]["players"]
    provinces = data_2_old["result"]["states"]["3"]["map"]["locations"][1]
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
                count = get_combined_number(f"{message.split('lost')[1][1]}",
                                          f"{message.split('lost')[1][2]}") * -1
                division = get_combined_number(f"{message.split('The')[1][1]}", f"{message.split('The')[1][2]}")
                location = None
                if "over" in message and False == ("over the" in message):
                    location = get_province_from_name(message.split("over")[1].split("\'")[1], provinces)["id"]
                if "over the" in message:
                    location = \
                        get_province_from_name(message.split("over the ")[1].split("</p>")[0][0:-1], provinces)["id"]
                new_article = {
                    "msg_typ": 2,
                    "country_id": article["senderID"],
                    "wtyp": getResearchID(typ, researches, mode, faction),
                    "division": division,
                    "count": count,
                    "time": datetime.fromtimestamp(get_normal_timestamp(time)),
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
                    "time": datetime.fromtimestamp(get_normal_timestamp(time)),
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
                    "time": datetime.fromtimestamp(get_normal_timestamp(time)),
                })
            if "has been destroyed by" in message or "was severely damaged by" in message or "was attacked by" in message:
                country_id = message.split("countryLink")[2].split("\'")[3]
                faction = FACTIONS.get(countrys[country_id]["faction"])
                typ = message.split("by ")[1].split("(")[0].split(" ")[3:-1]
                division = get_combined_number(f"{message.split('by ')[1].split('(')[0].split(' ')[1][0]}",
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
                            "time": datetime.fromtimestamp(get_normal_timestamp(time)),
                        })
                if count == -1:
                    if len([article_f for article_f in articles if
                            article_f["time"] == get_normal_timestamp(time) and article_f[
                                "division"] == division]) < 1:
                        articles.append({
                            "msg_typ": 2,
                            "country_id": article["senderID"],
                            "wtyp": wtyp,
                            "whtyp": whtyp,
                            "division": division,
                            "count": count,
                            "time": datetime.fromtimestamp(get_normal_timestamp(time)),
                        })
    # print(json.dumps([article for article in articles if article.get("wtyp") == 2861],
    # print(json.dumps([article for article in articles if article.get("whtyp") == 2899], indent=2))
    # print(len([article for article in articles if article.get("whtyp") == 2899]))
    # print(json.dumps(articles, indent=2))
    return articles


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
    if "Insurgent" in typ:
        typ = "Insurgent"
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
            filtered = [research for research in researches if is_name(researches[research], f"{name} {faction}")]
        if len(filtered) == 0:
            filtered = [research for research in researches if is_name(researches[research], name)]
        if len(filtered) == 0:
            filtered = [research for research in researches if is_name(researches[research], f"{name} 1 {faction}")]
    elif mode == 2:
        filtered = [research for research in researches if is_faction_name(researches[research], name, faction)]
    else:
        return 0
    research_id = sorted(filtered, key=lambda item: researches[item]["itemID"])

    if len(research_id) == 0:
        return 0
    return int(research_id[0])


def is_name(research, name):
    return research["name"] == name


def is_faction_name(research, name, faction):
    if research["nameFaction1"] == name:
        if research["name"].endswith(faction):
            return True
    return False
