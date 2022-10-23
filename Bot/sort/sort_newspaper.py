import json
import re
from datetime import datetime

from game_constants import FACTIONS, STARTER_UNIT_NAMES
from helper import get_normal_timestamp, get_combined_number, DateTimeEncoder
from deepdiff import DeepDiff


class NewspaperSorter:
    def __init__(self, game_id, current_day, data_2, data_2_old):
        self.warfare_unit_types = data_2_old["result"]["states"]["11"]["allUnitTypes"].copy()
        self.data_researches = data_2_old["result"]["states"]["11"]["researchTypes"].copy()
        if "@c" in self.warfare_unit_types:
            self.warfare_unit_types.pop("@c")
        if "@c" in self.data_researches:
            self.data_researches.pop("@c")

        self.countries = data_2_old["result"]["states"]["1"]["players"]
        self.provinces = data_2_old["result"]["states"]["3"]["map"]["locations"][1]
        self.data_articles = data_2["result"]["states"]["2"]["articles"][1]
        self.game_id = int(game_id)
        self.current_day = current_day
        self.army_loses_gains = []
        self.researches = []

    def run(self):
        for article in self.data_articles:
            messages = article["messageBody"].split("<p>")
            for message in messages:
                message = message.replace(":", "")
                country_id = article["senderID"]
                # Does formatting for Weapons which are lost from a country
                if "lost" in message:
                    warfare_name = message.split('lost')[1][3:-4].split(' over')[0]
                    warfare_type_ids = self.get_warfare_type_ids_from_name(warfare_name, article["senderID"])
                    time = datetime.fromtimestamp(get_normal_timestamp(message.split(" ")[3]))
                    count = get_combined_number(f"{message.split('lost')[1][1]}",
                                                f"{message.split('lost')[1][2]}") * -1
                    division = get_combined_number(f"{message.split('The')[1][1]}", f"{message.split('The')[1][2]}")
                    if not warfare_type_ids:
                        continue
                    self.army_loses_gains.append({
                        "owner_id": country_id,
                        "warfare_type_id": min(warfare_type_ids),
                        "division": division,
                        "count": count,
                        "game_id": self.game_id,
                        "time": time,
                    })
                    # Not safe that country has researched it because you have some starter units of these types
                    if warfare_name in STARTER_UNIT_NAMES:
                        continue
                    research_ids_from_warfare_type = self.get_research_ids_from_name(warfare_name, country_id)
                    if research_ids_from_warfare_type:
                        self.researches.append({
                            "owner_id": country_id,
                            "column_id": self.get_column_id(min(research_ids_from_warfare_type)),
                            "research_min_id": min(research_ids_from_warfare_type),
                            "research_max_id": max(research_ids_from_warfare_type),
                            "game_id": self.game_id,
                            "valid_from": time,
                            "valid_until": time,
                        })
                # If a country either builds a new Aircraft Carrier or Officer
                elif "recruits new" in message or "builds new" in message:
                    if "recruits new" in message:
                        warfare_name = message.split('recruits new')[1][1:-5]
                    elif "builds new" in message:
                        warfare_name = message.split('builds new')[1].split("\"")[0][1:-1]
                    warfare_type_id = min(self.get_warfare_type_ids_from_name(warfare_name, article["senderID"]))
                    time = datetime.fromtimestamp(get_normal_timestamp(message.split(" ")[3]))
                    self.army_loses_gains.append({
                        "owner_id": country_id,
                        "warfare_type_id": warfare_type_id,
                        "count": 1,
                        "game_id": self.game_id,
                        "time": time,
                    })
                    research_ids_from_warfare_type = self.get_research_ids_from_name(warfare_name, country_id)
                    if research_ids_from_warfare_type:
                        self.researches.append({
                            "owner_id": country_id,
                            "column_id": self.get_column_id(min(research_ids_from_warfare_type)),
                            "research_min_id": min(research_ids_from_warfare_type),
                            "research_max_id": max(research_ids_from_warfare_type),
                            "game_id": self.game_id,
                            "valid_from": time,
                            "valid_until": time,
                        })
                # If a Country starts a weapon Program either nuclear or chemical
                elif "According to an unnamed" in message:
                    if "nuclear" in message:
                        research_id = 2899
                    elif "chemical" in message:
                        research_id = 2900
                    else:
                        research_id = 0
                    time = datetime.fromtimestamp(get_normal_timestamp(article["timeStamp"]))
                    self.researches.append({
                        "owner_id": country_id,
                        "column_id": research_id,
                        "research_min_id": research_id,
                        "research_max_id": research_id,
                        "game_id": self.game_id,
                        "valid_from": time,
                        "valid_until": time,
                    })
                if "has been destroyed by" in message or "was severely damaged by" in message or "was attacked by" in message:
                    country_id = int(message.split("countryLink")[2].split("\'")[3])
                    warfare_name = " ".join([part for part in message.split("by ")[1].split("(")[0].split(" ")
                                             if not re.findall('[0-9]+', part)
                                             and not part == "the"
                                             and not part == "a"
                                             and not part == ""])
                    research_ids_from_warfare_type = self.get_research_ids_from_name(warfare_name, country_id)
                    time = datetime.fromtimestamp(get_normal_timestamp(message.split(" ")[3]))

                    # Not safe that country has researched it because you have some starter units of these types
                    if warfare_name in STARTER_UNIT_NAMES:
                        continue
                    if research_ids_from_warfare_type:
                        self.researches.append({
                            "owner_id": country_id,
                            "column_id": self.get_column_id(min(research_ids_from_warfare_type)),
                            "research_min_id": min(research_ids_from_warfare_type),
                            "research_max_id": max(research_ids_from_warfare_type),
                            "game_id": self.game_id,
                            "valid_from": time,
                            "valid_until": time,
                        })

        # Filter Researches
        filtered_researches = {}
        for research in self.researches:
            filtered_research = self.get_filtered_research(research, filtered_researches)
            if filtered_research:
                filtered_researches[f'{research["owner_id"]}_{research["research_min_id"]}'] = {
                    "owner_id": research["owner_id"],
                    "column_id": research["column_id"],
                    "research_min_id": research["research_min_id"],
                    "research_max_id": min(research["research_max_id"], filtered_research["research_max_id"]),
                    "valid_from": min(research["valid_from"], filtered_research["valid_from"]),
                    "valid_until": max(research["valid_until"], filtered_research["valid_until"]),
                    "game_id": self.game_id,
                }
        self.researches = [filtered_research for filtered_research in filtered_researches.values()]

    def get_filtered_research(self, research, filtered_researches):
        for filtered_research in filtered_researches.values():
            changes = DeepDiff(filtered_research, research,
                               exclude_paths=["root['research_max_id']",
                                              "root['valid_from']",
                                              "root['valid_until']"])
            if not changes:
                return filtered_research
        else:
            if len(filtered_researches.values()) == 0:
                return research
            try:
                next(filtered_research for filtered_research in filtered_researches.values()
                     if filtered_research["owner_id"] == research["owner_id"]
                     and filtered_research["column_id"] == research["column_id"])
            except StopIteration:
                return research
            return None

    # Get all possible warfare_type_ids from Name
    def get_warfare_type_ids_from_name(self, name, country_id):
        faction = self.get_faction(country_id)

        warfare_units = []

        # formationNameSmall or formationNameBig
        for warfare_unit in self.warfare_unit_types.values():
            if warfare_unit["formationNameSmall"] == name \
                    or warfare_unit["formationNameBig"] == name \
                    or warfare_unit["typeName"] == name \
                    or warfare_unit["nameFaction1"] == name:
                research = self.get_research_from_warfare_type_id(warfare_unit["itemID"])
                if not research:
                    continue
                # Research only possible if it is available at current day
                if research["dayAvailable"] > self.current_day:
                    continue
                if "factionSpecificResearchConfig" in research:
                    if faction in research["factionSpecificResearchConfig"]["factions"][1]:
                        warfare_units.append(warfare_unit["itemID"])
                else:
                    faction_short = FACTIONS.get(faction)
                    if faction_short in research["name"]:
                        warfare_units.append(warfare_unit["itemID"])
                    elif not any([every_faction in research["name"] for every_faction in FACTIONS.values()]):
                        warfare_units.append(warfare_unit["itemID"])
        if warfare_units and max(warfare_units) - min(warfare_units) == (len(warfare_units)) - 1:
            return warfare_units
        else:
            return None

    # Get all possible Researches from name
    def get_research_ids_from_name(self, name, country_id):
        warfare_type_ids = self.get_warfare_type_ids_from_name(name, country_id)
        if not warfare_type_ids:
            return None
        research_ids_from_warfare_type = [self.get_research_id_from_warfare_type_id(warfare_type_id)
                                          for warfare_type_id in warfare_type_ids]
        return research_ids_from_warfare_type

    def get_required_research(self, research_id, required_researches):
        research = self.data_researches[str(research_id)]
        for required_research in research["requiredResearches"]:
            if "@c" == required_research:
                continue
            required_research = int(required_research)
            if required_research not in required_researches:
                required_researches.append(required_research)
                self.get_required_research(required_research, required_researches)
        return required_researches

    def get_column_id(self, research_id):
        research = self.data_researches[str(research_id)]
        for required_research in research["requiredResearches"]:
            if "@c" == required_research:
                continue
            required_research = int(required_research)
            if research_id - required_research == 1:
                self.get_column_id(required_research)

        return research_id

    def get_faction(self, country_id):
        try:
            country = next(country for country in self.countries.values()
                           if country != "java.util.HashMap" and country["playerID"] == country_id)
            return country["faction"]
        except StopIteration:
            return None

    def get_research_from_warfare_type_id(self, warfare_id):
        warfare_unit = self.warfare_unit_types[str(warfare_id)]
        for key in warfare_unit["requiredResearches"].keys():
            try:
                int(key)
                return self.data_researches[key]
            except ValueError:
                continue
        return None

    def get_research_id_from_warfare_type_id(self, warfare_id):
        warfare_unit = self.warfare_unit_types[str(warfare_id)]
        for key in warfare_unit["requiredResearches"].keys():
            try:
                return int(key)
            except ValueError:
                continue
        return None


if "__main__" == __name__:
    with open("../../../Conlyse_analytics/Data/Version 9/data2.json", "r") as f:
        data_2_old = json.loads(f.read())
    newspaper_sorter = NewspaperSorter(12231, 4, data_2_old, data_2_old)
    newspaper_sorter.run()
