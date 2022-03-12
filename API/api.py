import json
import time
from datetime import datetime

from flask import Flask, jsonify, request
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import inspect
from sqlalchemy import func, between, case, cast, Integer
from flask_cors import CORS

import helper
import constants
# create the object of Flask
from API.helpers.research import getResearch

app = Flask(__name__)

app.config['SECRET_KEY'] = constants.FLASK_SECRET

# SqlAlchemy Datadb.Model Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{constants.MYSQL_USER}:{constants.MYSQL_USER_PASSWORD}@{constants.MYSQL_IP_ADDR}/{constants.MYSQL_DATABASE}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
Compress(app)
CORS(app)

with open("static_informations/upgrades.json") as file:
    data_upgrades = json.loads(file.read())

with open("static_informations/researches.json") as file:
    data_researches = json.loads(file.read())


class Building(db.Model):
    __tablename__ = 'building'

    building_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    upgrade_id = db.Column(db.Integer, nullable=False)
    health = db.Column(db.Integer)

    provinces = db.relationship('Province', secondary='province_has_building', overlaps="provinces")


class Player(db.Model):
    __tablename__ = 'player'

    player_id = db.Column(db.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    site_user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(75), nullable=False)


class Scenario(db.Model):
    __tablename__ = 'scenario'

    scenario_id = db.Column(db.Integer, primary_key=True)
    map_id = db.Column(db.Integer)
    name = db.Column(db.String(45))
    speed = db.Column(db.Integer)

    game = db.relationship("Game", back_populates="scenario")


class StaticProvince(db.Model):
    __tablename__ = 'static_province'

    static_province_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    province_location_id = db.Column(db.Integer, nullable=False)
    map_id = db.Column(db.Integer)
    province_type = db.Column(db.Integer)
    name = db.Column(db.String(50))
    coordinate_x = db.Column(db.Integer)
    coordinate_y = db.Column(db.Integer)
    mainland_id = db.Column(db.Integer)
    region = db.Column(db.Integer)
    db.Model_production = db.Column(db.Integer)
    terrain_type = db.Column(db.Integer)
    resource_production_type = db.Column(db.Integer)
    b = db.Column(db.String(10000))
    coastal = db.Column(db.BOOLEAN)


class Game(db.Model):
    __tablename__ = 'game'

    game_id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.ForeignKey('scenario.scenario_id'), nullable=False, index=True)
    start_time = db.Column(db.TIMESTAMP)
    end_time = db.Column(db.TIMESTAMP)
    current_time = db.Column(db.TIMESTAMP)
    next_day_time = db.Column(db.TIMESTAMP)
    next_heal_time = db.Column(db.TIMESTAMP)

    scenario = db.relationship('Scenario', back_populates="game")


class Team(db.Model):
    __tablename__ = 'team'

    universal_team_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    game_id = db.Column(db.ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    team_id = db.Column(db.Integer)
    name = db.Column(db.String(45))
    leader_id = db.Column(db.Integer)
    deleted = db.Column(db.BOOLEAN)

    game = db.relationship('Game')


class Country(db.Model):
    __tablename__ = 'country'

    country_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer)
    team_id = db.Column(db.ForeignKey('team.universal_team_id'), index=True)
    name = db.Column(db.String(45))
    capital_id = db.Column(db.Integer)
    defeated = db.Column(db.BOOLEAN)
    computer = db.Column(db.BOOLEAN)

    team = db.relationship('Team')


class GameHasPlayer(db.Model):
    __tablename__ = 'game_has_player'

    game_id = db.Column(db.ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    player_id = db.Column(db.ForeignKey('player.player_id'), primary_key=True, nullable=False, index=True)
    country_id = db.Column(db.ForeignKey('country.country_id'), primary_key=True, nullable=False, index=True)

    country = db.relationship('Country')
    game = db.relationship('Game')
    player = db.relationship('Player')


class Province(db.Model):
    __tablename__ = 'province'

    province_id = db.Column(db.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    province_location_id = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.ForeignKey('country.country_id'), primary_key=True, nullable=False, index=True)
    morale = db.Column(db.Integer)
    province_state_id = db.Column(db.Integer)
    stationary_army_id = db.Column(db.Integer)
    victory_points = db.Column(db.Integer)
    resource_production = db.Column(db.Integer)
    tax_production = db.Column(db.Integer)
    current_time = db.Column(db.TIMESTAMP, nullable=False)
    map_id = db.Column(db.Integer)
    game_id = db.Column(db.ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)

    game = db.relationship('Game')
    owner = db.relationship('Country')
    buildings = db.relationship("Building", secondary="province_has_building", overlaps="provinces")


class Trade(db.Model):
    __tablename__ = 'trade'

    trade_id = db.Column(db.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    game_id = db.Column(db.ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    order_id = db.Column(db.String(45))
    owner_id = db.Column(db.ForeignKey('country.country_id'), primary_key=True, nullable=False, index=True)
    amount = db.Column(db.Integer)
    resource_type = db.Column(db.Integer)
    limit = db.Column(db.Float)
    buy = db.Column(db.BOOLEAN)
    current_time = db.Column(db.TIMESTAMP)

    game = db.relationship('Game')
    owner = db.relationship('Country')


class Newspaper(db.Model):
    __tablename__ = 'newspaper'

    article_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    msg_typ = db.Column(db.Integer, nullable=False)
    country_id = db.Column(db.ForeignKey('country.country_id'), primary_key=True, nullable=False, index=True)
    wtyp = db.Column(db.Integer, nullable=False)
    whtyp = db.Column(db.Integer)
    division = db.Column(db.Integer)
    count = db.Column(db.Integer)
    time = db.Column(db.TIMESTAMP)

    country = db.relationship('Country')


class ProvinceHasBuilding(db.Model):
    __tablename__ = 'province_has_building'

    province_id = db.Column(db.ForeignKey('province.province_id'), primary_key=True, nullable=False, index=True)
    building_id = db.Column(db.ForeignKey('building.building_id'), primary_key=True, nullable=False, index=True)

    province = db.relationship("Province", overlaps="buildings,provinces")
    building = db.relationship("Building", overlaps="buildings,provinces")


# creating our routes
@app.route('/api/v1/game')
def game():
    filters = dict({})
    output = dict({})
    table = inspect(Team)
    for filter in table.c:
        if filter.name in request.args:
            filters[filter.name] = request.args[filter.name]
    for game in Game.query.filter_by(**filters).all():
        output_dict = object_as_dict(game)
        output_dict["current_time"] = round(output_dict["current_time"].timestamp())
        output_dict["start_time"] = round(output_dict["start_time"].timestamp())
        output_dict["next_heal_time"] = round(output_dict["next_heal_time"].timestamp()) if output_dict[
                                                                                                "next_heal_time"] is not None else None
        output_dict["next_day_time"] = round(output_dict["next_day_time"].timestamp()) if output_dict[
                                                                                              "next_heal_time"] is not None else None
        output_dict["end_time"] = round(output_dict["end_time"].timestamp()) if output_dict[
                                                                                    "end_time"] is not None else None

        output[game.game_id] = output_dict
    return jsonify(list(output.values()))


@app.route('/api/v1/team')
def team():
    filters = dict({})
    output = dict({})
    table = inspect(Team)
    if "game_id" not in request.args:
        return "game_id is needed"
    for filter in table.c:
        if filter.name in request.args:
            filters[filter.name] = request.args[filter.name]
    for team in Team.query.filter_by(**filters).all():
        output_dict = object_as_dict(team)
        output_dict.pop("game_id")
        output[team.universal_team_id] = output_dict

    return jsonify(output)


@app.route('/api/v1/province')
def provinces():
    output = dict({})
    filters = []
    table = inspect(Province)
    if "value" in request.args:
        query = db.session.query(Province.province_id, Province.owner_id, StaticProvince.name, Building.upgrade_id,
                                 Building.health) \
            .select_from(Province) \
            .join(StaticProvince, Province.province_location_id == StaticProvince.province_location_id) \
            .join(ProvinceHasBuilding) \
            .join(Building)
    else:
        query = db.session.query(Province)
    if "game_id" not in request.args:
        return "game_id is needed"
    for filter in table.c:
        if filter.name in request.args:
            if "current_time" == filter.name:
                query = query.filter(
                    getattr(Province, filter.name) == datetime.fromtimestamp(float(request.args[filter.name])))
            else:
                query = query.filter(getattr(Province, filter.name) == request.args[filter.name])

    if "day" in request.args:
        game = getGame(request.args["game_id"])
        differenc_hours = game["current_time"].hour - game["start_time"].hour
        differenc_minutes = game["current_time"].minute - game["start_time"].minute
        if "lastdays" in request.args:
            lastdays = int(request.args["lastdays"])
        else:
            lastdays = 0
        day_time = round(time.mktime(game["start_time"].timetuple())) + (
                int(request.args["day"]) * 3600 * 24) + differenc_hours * 3600 + differenc_minutes * 60
        time_start = day_time - 3600 * 24 * lastdays - 300
        time_end = day_time + 300
        query = query.filter(
            between(Province.current_time, func.FROM_UNIXTIME(time_start), func.FROM_UNIXTIME(time_end)))
    if "value" in request.args:
        province_buildings = {}
        for province in query.limit(1000000).all():
            province_dict = {
                "province_id": province.province_id,
                "owner_id": province.owner_id,
                "province_name": province[2],
                "upgrade_id": province.upgrade_id,
                "health": province.health
            }
            province_buildings[f'{province_dict["province_id"]}_{province_dict["upgrade_id"]}'] = province_dict
        ranked = False
        if "ranked" in request.args:
            ranked = True
        output = helper.getProvinceBuildings(province_buildings, data_upgrades, ranked)
        return jsonify(output)
    for province in query.limit(1000000).all():
        province_dict = object_as_dict(province)
        province_dict["current_time"] = round(time.mktime(province.current_time.timetuple()))
        province_dict.pop("map_id")
        province_dict.pop("game_id")
        output[province_dict["province_id"]] = province_dict
    return jsonify(output)


@app.route('/api/v1/country')
def country():
    output = dict({})
    filters = dict({})
    filters_exp = dict({})
    table_country = inspect(Country)
    table_player = inspect(Player)

    if "game_id" not in request.args:
        return "game_id is needed"

    game_id = request.args["game_id"]
    if len(filters) + len(filters_exp) == 1:
        return "Error: To less filters"

    if "economy" in request.args:
        query = db.session.query(
            Country.country_id,
            Province.current_time,
            func.sum(Province.victory_points),
            func.sum(case(
                [(StaticProvince.resource_production_type == 2, Province.resource_production)], else_=0
            )),
            func.sum(case(
                [(StaticProvince.resource_production_type == 3, Province.resource_production)], else_=0
            )),
            func.sum(case(
                [(StaticProvince.resource_production_type == 5, Province.resource_production)], else_=0
            )),
            func.sum(case(
                [(StaticProvince.resource_production_type == 6, Province.resource_production)], else_=0
            )),
            func.sum(case(
                [(StaticProvince.resource_production_type == 7, Province.resource_production)], else_=0
            )),
            func.sum(Province.tax_production),
            func.sum(Province.resource_production).label("total"),

        ).select_from(Country
                      ).join(Province).join(StaticProvince,
                                            Province.province_location_id == StaticProvince.province_location_id
                                            ).join(GameHasPlayer
                                                   )
        if "day" in request.args:
            game = getGame(request.args["game_id"])
            differenc_hours = game["current_time"].hour - game["start_time"].hour
            differenc_minutes = game["current_time"].minute - game["start_time"].minute
            if "lastdays" in request.args:
                lastdays = int(request.args["lastdays"])
            else:
                lastdays = 0
            day_time = round(time.mktime(game["start_time"].timetuple())) + (
                    int(request.args["day"]) * 3600 * 24) + differenc_hours * 3600 + differenc_minutes * 60
            time_start = day_time - 3600 * 24 * lastdays - 300
            time_end = day_time + 300
            query = query.filter(
                between(Province.current_time, func.FROM_UNIXTIME(time_start), func.FROM_UNIXTIME(time_end)))
        if "country_id" in request.args:
            query = query.filter(Country.country_id == int(request.args["country_id"]))
        if "single" in request.args:
            for country in query.filter(
                    GameHasPlayer.game_id == game_id
            ).group_by(Country.country_id, Province.current_time).all():
                output[country.country_id] = dict({
                    "country_id": country.country_id,
                    "current_time": round(country.current_time.timestamp()),
                    "victory_points": int(country[2]),
                    "2": int(country[3]),
                    "3": int(country[4]),
                    "5": int(country[5]),
                    "6": int(country[6]),
                    "7": int(country[7]),
                    "21": int(country[8]),
                    "total": int(country.total),
                })
            return jsonify(output)
        for country in query.filter(
                GameHasPlayer.game_id == game_id
        ).group_by(Country.country_id, Province.current_time).all():
            output[f"{country.country_id}_{round(country.current_time.timestamp())}"] = dict({
                "country_id": country.country_id,
                "current_time": round(country.current_time.timestamp()),
                "victory_points": int(country[2]),
                "2": int(country[3]),
                "3": int(country[4]),
                "5": int(country[5]),
                "6": int(country[6]),
                "7": int(country[7]),
                "21": int(country[8]),
                "total": int(country.total),
            })
        return jsonify(output)

    if "research" in request.args:
        query = db.session.query(
            Newspaper.country_id, Newspaper.wtyp, func.sum(Newspaper.count)
        ).select_from(Newspaper
                      ).join(GameHasPlayer, GameHasPlayer.country_id == Newspaper.country_id
                             ).filter(GameHasPlayer.game_id == game_id)
        if "country_id" in request.args:
            query = query.filter(Newspaper.country_id == int(request.args["country_id"]))
        for country in query.group_by(Newspaper.country_id, Newspaper.wtyp).all():
            output[f"{country.country_id} {country.wtyp}"] = dict({
                "country_id": country.country_id,
                "wtyp": country.wtyp,
                "count": country[-1],
            })
        output = getResearch(output)
        return jsonify(output)

    if "stats" in request.args:
        query = db.session.query(
            Country.country_id,
            Province.current_time,
            func.avg(Province.morale).label("morale"),
            func.sum(case(
                [(Province.province_state_id <= 52, 1)], else_=0
            )).label("total_provinces"),
            func.sum(case(
                [(Province.province_state_id >= 53, 1)], else_=0
            )).label("total_cities"),
            func.sum(case(
                [(Province.province_state_id == 55, 1)], else_=0
            )).label("total_mainland_cities"),
            func.sum(case(
                [(Province.province_state_id == 54, 1)], else_=0
            )).label("total_annexed_cities"),
            func.count(Province.province_id).label("total"),
        ).select_from(Country
                      ).join(Province).join(GameHasPlayer
                                            )
        if "day" in request.args:
            game = getGame(request.args["game_id"])
            differenc_hours = game["current_time"].hour - game["start_time"].hour
            differenc_minutes = game["current_time"].minute - game["start_time"].minute
            if "lastdays" in request.args:
                lastdays = int(request.args["lastdays"])
            else:
                lastdays = 0
            day_time = round(time.mktime(game["start_time"].timetuple())) + (
                    int(request.args["day"]) * 3600 * 24) + differenc_hours * 3600 + differenc_minutes * 60
            time_start = day_time - 3600 * 24 * lastdays - 300
            time_end = day_time + 300
            query = query.filter(
                between(Province.current_time, func.FROM_UNIXTIME(time_start), func.FROM_UNIXTIME(time_end)))
        if "country_id" in request.args:
            query = query.filter(Country.country_id == int(request.args["country_id"]))
        for country in query.filter(
                GameHasPlayer.game_id == game_id
        ).group_by(Country.country_id, Province.current_time).all():
            output[country.country_id] = dict({
                "country_id": country.country_id,
                "current_time": round(country.current_time.timestamp()),
                "morale": round(country.morale, 2),
                "total_provinces": int(country.total_provinces),
                "total_cities": int(country.total_cities),
                "total_mainland_cities": int(country.total_mainland_cities),
                "total_annexed_cities": int(country.total_annexed_cities),
                "total": int(country.total),
            })
        return jsonify(output)
    query = db.session.query(Country.country_id, Country.name, Player.player_id, Player.name,
                             Country.team_id,
                             Country.capital_id, Country.defeated, Country.computer
                             ).select_from(Country).join(
        GameHasPlayer).join(Player
                            ).filter(GameHasPlayer.game_id == game_id)
    if "country_id" in request.args:
        query = query.filter(GameHasPlayer.country_id == int(request.args["country_id"]))
    for country in query.all():
        output[country.country_id] = dict({
            "player_id": country.player_id,
            "player_name": country[3],
            "country_id": country.country_id,
            "country_name": country[1],
            "team_id": country.team_id,
            "capital_id": country.capital_id,
            "defeated": country.defeated,
            "computer": country.computer,
        })
    return jsonify(output)


@app.route('/api/v1/building')
def building():
    output = dict({})
    filters = dict({})

    query = db.session.query(Province.province_id, Province.province_location_id, Building.building_id,
                             Building.upgrade_id, Building.health, Province.current_time
                             ).select_from(Building
                                           ).join(ProvinceHasBuilding).join(Province)
    print(request.args)
    if "game_id" in request.args:
        query = query.filter(Province.game_id == request.args["game_id"])
    if "current_time" in request.args:
        query = query.filter(Province.current_time == datetime.fromtimestamp(float(request.args["current_time"])))
    if "province_location_id" in request.args:
        query = query.filter(Province.province_location_id == request.args["province_location_id"])
    if "owner_id" in request.args:
        query = query.filter(Province.owner_id == request.args["owner_id"])
    for building in query.limit(100000).all():
        output[f"{building.building_id}_{building.province_id}"] = dict({
            "building_id": building.building_id,
            "province_location_id": building.province_location_id,
            "upgrade_id": building.upgrade_id,
            "health": building.health,
            "current_time": round(building.current_time.timestamp()),
        })
    return jsonify(output)


@app.route('/api/v1/trade')
def trade():
    output = dict({})
    filters = dict({})
    filters_exp = dict({})
    table = inspect(Trade)

    if "game_id" not in request.args:
        return "game_id is needed"

    if "day" in request.args:
        filters_exp["day"] = int(request.args["day"])
    for filter in table.c:
        if filter.name in request.args:
            filters[filter.name] = request.args[filter.name]

    for trade in Trade.query.filter_by(**filters).all():
        trade_dict = object_as_dict(trade)
        trade_dict["current_time"] = round(trade_dict["current_time"].timestamp())
        trade_dict.pop("game_id")
        output[trade_dict["trade_id"]] = trade_dict
    return jsonify(output)


@app.route('/api/v1/static/province')
def static_province():
    output = dict({})
    filters = dict({})
    table = inspect(StaticProvince)

    for filter in table.c:
        if filter.name in request.args:
            filters[filter.name] = request.args[filter.name]

    for static_province in StaticProvince.query.filter_by(**filters).all():
        static_province = object_as_dict(static_province)
        static_province.pop("map_id")
        static_province.pop("coastal")
        static_province.pop("static_province_id")
        output[static_province["province_location_id"]] = static_province
    return jsonify(output)


@app.route('/api/v1/static/research')
def static_research():
    return jsonify(data_researches)


@app.route('/api/v1/static/upgrade')
def staic_upgrade():
    return jsonify(data_upgrades)


@app.route('/api/v1/static/scenario')
def static_scenario():
    output = dict({})
    filters = dict({})
    table = inspect(Scenario)

    for filter in table.c:
        if filter.name in request.args:
            filters[filter.name] = request.args[filter.name]

    for static_scenario in Scenario.query.filter_by(**filters).all():
        static_scenario = object_as_dict(static_scenario)
        output[static_scenario["scenario_id"]] = static_scenario
    return jsonify(output)


def getGame(game_id):
    game = db.session.query(Game.game_id, Game.start_time, Game.current_time, Scenario.speed).join(Scenario).filter(
        Game.game_id == game_id).first()
    return game


def getScenarios():
    scenarios = Scenario.query.all()
    return scenarios


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


# run flask app
if __name__ == "__main__":
    app.run(debug=True, port=4444)
