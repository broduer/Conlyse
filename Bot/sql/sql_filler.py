from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from Bot.sql.Models import Scenario, Trade, Player, Province, StaticProvince, Country, Game, GameHasPlayer, Team, \
    Building, ProvinceHasBuilding, Newspaper
from Bot.sql.sql import engine
from datetime import datetime


class Filler:
    def __init__(self, data):
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()
        self.data = data
        self.fillStatic(data["static"])
        self.fillGame(data["game"])
        if int(data["game"]["end_time"]) == 0:
            self.fillTeam(data["teams"])
            self.fillPlayer_Country(data["players"], data["countries"])
            self.fillTrade(data["trades"])
            self.fillNewsPaper(data["newspaper"])
            self.fillProvince(data["provinces"])
            self.fillBuildings(data["provinces"])
        self.session.commit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def fillGame(self, data):
        if self.session.query(Game.game_id).filter_by(game_id=data["game_id"]).first() is None:
            game_sql = Game(
                game_id=data["game_id"],
                scenario_id=data["scenario_id"],
                start_time=datetime.fromtimestamp(data["start_time"]),
                end_time=None,
                current_time=datetime.fromtimestamp(data["current_time"]),
                next_day_time=datetime.fromtimestamp(data["next_day_time"]),
                next_heal_time=datetime.fromtimestamp(data["next_heal_time"]),
            )
            self.session.add(game_sql)
        else:
            game_sql = self.session.query(Game).filter_by(game_id=data["game_id"]).first()
            if data["end_time"] != 0:
                game_sql.end_time = datetime.fromtimestamp(data["end_time"])
                game_sql.next_day_time = None
                game_sql.next_heal_time = None
            else:
                game_sql.next_day_time = datetime.fromtimestamp(data["next_day_time"])
                game_sql.current_time = datetime.fromtimestamp(data["current_time"])
                game_sql.next_heal_time = datetime.fromtimestamp(data["next_heal_time"])

    def checkifCountryexists(self, country_id):
        country = self.session.query(GameHasPlayer).join(Country).filter(
            GameHasPlayer.game_id == self.data["game"]["game_id"],
            Country.player_id == country_id).first()
        if country is None:
            return False
        else:
            return True

    def fillPlayer_Country(self, data, data_2):
        for p, country in zip(data, data_2):
            p = data[p]
            country = data_2[country]
            player_id = self.fillPlayer(p)
            self.fillCountry(country, player_id)

    def fillPlayer(self, p):
        p_sql = self.session.query(Player).filter_by(
            name=p["name"]).first()
        if p_sql is None:
            p_sql = Player(
                site_user_id=p["site_user_id"],
                name=p["name"],
            )
            self.session.add(p_sql)
            self.session.flush()
        return p_sql.player_id

    def fillCountry(self, country, player_id):
        if not self.checkifCountryexists(country["player_id"]):
            if country["team_id"] != 0:
                team_id = self.session.query(Team.universal_team_id).filter_by(
                    game_id=self.data["game"]["game_id"],
                    team_id=country["team_id"],
                ).first().universal_team_id
            else:
                team_id = None
            country_sql = Country(
                player_id=country["player_id"],
                team_id=team_id,
                name=country["name"],
                capital_id=country["capital_id"],
                defeated=country["defeated"],
                computer=country["computer"],
            )
            self.session.add(country_sql)
            self.session.flush()
            gamehasplayer = GameHasPlayer(
                game_id=self.data["game"]["game_id"],
                player_id=player_id,
                country_id=country_sql.country_id,
            )
            self.session.add(gamehasplayer)

    def fillTeam(self, data):
        for team in data:
            team = data[team]
            team_exists = self.session.query(Team).filter_by(
                game_id=self.data["game"]["game_id"],
                team_id=team["team_id"], ).first()
            if team_exists is None:
                team_sql = Team(
                    game_id=self.data["game"]["game_id"],
                    team_id=team["team_id"],
                    leader_id=team["leader_id"],
                    name=team["name"],
                    deleted=team["deleted"],
                )
                self.session.add(team_sql)
            else:
                team_exists.leader_id = team["leader_id"]
                team_exists.name = team["name"]
                team_exists.deleted = team["deleted"]

    def fillTrade(self, data):
        countrys = self.session.query(Country).join(GameHasPlayer).filter_by(game_id=self.data["game"]["game_id"]).all()
        for trade in data:
            trade = data[trade]
            for country in countrys:
                if country.player_id == trade["owner_id"]:
                    trade["owner_id"] = country.country_id
                    break
            trade_sql = Trade(
                game_id=self.data["game"]["game_id"],
                order_id=trade["order_id"],
                owner_id=trade["owner_id"],
                amount=trade["amount"],
                resource_type=trade["resource_type"],
                limit=trade["limit"],
                buy=trade["buy"],
                current_time=datetime.now(),
            )
            self.session.add(trade_sql)

    def fillProvince(self, data):
        country_ids = self.session.query(GameHasPlayer.country_id, Country.player_id).join(Country).filter(
            GameHasPlayer.game_id == self.data["game"]["game_id"],
        ).all()
        new_provinces = list()
        for province in data:
            province = data[province]
            for country_id in country_ids:
                if country_id.player_id == province["owner_id"]:
                    province["owner_id"] = country_id.country_id
                    new_provinces.append(province)
        self.session.bulk_insert_mappings(Province, new_provinces)

    def fillBuildings(self, data):
        province_ids = self.session.query(Province).join(Country).join(GameHasPlayer).filter(
            GameHasPlayer.game_id == self.data["game"]["game_id"],
            Province.current_time == datetime.fromtimestamp(self.data["game"]["current_time"]),
        ).order_by(Province.province_id).all()
        added_buildings = self.session.query(Building).all()
        new_buildings = list()
        for province in data:
            buildings = data[province]["upgrades"]
            for building in buildings:
                building = buildings[building]
                already_added_building = False

                for added_building in added_buildings:
                    if added_building.upgrade_id == building["upgrade_id"] and added_building.health == building[
                        "health"]:
                        already_added_building = True
                for new_building in new_buildings:
                    if new_building["upgrade_id"] == building["upgrade_id"] and new_building["health"] == building[
                        "health"]:
                        already_added_building = True
                if not already_added_building:
                    new_buildings.append(building)
        self.session.bulk_insert_mappings(Building, new_buildings)
        added_buildings = self.session.query(Building).all()
        new_buildings_province = list()
        for province, province_id in zip(data, province_ids):
            buildings = data[province]["upgrades"]
            for building in buildings:
                building = buildings[building]
                for added_building in added_buildings:
                    if added_building.upgrade_id == building["upgrade_id"] and added_building.health == building[
                        "health"]:
                        new_buildings_province.append(dict({
                            "province_id": province_id.province_id,
                            "building_id": added_building.building_id,
                        }))
        self.session.bulk_insert_mappings(ProvinceHasBuilding, new_buildings_province)

    def fillNewsPaper(self, data):
        newspaper_all = [a for a in self.session.query(Newspaper).all()]
        countrys_all = [object_as_dict(c) for c in self.session.query(Country).join(GameHasPlayer).filter(
            GameHasPlayer.game_id == self.data["game"]["game_id"]).all()]

        articles_times = [a.time for a in newspaper_all]
        new_articles = list()
        for article in data:
            new = True
            article["country_id"] = [c for c in countrys_all if c["player_id"] == article.get("country_id")][0]["country_id"]
            for old_article in newspaper_all:
                if old_article.msg_typ == article.get("msg_typ") \
                        and int(old_article.time.timestamp()) == int(article.get("time").timestamp()) \
                        and old_article.country_id == article.get("country_id"):
                    new = False
            if new:
                new_articles.append(article)
        self.session.bulk_insert_mappings(Newspaper, new_articles)

    def fillStatic(self, static):
        self.fillStaticScenario(static["scenarios"])
        self.fillStaticProvince(static["provinces"])

    def fillStaticScenario(self, data):
        scenario_all = [r.scenario_id for r in self.session.query(Scenario.scenario_id)]
        new_scenarios = list()
        for scenario in data:
            scenario = data[scenario]
            if scenario["scenario_id"] not in scenario_all:
                new_scenarios.append(scenario)

        self.session.bulk_insert_mappings(Scenario, new_scenarios)

    def fillStaticProvince(self, data):
        static_provinces_all = [r.province_location_id for r in
                                self.session.query(StaticProvince.province_location_id).filter_by(
                                    map_id=self.data["game"]["map_id"]).all()]
        new_static_provinces = list()
        for province in data:
            province = data[province]
            if province["province_location_id"] not in static_provinces_all:
                new_static_provinces.append(province)
        self.session.bulk_insert_mappings(StaticProvince, new_static_provinces)


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
