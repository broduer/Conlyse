import json
import logging
import time
from dotenv import load_dotenv
from os import getenv

from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from Bot.sort.helper import DateTimeEncoder, compare
from .Models import Scenario, Trade, Player, Province, StaticProvince, StaticCountry, Country, Game, \
    GameHasPlayer, Team, \
    Building, ArmyLossesGain, Research, Army, Command, WarfareUnit, GamesAccount

load_dotenv()


class Filler:
    def __init__(self, game_id, data, game_detail):
        connection_string = f"mysql+mysqlconnector://{getenv('DB_USERNAME')}:{getenv('DB_PASSWORD')}@{getenv('DB_IP')}/{getenv('DB_NAME')}?charset=utf8mb4"

        engine = create_engine(connection_string, echo=False)
        session_maker = sessionmaker()
        session_maker.configure(bind=engine)
        self.session = session_maker()
        self.data = data
        self.timestamp = data["timestamp"]
        self.game_id = int(game_id)
        self.map_id = data["map_id"]
        self.game_detail = game_detail

        self.static_provinces = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.commit()
        self.session.close()

    def fill(self):
        logging.debug(f"Filling Game {self.game_id}")
        t1 = time.monotonic()
        keys = list(self.data.keys())
        if "static_provinces" in keys:
            logging.log(5, "Filling static_provinces and static_scenarios")
            self.fill_static_provinces(self.data["static_provinces"])
            self.fill_static_countries(self.data["static_countries"])
            self.fill_static_scenarios(self.data["static_scenarios"])
            self.session.commit()
            self.session.flush()

        self.fill_game_update(self.data["timestamp"])
        if "game" in keys:
            self.fill_game(self.data["game"])
            self.session.commit()
            if self.data["game"]["end_time"] is not None:
                self.remove_game_account()
                return

        if "teams" in keys:
            self.fill_teams(self.data["teams"])
            self.session.commit()

        if all(ele in keys for ele in ["players", "countries"]):
            logging.log(5, f"Filling {len(self.data['players'].values())} Players and Countries")
            self.fill_player_country(self.data["players"], self.data["countries"])

        if "trades" in keys:
            self.fill_trades(self.data["trades"])

        if "army_losses_gains" in keys:
            self.fill_army_gains_losses(self.data["army_losses_gains"])

        if "researches" in keys:
            self.fill_researches(self.data["researches"])

        if "provinces" in keys:
            self.fill_provinces(self.data["provinces"])
            self.fill_buildings(self.data["buildings"])

        if "armies" in keys:
            self.fill_armies(self.data["armies"])
            self.session.commit()
            self.fill_commands(self.data["commands"])
            self.session.flush()
            self.session.commit()
            self.fill_warfare_units(self.data["warfare_units"])
            self.session.commit()

        t2 = time.monotonic()
        print(f"G: {self.game_id} Filler Time -> {t2 - t1}")
        self.session.commit()

    def remove_game_account(self):
        self.session.query(GamesAccount).filter_by(account_id=self.game_detail.account_id,
                                                   game_id=self.game_detail.game_id).delete()
        self.session.commit()

    def fill_game_update(self, timestamp):
        game_sql = self.session.query(Game).filter_by(game_id=self.game_id).scalar()
        game_sql.current_time = timestamp

    def fill_game(self, data):
        game_sql = self.session.query(Game).filter_by(game_id=data["game_id"]).scalar()
        if game_sql is None:
            new_game = Game(
                game_id=data["game_id"],
                scenario_id=data["scenario_id"],
                start_time=data["start_time"],
                end_time=data["end_time"],
                current_time=data["current_time"],
                next_day_time=data["next_day_time"],
                next_heal_time=data["next_heal_time"],
            )
            self.session.add(new_game)
        else:
            if data["end_time"]:
                game_sql.end_time = data["end_time"]
                game_sql.next_day_time = None
                game_sql.next_heal_time = None
            else:
                game_sql.next_day_time = data["next_day_time"]
                game_sql.current_time = data["current_time"]
                game_sql.next_heal_time = data["next_heal_time"]

    def fill_player_country(self, data_players, data_countries):
        # Retrieve the latest Data from DB
        counties = self.session.query(Country).filter_by(game_id=self.game_id, valid_until=None).all()
        static_counties = self.session.query(StaticCountry).filter_by(map_id=self.map_id).all()
        players = self.session.query(Player).join(GameHasPlayer).filter_by(game_id=self.game_id).all()
        teams = self.session.query(Team).filter_by(game_id=self.game_id).all()

        new_countries = []
        update_countries = []
        new_player_countries = []
        players_names = [player.name for player in players]
        countries_country_id = [country.country_id for country in counties]
        for data_player, data_country in zip(data_players, data_countries):
            data_player = data_players[data_player]
            data_country = data_countries[data_country]

            # Add the new Player if the name is not in database
            if data_player["name"] not in players_names:
                player_sql = Player(
                    site_user_id=data_player["site_user_id"],
                    name=data_player["name"],
                )
                self.session.add(player_sql)

                # Flush to get its new player_id(autoincrement) to add game_has_player Entry
                self.session.flush()
                new_player_countries.append({
                    "game_id": self.game_id,
                    "player_id": player_sql.player_id,
                    "country_id": data_country["country_id"],
                })

            # Get the universal_team_id and update the country_dict
            try:
                team_id = next(
                    team.universal_team_id for team in teams if team.team_id == data_country["team_id"])
            except StopIteration:
                team_id = None
            # Get the static_country_id and update the country_dict
            try:
                static_country_id = next(
                    static_country.static_country_id for static_country in static_counties
                    if static_country.country_id == data_country["country_id"])
            except StopIteration:
                static_country_id = None

            new_country = {**data_country, "team_id": team_id, "static_country_id": static_country_id}
            # New Country if this country_id does not exist for this Game.
            if new_country["country_id"] not in countries_country_id:
                new_countries.append(new_country)
            else:
                # SQLALCHEMY object to dict
                country_sql_dict = object_as_dict(counties[countries_country_id.index(new_country["country_id"])])
                # Compare New Country to the latest in DB with some exceptions.
                changes = compare(country_sql_dict,
                                  new_country,
                                  ["universal_country_id", "valid_from", "valid_until"])
                if changes:
                    logging.log(5, f"UPDATE Country {new_country['country_id']}"
                                   f"{country_sql_dict}"
                                   f"{new_country}")
                    update_countries.append({
                        **country_sql_dict,
                        "valid_until": data_country["valid_from"]
                    })
                    new_countries.append(new_country)
        self.session.bulk_insert_mappings(Country, new_countries)
        self.session.bulk_update_mappings(Country, update_countries)
        self.session.bulk_insert_mappings(GameHasPlayer, new_player_countries)

    def fill_teams(self, data):
        teams = self.session.query(Team).filter_by(game_id=self.game_id).all()
        teams_team_id = [team.team_id for team in teams]
        new_teams = []
        updated_teams = []
        for team in data:
            team = data[team]
            if team["team_id"] not in teams_team_id:
                new_teams.append(team)
                logging.log(5, f"INSERT Team: {json.dumps(team, cls=DateTimeEncoder, indent=2)}")
            else:
                team_exists = object_as_dict(teams[teams_team_id.index(team["team_id"])])
                changes = compare(team_exists, team, ["universal_team_id"])
                if changes:
                    updated_teams.append({
                        **team_exists,
                        "leader_id": team["leader_id"],
                        "name": team["name"],
                        "deleted": team["deleted"],
                    })
                    logging.log(5, f"UPDATE Team {team['team_id']}"
                                   f"{team_exists}"
                                   f"{team}")
        self.session.bulk_insert_mappings(Team, new_teams)
        self.session.bulk_update_mappings(Team, updated_teams)

    def fill_trades(self, data):
        old_trades = self.session.query(Trade).filter_by(game_id=self.game_id, valid_until=None).all()
        old_order_ids = [trade.order_id for trade in old_trades]

        new_order_ids = [trade["order_id"] for trade in data.values()]
        new_trades = []
        update_trades = []
        # Add new trades or update existing trades
        for trade in data.values():
            if trade["order_id"] not in old_order_ids:
                new_trades.append(trade)
                logging.log(5, f"INSERT Trade: {json.dumps(trade, cls=DateTimeEncoder, indent=2)}")
            else:
                old_trade_sql = next(
                    old_trade_sql for old_trade_sql in old_trades if old_trade_sql.order_id == trade["order_id"])
                old_trade_dict = object_as_dict(old_trade_sql)
                changes = compare(old_trade_dict,
                                  trade,
                                  ["trade_id",
                                   "valid_from",
                                   "valid_until"])
                if changes:
                    logging.log(5, f"UPDATE Trade {trade['order_id']}"
                                   f"{old_trade_dict}"
                                   f"{trade}")
                    update_trades.append({
                        **old_trade_dict,
                        "valid_until": trade["valid_from"]
                    })
                    new_trades.append(trade)

        # Check if new Trade doesn't exist
        for old_trade in old_trades:
            if old_trade.order_id not in new_order_ids:
                logging.log(5, f"DELETE Trade {old_trade.order_id}")
                old_trade_dict = object_as_dict(old_trade)
                update_trades.append({
                    **old_trade_dict,
                    "valid_until": self.timestamp
                })
        self.session.bulk_insert_mappings(Trade, new_trades)
        self.session.bulk_update_mappings(Trade, update_trades)

    def fill_provinces(self, data):
        old_provinces = self.session.query(Province).filter_by(valid_until=None, game_id=self.game_id).all()
        old_provinces_dict = {old_province.static_province_id: object_as_dict(old_province)
                              for old_province in old_provinces}

        new_provinces = []
        update_provinces = []

        for province in data.values():
            static_province = self.get_static_province(province_location_id=province["province_location_id"])
            old_province_dict = old_provinces_dict.get(static_province["static_province_id"])

            province.pop("province_location_id")
            province["static_province_id"] = static_province["static_province_id"]
            if old_province_dict is None:
                new_provinces.append(province)
            else:
                changes = compare(old_province_dict,
                                  province,
                                  [
                                      "province_id",
                                      "valid_from",
                                      "valid_until",
                                      "upgrades"])
                if changes:
                    logging.log(5,
                                f"UPDATE Province {static_province['province_location_id']}"
                                f"{old_province_dict}"
                                f"{province}")
                    update_provinces.append({
                        **old_province_dict,
                        "valid_until": province["valid_from"]
                    })
                    new_provinces.append(province)
        self.session.bulk_insert_mappings(Province, new_provinces)
        self.session.bulk_update_mappings(Province, update_provinces)

    def fill_buildings(self, data):
        old_buildings = self.session.query(Building).filter_by(game_id=self.game_id, valid_until=None).all()
        new_province_building_province_location_ids = [building["province_location_id"] for building in data]
        old_building_dict = {f"{old_building.static_province_id}_{old_building.upgrade_id}": old_building
                             for old_building in old_buildings}
        new_buildings = []
        update_buildings = []
        for building in data:
            static_province = self.get_static_province(province_location_id=building["province_location_id"])
            building["static_province_id"] = static_province["static_province_id"]
            existing_building = old_building_dict.get(f"{building['static_province_id']}_{building['upgrade_id']}")

            if not existing_building:
                new_buildings.append(building)
                logging.log(5, f"INSERT Building: {json.dumps(building, cls=DateTimeEncoder, indent=2)}")
            else:
                old_province_building_dict = object_as_dict(existing_building)

                changes = compare(old_province_building_dict, building, [
                    "building_id",
                    "province_location_id",
                    "valid_from",
                    "valid_until"])
                if changes:
                    logging.log(5,
                                f"UPDATE Building {static_province['province_location_id']} - {building['upgrade_id']}: "
                                f"{old_province_building_dict} "
                                f"{building}")
                    update_buildings.append({
                        **old_province_building_dict,
                        "valid_until": building["valid_from"]
                    })
                    new_buildings.append(building)

        new_buildings_dict = {f"{building['province_location_id']}_{building['upgrade_id']}": True
                              for building in data}

        # Check if new Building doesn't exist anymore
        for old_building in old_buildings:
            static_province = self.get_static_province(static_province_id=old_building.static_province_id)
            if static_province["province_location_id"] not in new_province_building_province_location_ids:
                continue

            if not new_buildings_dict.get(f"{static_province['province_location_id']}_{old_building.upgrade_id}"):
                logging.log(5,
                            f"DELETE Building {static_province['province_location_id']} - {old_building.upgrade_id}: ")
                old_building_dict = object_as_dict(old_building)
                update_buildings.append({
                    **old_building_dict,
                    "valid_until": self.timestamp
                })
        self.session.bulk_insert_mappings(Building, new_buildings)
        self.session.bulk_update_mappings(Building, update_buildings)

    def fill_armies(self, data):
        old_armies = self.session.query(Army).filter_by(game_id=self.game_id, valid_until=None).all()
        old_army_ids = [old_army.army_id for old_army in old_armies]

        new_army_ids = [new_army["army_id"] for new_army in data]
        new_armies = []
        update_armies = []
        for army in data:
            static_province = self.get_static_province(province_location_id=army["province_location_id"])
            if static_province:
                army["static_province_id"] = static_province.get("static_province_id")
            army.pop("province_location_id")
            if army["army_id"] not in old_army_ids:
                new_armies.append(army)
                logging.log(5,
                            f"INSERT Army {army['army_id']}:"
                            f"{json.dumps(army, indent=2, cls=DateTimeEncoder)}")
            else:
                old_army_sql = next(old_army for old_army in old_armies if old_army.army_id == army["army_id"])
                old_army = object_as_dict(old_army_sql)
                changes = compare(old_army, army, [
                    "universal_army_id",
                    "static_province_id",
                    "valid_from",
                    "valid_until"])
                if changes:
                    logging.log(5,
                                f"UPDATE Army {army['army_id']}:"
                                f"{old_army} "
                                f"{army}")
                    update_armies.append({
                        **old_army,
                        "valid_until": army["valid_from"]
                    })
                    new_armies.append(army)
        self.session.bulk_insert_mappings(Army, new_armies)
        self.session.bulk_update_mappings(Army, update_armies)

    def fill_commands(self, data):
        old_commands = self.session.query(Command).filter_by(game_id=self.game_id, valid_until=None).all()

        new_commands = []
        update_commands = []
        for command in data:
            try:
                old_command_sql = next(old_command for old_command in old_commands
                                       if old_command.army_id == command["army_id"])
                old_command_dict = object_as_dict(old_command_sql)
            except StopIteration:
                old_command_dict = None
            if old_command_dict is None:
                logging.log(5,
                            f"INSERT Command of Army {command['army_id']}:"
                            f"{json.dumps(command, indent=2, cls=DateTimeEncoder)}")
                new_commands.append(command)
            else:
                changes = compare(old_command_dict, command, ["command_id", "valid_from", "valid_until"])
                if changes:
                    # If new Command is stationary set the start_time to the new arrival_time
                    if "sy" in command["command_type"]:
                        command["start_time"] = old_command_dict["arrival_time"]

                    logging.log(5,
                                f"UPDATE Command of Army {command['army_id']}:"
                                f"{old_command_dict}"
                                f"{command}")

                    # If the old command is stationary set its arrival_time to the new start_time
                    if old_command_dict["command_type"] and "sy" in old_command_dict["command_type"]:
                        old_command_dict["arrival_time"] = command["start_time"]
                    update_commands.append({
                        **old_command_dict,
                        "valid_until": command["valid_from"]
                    })
                    new_commands.append(command)

        self.session.bulk_insert_mappings(Command, new_commands)
        self.session.bulk_update_mappings(Command, update_commands)

    def fill_warfare_units(self, data):
        old_warfare_units = self.session.query(WarfareUnit).join(Army).filter(Army.game_id == self.game_id).all()
        old_armies = self.session.query(Army).filter_by(game_id=self.game_id, valid_until=None).all()

        new_warfare_units = []

        # Checks if this specific warfare_unit is not saved for this army. Then it inserts it.
        for warfare_unit in data:
            try:
                old_army = next(old_army for old_army in old_armies
                                if old_army.army_id == warfare_unit["army_id"])
            except StopIteration:
                continue
            old_army_warfare_unit_warfare_ids = [old_army_warfare_unit.warfare_id
                                                 for old_army_warfare_unit in old_warfare_units
                                                 if
                                                 old_army_warfare_unit.universal_army_id == old_army.universal_army_id]
            if warfare_unit["warfare_id"] not in old_army_warfare_unit_warfare_ids:
                logging.log(5,
                            f"INSERT Warfare Unit {warfare_unit['warfare_id']}:"
                            f"{json.dumps(warfare_unit, indent=2, cls=DateTimeEncoder)}")
                new_warfare_units.append({
                    **warfare_unit,
                    "universal_army_id": old_army.universal_army_id
                })
        self.session.bulk_insert_mappings(WarfareUnit, new_warfare_units)

    def fill_army_gains_losses(self, data):
        old_army_gains_losses = self.session.query(ArmyLossesGain).filter_by(game_id=self.game_id).all()

        new_army_gains_losses = []

        for army_gains_loss in data:
            exists = any([not bool(compare(object_as_dict(old_army_gains_loss), army_gains_loss, ["army_loss_gain_id"]))
                          for old_army_gains_loss in old_army_gains_losses])
            if not exists:
                new_army_gains_losses.append(army_gains_loss)

        self.session.bulk_insert_mappings(ArmyLossesGain, new_army_gains_losses)

    def fill_researches(self, data):
        old_researches = self.session.query(Research).filter_by(game_id=self.game_id).all()

        new_researches = []
        update_researches = []

        for research in data:
            country_researches = [old_research for old_research in old_researches
                                  if old_research.owner_id == research["owner_id"]]
            country_column_ids = set([country_research.column_id for country_research in country_researches])
            country_column_research_min_ids = set([country_research.research_min_id
                                                   for country_research in country_researches
                                                   if country_research.column_id == research["column_id"]])
            if research["column_id"] not in country_column_ids:
                logging.log(5, f"INSERT Research: {json.dumps(research, cls=DateTimeEncoder, indent=2)}")
                new_researches.append(research)
            # Check if new research_min_id in column
            elif any([old_research_min_id >= research["research_min_id"]
                      for old_research_min_id in country_column_research_min_ids]):
                for old_research_min_id in country_column_research_min_ids:
                    if old_research_min_id >= research["research_min_id"]:
                        old_research = next(country_research for country_research in country_researches
                                            if old_research_min_id == country_research.research_min_id
                                            and research["column_id"] == country_research.column_id)
                        if time.mktime(old_research.valid_until.timetuple()) >= time.mktime(
                                research["valid_until"].timetuple()):
                            continue
                        logging.log(5, f"Update Research: "
                                       f"old: valid_until {old_research.valid_until}"
                                       f"new: valid_until {research['valid_until']}")
                        old_research.valid_until = research["valid_until"]
                        old_research.research_max_id = min(research["research_max_id"], old_research.research_max_id)
                        update_researches.append(object_as_dict(old_research))
                        break
            elif any([old_research_min_id < research["research_min_id"]
                      for old_research_min_id in country_column_research_min_ids]):
                logging.log(5, f"INSERT Research: {json.dumps(research, cls=DateTimeEncoder, indent=2)}")
                new_researches.append(research)

        self.session.bulk_update_mappings(Research, update_researches)
        self.session.bulk_insert_mappings(Research, new_researches)

    def fill_static_countries(self, data):
        static_countries_all = [r.country_id
                                for r in
                                self.session.query(StaticCountry).filter_by(map_id=self.map_id).all()]
        new_countries = list()
        for static_country in data:
            if static_country["country_id"] not in static_countries_all:
                new_countries.append(static_country)
        self.session.bulk_insert_mappings(StaticCountry, new_countries)

    def fill_static_scenarios(self, data):
        scenario_all = [r.scenario_id for r in self.session.query(Scenario.scenario_id)]
        new_scenarios = list()
        for scenario in data:
            scenario = data[scenario]
            if scenario["scenario_id"] not in scenario_all:
                new_scenarios.append(scenario)

        self.session.bulk_insert_mappings(Scenario, new_scenarios)

    def fill_static_provinces(self, data):
        static_provinces_all = [r.province_location_id for r in
                                self.session.query(StaticProvince.province_location_id).filter_by(
                                    map_id=self.map_id).all()]
        new_static_provinces = list()
        for province in data:
            province = data[province]
            if province["province_location_id"] not in static_provinces_all:
                new_static_provinces.append(province)
        self.session.bulk_insert_mappings(StaticProvince, new_static_provinces)

    def get_static_province(self, static_province_id=None, province_location_id=None):
        if not self.static_provinces:
            static_provinces = self.session.query(StaticProvince) \
                .join(Scenario, StaticProvince.map_id == Scenario.map_id) \
                .join(Game) \
                .filter_by(game_id=self.game_id).all()
            self.static_provinces["province_location"] = {object_as_dict(static_province)
                                                          ["province_location_id"]
                                                          : object_as_dict(static_province)
                                                          for static_province in static_provinces}
            self.static_provinces["static_province"] = {object_as_dict(static_province)
                                                        ["static_province_id"]
                                                        : object_as_dict(static_province)
                                                        for static_province in static_provinces}

        if province_location_id:
            return self.static_provinces["province_location"].get(province_location_id)
        elif static_province_id:
            return self.static_provinces["static_province"].get(static_province_id)


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
