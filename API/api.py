import json
import sys
import time
from datetime import datetime, timedelta

from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_compress import Compress
from flask_sqlalchemy import inspect
from sqlalchemy import func, between, case, desc, text
from flask_cors import CORS

from helpers.province_buidings import get_province_buildings, province_sort_by_building_cost
import constants
from helpers.production import get_production
from models import *

# create the object of Flask


app = Flask(__name__)

app.config['SECRET_KEY'] = constants.FLASK_SECRET

# SqlAlchemy Datadb.Model Configuration With Mysql
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{constants.MYSQL_USER}:{constants.MYSQL_USER_PASSWORD}@{constants.MYSQL_IP_ADDR}/{constants.MYSQL_DATABASE}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True

# Caching
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300

db = SQLAlchemy(app)
Compress(app)
CORS(app)
cache = Cache(app)

with open("static_informations/upgrades.json") as file:
    data_upgrades = json.loads(file.read())

with open("static_informations/researches.json") as file:
    data_researches = json.loads(file.read())


@app.route('/load')
def load():
    for k in cache.cache._cache:
        print(k, cache.get(k))


# creating our routes
@app.route('/api/v1/game/<game_id>')
@cache.cached(timeout=5000)
def game(game_id):
    output = {}
    game_id = int(game_id)
    query = db.session \
        .query(Game.game_id, Game.current_time, Game.start_time, Game.next_heal_time, Game.next_day_time,
               Game.end_time, Scenario.map_id, Scenario.name, Scenario.speed) \
        .join(Scenario)

    if game_id != -1:
        query = query.filter(Game.game_id == game_id)

    for game in query.all():
        output[game.game_id] = {
            "gid": game.game_id,
            "ct": round(game.current_time.timestamp()),
            "st": round(game.start_time.timestamp()),
            "nht": game.next_heal_time if game.next_heal_time is None else round(game.next_heal_time.timestamp()),
            "ndt": game.next_day_time if game.next_day_time is None else round(game.next_day_time.timestamp()),
            "et": game.end_time if game.end_time is None else round(game.end_time.timestamp()),
            "mid": game.map_id,
            "sn": game.name,
            "sp": game.speed,
        }
    return jsonify(output)


@app.route('/api/v1/team/<game_id>/')
@cache.cached(timeout=500)
def team(game_id):
    game = getGame(game_id)
    output = {}
    query = db.session.query(Team).filter(Team.game_id == game.game_id)

    for team in query.all():
        output[team.universal_team_id] = {
            "utid": team.universal_team_id,
            "tmid": team.team_id,
            "tn": team.name,
            "lid": team.leader_id,
            "ds": bool(team.deleted),
        }
    return jsonify(output)


@app.route('/api/v1/provinces/<game_id>/<mode>/<day>')
@cache.cached(timeout=50000)
def provinces(game_id, mode, day):
    output = {}
    game = getGame(game_id)
    day_time = get_newest_time(game, day)
    print(day_time)

    if "value" == mode:
        query = db.session.query(Province.province_id, Province.owner_id, Building.upgrade_id, Building.health,
                                 StaticProvince.province_location_id) \
            .select_from(Province) \
            .join(StaticProvince, Province.province_location_id == StaticProvince.province_location_id) \
            .join(ProvinceHasBuilding) \
            .join(Building) \
            .filter(StaticProvince.map_id == game.map_id) \
            .filter(Province.game_id == game.game_id) \
            .filter(Province.current_time == day_time)

    elif "list" == mode:
        query = db.session.query(Province.province_id, StaticProvince.province_location_id, Province.owner_id,
                                 Building.upgrade_id, Building.health, Province.morale, Province.province_state_id,
                                 Province.victory_points,
                                 case(
                                     [(StaticProvince.resource_production_type == 2, Province.resource_production)],
                                     else_=0
                                 ).label("r2"),
                                 case(
                                     [(StaticProvince.resource_production_type == 3, Province.resource_production)],
                                     else_=0
                                 ).label("r3"),
                                 case(
                                     [(StaticProvince.resource_production_type == 5, Province.resource_production)],
                                     else_=0
                                 ).label("r5"),
                                 case(
                                     [(StaticProvince.resource_production_type == 6, Province.resource_production)],
                                     else_=0
                                 ).label("r6"),
                                 case(
                                     [(StaticProvince.resource_production_type == 7, Province.resource_production)],
                                     else_=0
                                 ).label("r7"),
                                 Province.tax_production) \
            .select_from(Province) \
            .join(Country) \
            .join(StaticProvince, Province.province_location_id == StaticProvince.province_location_id) \
            .join(ProvinceHasBuilding) \
            .join(Building) \
            .filter(Province.game_id == game.game_id) \
            .filter(StaticProvince.map_id == game.map_id) \
            .filter(Province.current_time == day_time)

    else:
        query = db.session.query(Province).filter(Game.game_id == game_id).filter(Province.current_time == day_time)

    if "value" == mode:
        province_buildings = {}

        for province in query.all():
            if province.province_id not in province_buildings:
                province_buildings[province.province_id] = {
                    "pid": province.province_id,
                    "plid": province.province_location_id,
                    "oid": province.owner_id,
                    "upg": {},
                }
            province_buildings[province.province_id]["upg"][province.upgrade_id] = {
                "upid": province.upgrade_id,
                "ht": province.health
            }
        for province in province_buildings:
            province = province_buildings[province]
            province.update(get_province_buildings(province, data_upgrades, True))
        output = sorted(list(province_buildings.values()), reverse=True, key=province_sort_by_building_cost)[0:30]
        return jsonify(output)

    if "list" == mode:
        province_buildings = {}
        for province in query.all():
            if province.province_id not in province_buildings:
                province_buildings[province.province_id] = {
                    "pid": province.province_id,
                    "plid": province.province_location_id,
                    "ml": province.morale,
                    "psid": province.province_state_id,
                    "vp": province.victory_points,
                    "oid": province.owner_id,
                    "2": province.r2,
                    "3": province.r3,
                    "5": province.r5,
                    "6": province.r6,
                    "7": province.r7,
                    "21": province.tax_production,
                    "upg": {},
                }
            province_buildings[province.province_id]["upg"][province.upgrade_id] = {
                "upid": province.upgrade_id,
                "ht": province.health
            }
        for province in province_buildings:
            province = province_buildings[province]
            province.update(get_province_buildings(province, data_upgrades, False))

        output = province_buildings
        return jsonify(output)

    for province in query.limit(1000000).all():
        output[province.province_id] = {
            "ct": round(province.current_time.timestamp()),
            "ml": province.morale,
            "oid": province.owner_id,
            "pid": province.province_id,
            "plid": province.province_location_id,
            "psid": province.province_state_id,
            "rp": province.resource_production,
            "stid": province.stationary_army_id,
            "tp": province.tax_production,
            "vp": province.victory_points,
        }
    return jsonify(output)


@app.route('/api/v1/countrys/<int:game_id>/<mode>/<country_id>/<day>')
@cache.cached(timeout=50000)
def countrys(game_id, mode, country_id, day):
    if game_id is None:
        return "game_id is needed"
    country_id = int(country_id)
    day = int(day)
    game = getGame(game_id)
    day_time = get_newest_time(game, day)
    # Define Queries for different modes
    if mode == "stats":
        query = db.session.query(
            Country.country_id,
            Province.current_time,
            func.sum(Province.victory_points).label("victory_points"),
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
            func.count(Province.province_id).label("total_provinces_cities"),
            func.sum(case(
                [(StaticProvince.resource_production_type == 2, Province.resource_production)], else_=0
            )).label("r2"),
            func.sum(case(
                [(StaticProvince.resource_production_type == 3, Province.resource_production)], else_=0
            )).label("r3"),
            func.sum(case(
                [(StaticProvince.resource_production_type == 5, Province.resource_production)], else_=0
            )).label("r5"),
            func.sum(case(
                [(StaticProvince.resource_production_type == 6, Province.resource_production)], else_=0
            )).label("r6"),
            func.sum(case(
                [(StaticProvince.resource_production_type == 7, Province.resource_production)], else_=0
            )).label("r7"),
            func.sum(Province.tax_production).label("tax_production"),
            func.sum(Province.resource_production).label("total_resource_production"),
        ).select_from(Country) \
            .join(Province) \
            .join(StaticProvince, Province.province_location_id == StaticProvince.province_location_id) \
            .join(GameHasPlayer) \
            .filter(StaticProvince.map_id == game.map_id)
        if country_id == -1:
            query = query.filter(Province.current_time == day_time) \
                .group_by(Country.country_id)
        else:
            query = query.filter(Country.country_id == country_id).group_by(Province.current_time)

    elif mode == "rising_power":
        day_ago = get_nearest_time(game, day_time)
        query = db.session.query(Country.country_id,
                                 ((func.sum(
                                     case(
                                         [(Province.current_time == day_time, Province.victory_points)], else_=0
                                     )
                                 ))
                                  -
                                  func.sum(
                                      case(
                                          [(Province.current_time == day_ago, Province.victory_points)], else_=0
                                      )
                                  )
                                  ).label("5_day")) \
            .join(Province) \
            .filter(Province.game_id == game.game_id) \
            .order_by(desc("5_day")) \
            .group_by(Country)

    elif mode == "production":
        query = db.session.query(Newspaper.country_id, Newspaper.wtyp,
                                 func.sum(
                                     case(
                                         [(Newspaper.count > 0, Newspaper.count)], else_=0
                                     )
                                 ).label("noticed_weapons"),
                                 func.sum(
                                     case(
                                         [(Newspaper.count < 0, Newspaper.count * -1)], else_=0
                                     )
                                 ).label("lost_weapons")
                                 ) \
            .select_from(Newspaper) \
            .join(GameHasPlayer, GameHasPlayer.country_id == Newspaper.country_id) \
            .filter(GameHasPlayer.game_id == game_id) \
            .filter(Newspaper.time <= day_time) \
            .group_by(Newspaper.country_id, Newspaper.wtyp)

        if country_id != -1:
            query = query.filter(Newspaper.country_id == country_id)

    else:
        query = db.session \
            .query(Country.country_id, Country.team_id, Country.name.label("country_name"), Country.capital_id,
                   Player.player_id, Country.defeated, Country.computer, Player.name.label("player_name")) \
            .select_from(Country) \
            .join(GameHasPlayer) \
            .join(Player) \
            .filter(GameHasPlayer.game_id == game_id)

        if country_id != -1:
            query.filter(Country.country_id == country_id)

    # Execute different Queries

    if mode == "stats":
        output = {}
        for country in query.all():
            if country_id == -1:
                output[country.country_id] = {
                    "cid": country.country_id,
                    "ct": round(country.current_time.timestamp()),
                    "vp": int(country.victory_points),
                    "ml": round(country.morale),
                    "t_p": int(country.total_provinces),
                    "t_c": int(country.total_cities),
                    "t_ac": int(country.total_annexed_cities),
                    "t_mlc": int(country.total_mainland_cities),
                    "t_pc": int(country.total_provinces_cities),
                    "2": int(country.r2),
                    "3": int(country.r3),
                    "5": int(country.r5),
                    "6": int(country.r6),
                    "7": int(country.r7),
                    "21": int(country.tax_production),
                    "trp": int(country.total_resource_production),
                }
            else:
                if country.country_id not in output:
                    output[country.country_id] = {
                        "cid": country.country_id,
                        "ts": {},
                    }
                output[country.country_id]["ts"][round(country.current_time.timestamp())] = {
                    "ct": round(country.current_time.timestamp()),
                    "vp": int(country.victory_points),
                    "ml": round(country.morale),
                    "t_p": int(country.total_provinces),
                    "t_c": int(country.total_cities),
                    "t_ac": int(country.total_annexed_cities),
                    "t_mlc": int(country.total_mainland_cities),
                    "t_pc": int(country.total_provinces_cities),
                    "2": int(country.r2),
                    "3": int(country.r3),
                    "5": int(country.r5),
                    "6": int(country.r6),
                    "7": int(country.r7),
                    "21": int(country.tax_production),
                    "trp": int(country.total_resource_production),
                }
        return jsonify(output)

    elif mode == "rising_power":
        # Countrys sorted by last 5 days victorys
        ids = {country.country_id: pos for pos, country in enumerate(query.all())}
        query2 = db.session.query(
            Country.country_id,
            Province.current_time,
            func.sum(Province.victory_points).label("victory_points"),
            func.avg(Province.morale).label("morale"),
            func.sum(Province.resource_production).label("total_resource_production"), ) \
            .join(Province) \
            .filter(Province.game_id == game_id) \
            .group_by(Country, Province.current_time)

        if country_id != -1:
            query2 = query2.filter(Country.country_id == country_id)

        # Retrieve Country data
        # output = {key: {} for key in ids.keys()}
        output = {}
        for country in query2:
            pos = ids[country.country_id]
            if country.country_id not in output:
                output[country.country_id] = {
                    "cid": country.country_id,
                    "rspos": pos,
                    "ts": {}
                }
            output[country.country_id]["ts"][round(country.current_time.timestamp())] = {
                "vp": int(country.victory_points),
                "trp": int(country.total_resource_production),
            }
        return jsonify(output)

    elif mode == "production":
        output = {}
        for country in query.all():
            if country.country_id not in output:
                output[country.country_id] = {
                    "cid": country.country_id,
                    "wp": {}
                }
            output[country.country_id]["wp"][country.wtyp] = {
                "wtyp": int(country.wtyp),
                "ntw": int(country.noticed_weapons),
                "lsw": int(country.lost_weapons),
            }
        for country in output:
            country = output[country]
            country.update(get_production(country))
        return jsonify(output)

    else:
        output = {}
        for country in query.all():
            output[country.country_id] = {
                "cid": country.country_id,
                "pyn": country.player_name,
                "utid": country.team_id,
                "cn": country.country_name,
                "cpid": country.capital_id,
                "df": bool(country.defeated),
                "cp": bool(country.computer),
            }
        return jsonify(output)


@app.route('/api/v1/trade/<int:game_id>')
@cache.cached(timeout=500)
def trade(game_id):
    output = {}
    query = db.session.query(Trade).filter(Trade.game_id == game_id)
    for trade in query.all():
        output[trade.trade_id] = {
            "tdid": trade.trade_id,
            "am": trade.amount,
            "b": trade.buy,
            "ct": round(trade.current_time.timestamp()),
            "lm": trade.limit,
            "odid": trade.order_id,
            "oid": trade.owner_id,
            "rsrt": trade.resource_type,
        }
    return jsonify(output)


@app.route('/api/v1/static/province/<int:map_id>')
@cache.cached(timeout=5000)
def static_province(map_id):
    output = {}

    query = db.session.query(StaticProvince.province_location_id, StaticProvince.coordinate_x,
                             StaticProvince.coordinate_y,
                             StaticProvince.b, StaticProvince.mainland_id, StaticProvince.name, StaticProvince.region,
                             StaticProvince.resource_production_type, StaticProvince.terrain_type
                             ) \
        .filter(StaticProvince.map_id == map_id)

    for static_province in query.all():
        output[static_province.province_location_id] = {
            "plid": static_province.province_location_id,
            "bt": static_province.b,
            "cdx": static_province.coordinate_x,
            "cdy": static_province.coordinate_y,
            "mlid": static_province.mainland_id,
            "pn": static_province.name,
            "rg": static_province.region,
            "rpt": static_province.resource_production_type,
            "tt": static_province.terrain_type,
        }
    return jsonify(output)


@app.route('/api/v1/static/research')
@cache.cached()
def static_research():
    return jsonify(data_researches)


@app.route('/api/v1/static/upgrade')
@cache.cached()
def staic_upgrade():
    return jsonify(data_upgrades)


@app.route('/api/v1/static/scenario')
@cache.cached()
def static_scenario():
    output = dict({})
    filters = dict({})
    table = inspect(Scenario)

    for filter in table.c:
        if filter.name in request.args:
            filters[filter.name] = request.args[filter.name]

    for static_scenario in Scenario.query.filter_by(**filters).all():
        output[static_scenario.scenario_id] = {
            "sid": static_scenario.scenario_id,
            "mid": static_scenario.map_id,
            "sn": static_scenario.name,
            "sp": static_scenario.speed,
        }
    return jsonify(output)


def getGame(game_id):
    game = db.session.query(Game.game_id, Game.start_time, Game.current_time, Scenario.speed, Scenario.map_id,
                            Game.scenario_id).join(Scenario).filter(
        Game.game_id == game_id).first()
    return game


@cache.cached(timeout=60000, key_prefix="scenarios")
def getScenarios():
    scenarios = Scenario.query.all()
    return scenarios


def get_newest_time(game, day):
    time_start = time.mktime(game["start_time"].timetuple()) + (int(day) * 3600 * 24) - 300
    time_end = time.mktime(game["start_time"].timetuple()) + int(day) * 3600 * 24 + 3600 * 24 + 300
    query = db.session.query(func.max(Province.current_time)).filter(
        between(Province.current_time, func.FROM_UNIXTIME(time_start), func.FROM_UNIXTIME(time_end)))
    newest_time = query.scalar()
    return newest_time

def get_nearest_time(game, day_time: datetime):
    query = db.session.query(
        Province.current_time,
        (func.abs(func.timestampdiff(text("SECOND"), Province.current_time, day_time - timedelta(days=5)))).label(
            "nearest_time")) \
        .filter(Province.game_id == game["game_id"]) \
        .group_by(Province.current_time) \
        .order_by("nearest_time")
    newest_time = query.limit(1).all()[0][0]
    return newest_time


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


# run flask app
if __name__ == "__main__":
    app.run(debug=True, port=4444)
