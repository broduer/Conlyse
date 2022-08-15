import json
import logging

from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from Bot.sort.helper import DateTimeEncoder
from Bot.sql.Models import Scenario, Trade, Player, Province, StaticProvince, Country, Game, GameHasPlayer, Team, \
    Building, Newspaper
from Bot.sql.sql import engine
from datetime import datetime
from deepdiff import DeepDiff


class Filler:
    def __init__(self, game_id, data):
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()
        self.data = data
        self.timestamp = data["timestamp"]
        self.game_id = int(game_id)

        self.static_provinces = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.commit()
        self.session.close()

    def fill(self):
        logging.debug(f"Filling Game {self.game_id}")
        keys = list(self.data.keys())
        if "static_provinces" in keys:
            logging.debug("Filling static_provinces and static_scenarios")
            self.fill_static_provinces(self.data["static_provinces"])
            self.fill_static_scenarios(self.data["static_scenarios"])
            self.session.flush()

        if "game" in keys:
            self.fill_game(self.data["game"])
            if int(self.data["game"]["end_time"]) != 0:
                return True

        if "teams" in keys:
            self.fill_teams(self.data["teams"])

        if all(ele in keys for ele in ["players", "countries"]):
            logging.debug(f"Filling {len(self.data['players'].values())} Players and Countries")
            self.fill_player_country(self.data["players"], self.data["countries"])

        if "trades" in keys:
            self.fill_trades(self.data["trades"])

        if "newspaper" in keys:
            self.fill_newspaper(self.data["newspaper"])

        if "provinces" in keys:
            self.fill_provinces(self.data["provinces"])
            self.fill_buildings(self.data["buildings"])

    def fill_game(self, data):
        game_sql = self.session.query(Game).filter_by(game_id=data["game_id"]).first()
        if game_sql is None:
            new_game = Game(
                game_id=data["game_id"],
                scenario_id=data["scenario_id"],
                start_time=datetime.fromtimestamp(data["start_time"]),
                end_time=None,
                current_time=datetime.fromtimestamp(data["current_time"]),
                next_day_time=datetime.fromtimestamp(data["next_day_time"]),
                next_heal_time=datetime.fromtimestamp(data["next_heal_time"]),
            )
            self.session.add(new_game)
        else:
            if data["end_time"] != 0:
                game_sql.end_time = datetime.fromtimestamp(data["end_time"])
                game_sql.next_day_time = None
                game_sql.next_heal_time = None
            else:
                game_sql.next_day_time = datetime.fromtimestamp(data["next_day_time"])
                game_sql.current_time = datetime.fromtimestamp(data["current_time"])
                game_sql.next_heal_time = datetime.fromtimestamp(data["next_heal_time"])

    def fill_player_country(self, data_players, data_countries):
        # Retrieve the latest Data from DB
        counties = self.session.query(Country).filter_by(game_id=self.game_id, valid_until=None).all()
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
            new_country = {**data_country, "team_id": team_id}

            # New Country if this country_id does not exist for this Game.
            if new_country["country_id"] not in countries_country_id:
                new_countries.append(new_country)
            else:
                # SQLALCHEMY object to dict
                country_sql_dict = object_as_dict(counties[countries_country_id.index(new_country["country_id"])])

                # Compare New Country to the latest in DB with some exceptions.
                changes = DeepDiff(country_sql_dict,
                                   new_country,
                                   exclude_paths=["root['universal_country_id']",
                                                  "root['valid_from']",
                                                  "root['valid_until']"])
                if changes:
                    logging.debug(f"UPDATE Country {data_country['country_id']}: {changes.get('type_changes')} "
                                  f"{changes.get('values_changed')}")
                    update_countries.append({
                        **country_sql_dict,
                        "valid_until": data_country["valid_from"]
                    })
                    new_countries.append(data_country)

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
                logging.debug(f"INSERT Team: {json.dumps(team, cls=DateTimeEncoder, indent=2)}")
            else:
                team_exists = object_as_dict(teams[teams_team_id.index(team["team_id"])])
                changes = DeepDiff(team_exists, team,
                                   exclude_paths=["root['universal_team_id']"])
                if changes:
                    updated_teams.append({
                        **team_exists,
                        "leader_id": team["leader_id"],
                        "name": team["name"],
                        "deleted": team["deleted"],
                    })
                    logging.debug(f"UPDATE Team {team['team_id']}: {changes.get('type_changes')} "
                                  f"{changes.get('values_changed')}")
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
                logging.debug(f"INSERT Trade: {json.dumps(trade, cls=DateTimeEncoder, indent=2)}")
            else:
                old_trade_sql = next(
                    old_trade_sql for old_trade_sql in old_trades if old_trade_sql.order_id == trade["order_id"])
                old_trade_dict = object_as_dict(old_trade_sql)
                changes = DeepDiff(old_trade_dict,
                                   trade,
                                   exclude_paths=["root['trade_id']",
                                                  "root['valid_from']",
                                                  "root['valid_until']"])
                if changes:
                    logging.debug(f"UPDATE Trade {trade['order_id']}: {changes.get('type_changes')} "
                                  f"{changes.get('values_changed')}")
                    update_trades.append({
                        **old_trade_dict,
                        "valid_until": trade["valid_from"]
                    })
                    new_trades.append(trade)

        # Check if new Trade doesn't exist
        for old_trade in old_trades:
            if old_trade.order_id not in new_order_ids:
                logging.debug(f"DELETE Trade {old_trade.order_id}")
                old_trade_dict = object_as_dict(old_trade)
                update_trades.append({
                    **old_trade_dict,
                    "valid_until": self.timestamp
                })
        self.session.bulk_insert_mappings(Trade, new_trades)
        self.session.bulk_update_mappings(Trade, update_trades)

    def fill_provinces(self, data):
        old_provinces = self.session.query(Province).filter_by(valid_until=None, game_id=self.game_id).all()

        new_provinces = []
        update_provinces = []

        for province in data.values():
            static_province = self.get_static_province(province_location_id=province["province_location_id"])
            try:
                old_province = next(old_province for old_province in old_provinces
                                    if old_province.static_province_id == static_province["static_province_id"])
                old_province_dict = object_as_dict(old_province)
            except StopIteration:
                old_province_dict = None

            province.pop("province_location_id")
            province["static_province_id"] = static_province["static_province_id"]
            if old_province_dict is None:
                new_provinces.append(province)
            else:
                changes = DeepDiff(old_province_dict,
                                   province,
                                   exclude_paths=[
                                       "root['province_id']",
                                       "root['valid_from']",
                                       "root['valid_until']",
                                       "root['upgrades']"])
                if changes:
                    logging.debug(
                        f"UPDATE Province {static_province['province_location_id']}: {changes.get('type_changes')} "
                        f"{changes.get('values_changed')}")
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
        new_buildings = []
        update_buildings = []
        for building in data:
            static_province = self.get_static_province(province_location_id=building["province_location_id"])
            old_province_buildings = [old_building for old_building in old_buildings if
                                      old_building.static_province_id == static_province["static_province_id"]]
            old_province_building_upgrade_ids = [old_province_building.upgrade_id for old_province_building in
                                                 old_province_buildings]
            building["static_province_id"] = static_province["static_province_id"]
            if building["upgrade_id"] not in old_province_building_upgrade_ids:
                new_buildings.append(building)
                logging.debug(f"INSERT Building: {json.dumps(building, cls=DateTimeEncoder, indent=2)}")
            else:
                old_province_building = next(
                    old_province_building for old_province_building in old_province_buildings if
                    old_province_building.upgrade_id == building["upgrade_id"])
                old_province_building_dict = object_as_dict(old_province_building)

                changes = DeepDiff(old_province_building_dict, building,
                                   exclude_paths=[
                                       "root['building_id']",
                                       "root['province_location_id']",
                                       "root['valid_from']",
                                       "root['valid_until']"])
                if changes:
                    logging.debug(
                        f"UPDATE Building {static_province['province_location_id']} - {building['upgrade_id']}: "
                        f"{changes.get('type_changes')} "
                        f"{changes.get('values_changed')}")
                    update_buildings.append({
                        **old_province_building_dict,
                        "valid_until": building["valid_from"]
                    })
                    new_buildings.append(building)

        # Check if new Building doesn't exist anymore
        for old_building in old_buildings:
            static_province = self.get_static_province(static_province_id=old_building.static_province_id)
            if static_province["province_location_id"] not in new_province_building_province_location_ids:
                continue
            new_province_building_upgrade_ids = [building["upgrade_id"] for building in data
                                                 if building["province_location_id"] == static_province[
                                                     "province_location_id"]]
            if old_building.upgrade_id not in new_province_building_upgrade_ids:
                logging.debug(f"DELETE Building {static_province['province_location_id']} - {old_building.upgrade_id}: ")
                old_building_dict = object_as_dict(old_building)
                update_buildings.append({
                    **old_building_dict,
                    "valid_until": self.timestamp
                })
        self.session.bulk_insert_mappings(Building, new_buildings)
        self.session.bulk_update_mappings(Building, update_buildings)

    def fill_newspaper(self, data):
        newspaper_all = [a for a in self.session.query(Newspaper).all()]
        new_articles = list()
        for article in data:
            for newspaper_sql in newspaper_all:
                if DeepDiff(object_as_dict(newspaper_sql),
                            article,
                            exclude_paths=["root['article_id']"]):
                    break
            else:
                logging.debug(f"INSERT Newspaper-Article {json.dumps(article, cls=DateTimeEncoder, indent=2)}")
                new_articles.append({**article, "game_id": self.game_id})
        self.session.bulk_insert_mappings(Newspaper, new_articles)

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
                                    map_id=self.data["game"]["map_id"]).all()]
        new_static_provinces = list()
        for province in data:
            province = data[province]
            if province["province_location_id"] not in static_provinces_all:
                new_static_provinces.append(province)
        self.session.bulk_insert_mappings(StaticProvince, new_static_provinces)

    def get_static_province(self, static_province_id=None, province_location_id=None):
        if self.static_provinces is None:
            self.static_provinces = self.session.query(StaticProvince) \
                .join(Scenario, StaticProvince.map_id == Scenario.map_id) \
                .join(Game) \
                .filter_by(game_id=self.game_id).all()

        if province_location_id is not None:
            try:
                static_province = next(static_province for static_province in self.static_provinces
                                       if static_province.province_location_id == province_location_id)
                return object_as_dict(static_province)
            except StopIteration:
                return None
        elif static_province_id is not None:
            try:
                static_province = next(static_province for static_province in self.static_provinces
                                       if static_province.static_province_id == static_province_id)
                return object_as_dict(static_province)
            except StopIteration:
                return None


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
