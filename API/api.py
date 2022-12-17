import json
import time
from datetime import datetime, timedelta

from flask import Flask, jsonify, request
# from flask_caching import Cache
from flask_compress import Compress
from flask_sqlalchemy import inspect, SQLAlchemy
from sqlalchemy import func, between, case, desc, text, and_, or_, distinct, select, bindparam
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.orm import aliased
from flask_cors import CORS

from helpers.province_buidings import get_province_buildings, province_sort_by_building_cost

from dotenv import load_dotenv
from os import getenv

from models import Province, StaticProvince, Game, \
    Country, StaticCountry, \
    Team, Trade, Scenario, Building, GameHasPlayer, Player, Research

# create the object of Flask

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = getenv("FLASK_SECRET")

# SqlAlchemy Datadb.Model Configuration With Mysql
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{getenv("MYSQL_USER")}:{getenv("MYSQL_USER_PASSWORD")}@{getenv("MYSQL_IP_ADDR")}/{getenv("MYSQL_DATABASE")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True

# Caching
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300

db = SQLAlchemy(app)
Compress(app)
CORS(app)

with open("static_informations/upgrades.json") as file:
    data_upgrades = json.loads(file.read())

with open("static_informations/researches.json") as file:
    data_researches = json.loads(file.read())

with open("static_informations/warfare_types.json") as file:
    data_warfare_types = json.loads(file.read())

'''
@app.route('/load')
def load():
    for k in cache.cache._cache:
        print(k, cache.get(k))
'''


# creating our routes
@app.route('/api/v2/game/<game_id>')
def game(game_id):
    output = {}
    game_id = int(game_id)
    query = db.session \
        .query(Game.game_id, Game.current_time, Game.start_time, Game.next_heal_time, Game.next_day_time,
               Game.end_time, Scenario.map_id, Scenario.name, Scenario.speed) \
        .join(Scenario)

    if game_id != -1:
        query = query.filter(Game.game_id == game_id)
    else:
        query = query.filter(or_(
            Game.next_day_time != None,
            Game.end_time != None))

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


@app.route('/api/v2/team/<game_id>')
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


@app.route('/api/v2/provinces/<game_id>/<mode>/<timestamp>')
def provinces(game_id, mode, timestamp):
    output = {}
    game = getGame(game_id)
    timestamp = int(timestamp)
    if timestamp == 0:
        date_timestamp = None
    else:
        date_timestamp = datetime.fromtimestamp(timestamp)

    if "value" == mode:
        query = db.session.query(Province.province_id, Province.owner_id, Building.upgrade_id, Building.health,
                                 StaticProvince.static_province_id, Building.valid_until) \
            .select_from(Province) \
            .join(StaticProvince, Province.static_province_id == StaticProvince.static_province_id) \
            .join(Building,
                  and_(Province.game_id == Building.game_id,
                       Province.static_province_id == Building.static_province_id)) \
            .filter(Province.game_id == game.game_id)
        query = add_timestamp_filter_building(date_timestamp, query)

    elif "list" == mode:
        query = db.session.query(Province.province_id, StaticProvince.static_province_id, Province.owner_id,
                                 Building.upgrade_id, Building.health, Province.morale,
                                 Province.province_state_id,
                                 Province.victory_points,
                                 case(
                                     [(StaticProvince.resource_production_type == 2,
                                       Province.resource_production)],
                                     else_=0
                                 ).label("r2"),
                                 case(
                                     [(StaticProvince.resource_production_type == 3,
                                       Province.resource_production)],
                                     else_=0
                                 ).label("r3"),
                                 case(
                                     [(StaticProvince.resource_production_type == 5,
                                       Province.resource_production)],
                                     else_=0
                                 ).label("r5"),
                                 case(
                                     [(StaticProvince.resource_production_type == 6,
                                       Province.resource_production)],
                                     else_=0
                                 ).label("r6"),
                                 case(
                                     [(StaticProvince.resource_production_type == 7,
                                       Province.resource_production)],
                                     else_=0
                                 ).label("r7"),
                                 Province.tax_production) \
            .select_from(Province) \
            .join(StaticProvince) \
            .join(Building,
                  and_(Province.game_id == Building.game_id,
                       Province.static_province_id == Building.static_province_id)) \
            .filter(Province.game_id == game.game_id)
        query = add_timestamp_filter_building(date_timestamp, query)
    else:
        query = db.session.query(Province).filter(Province.game_id == game_id)

    query = add_timestamp_filter_province(date_timestamp, query)

    if "value" == mode:
        province_buildings = {}

        for province in query.all():
            if province.static_province_id not in province_buildings:
                province_buildings[province.static_province_id] = {
                    "pid": province.province_id,
                    "plid": province.static_province_id,
                    "oid": province.owner_id,
                    "upg": {},
                }
            province_buildings[province.static_province_id]["upg"][province.upgrade_id] = {
                "upid": province.upgrade_id,
                "ht": province.health,
            }
        for province in province_buildings.values():
            province.update(get_province_buildings(province, data_upgrades, True))
        output = sorted(list(province_buildings.values()), reverse=True, key=province_sort_by_building_cost)[0:30]
        return jsonify(output)

    if "list" == mode:
        province_buildings = {}
        for province in query.all():
            if province.static_province_id not in province_buildings:
                province_buildings[province.static_province_id] = {
                    "pid": province.province_id,
                    "plid": province.static_province_id,
                    "ml": province.morale,
                    "psid": province.province_state_id,
                    "vp": province.victory_points,
                    "oid": province.owner_id,
                    "1": province.r2,
                    "2": province.r3,
                    "4": province.r5,
                    "5": province.r6,
                    "6": province.r7,
                    "20": province.tax_production,
                    "upg": {},
                }
            province_buildings[province.static_province_id]["upg"][province.upgrade_id] = {
                "upid": province.upgrade_id,
                "ht": province.health
            }
        for province in province_buildings.values():
            province.update(get_province_buildings(province, data_upgrades, False))

        output = province_buildings
        return jsonify(output)

    for province in query.all():
        output[province.static_province_id] = {
            "ct": round(province.valid_from.timestamp()),
            "ml": province.morale,
            "oid": province.owner_id,
            "pid": province.province_id,
            "plid": province.static_province_id,
            "psid": province.province_state_id,
            "rp": province.resource_production,
            "stid": province.stationary_army_id,
            "tp": province.tax_production,
            "vp": province.victory_points,
        }
    return jsonify(output)


@app.route('/api/v2/countrys/<int:game_id>/<mode>/<country_id>/<from_timestamp>/<until_timestamp>')
def countrys(game_id, mode, country_id, from_timestamp, until_timestamp):
    if game_id is None:
        return "game_id is needed"
    country_id = int(country_id)
    from_timestamp = int(from_timestamp)
    until_timestamp = int(until_timestamp)
    game = getGame(game_id)
    date_timestamp = None

    # Timestamp needs to be converted from unix format to datetime
    if (from_timestamp == until_timestamp) and until_timestamp > 0:
        date_timestamp = datetime.fromtimestamp(until_timestamp)
    elif from_timestamp == 0:
        date_timestamp = game.current_time
    elif (from_timestamp > 0) and (until_timestamp > 0):
        from_timestamp = datetime.fromtimestamp(from_timestamp)
        until_timestamp = datetime.fromtimestamp(until_timestamp)
    else:
        date_timestamp = None

    # Define Queries for different modes
    if mode == "stats":
        province_b = aliased(Province)
        if date_timestamp:
            timestamps = select(
                distinct(bindparam("date_timestamp", value=date_timestamp, type_=TIMESTAMP)).label("valid_from"),
                Province.owner_id.label("owner_id")) \
                .filter(Province.game_id == game_id)
        else:
            timestamps = select([distinct(func.date_add(func.date(Province.valid_from), text(
                'interval ceil(hour(province.valid_from)/ 24)*24 HOUR'))).label("valid_from"),
                                 Province.owner_id.label("owner_id")]) \
                .filter(Province.game_id == game_id) \
                .filter(Province.valid_from > from_timestamp).filter(Province.valid_from < until_timestamp)

        if country_id != -1:
            timestamps = timestamps.filter(Province.owner_id == country_id)

        timestamps = timestamps.alias("timestamp_a")
        timestamp_a = timestamps
        query = db.session.query(
            timestamp_a.c.owner_id,
            timestamp_a.c.valid_from,
            func.sum(province_b.victory_points).label("victory_points"),
            func.avg(province_b.morale).label("morale"),
            func.sum(case(
                [(province_b.province_state_id <= 52, 1)], else_=0
            )).label("total_provinces"),
            func.sum(case(
                [(province_b.province_state_id >= 53, 1)], else_=0
            )).label("total_cities"),
            func.sum(case(
                [(province_b.province_state_id == 55, 1)], else_=0
            )).label("total_mainland_cities"),
            func.sum(case(
                [(province_b.province_state_id == 54, 1)], else_=0
            )).label("total_annexed_cities"),
            func.count(province_b.province_id).label("total_provinces_cities"),
            func.sum(case(
                [(StaticProvince.resource_production_type == 2, province_b.resource_production)], else_=0
            )).label("r2"),
            func.sum(case(
                [(StaticProvince.resource_production_type == 3, province_b.resource_production)], else_=0
            )).label("r3"),
            func.sum(case(
                [(StaticProvince.resource_production_type == 5, province_b.resource_production)], else_=0
            )).label("r5"),
            func.sum(case(
                [(StaticProvince.resource_production_type == 6, province_b.resource_production)], else_=0
            )).label("r6"),
            func.sum(case(
                [(StaticProvince.resource_production_type == 7, province_b.resource_production)], else_=0
            )).label("r7"),
            func.sum(province_b.tax_production).label("tax_production"),
            func.sum(province_b.resource_production).label("total_resource_production"),
        ).select_from(timestamps) \
            .join(province_b,
                  and_(
                      province_b.game_id == game_id,
                      and_(province_b.owner_id == timestamp_a.c.owner_id,
                           and_(or_(
                               and_(province_b.valid_from <= timestamp_a.c.valid_from,
                                    province_b.valid_until > timestamp_a.c.valid_from),

                               (province_b.valid_from == timestamp_a.c.valid_from),

                               and_(province_b.valid_until == None,
                                    province_b.valid_from < timestamp_a.c.valid_from)
                           ))))) \
            .join(StaticProvince, province_b.static_province_id == StaticProvince.static_province_id) \
            .group_by(timestamp_a.c.valid_from, timestamp_a.c.owner_id)

    elif mode == "rising_power":
        # Currently Rising Power isn't implemented to be calculated for every timestamp
        if not date_timestamp:
            return
        current_time = date_timestamp
        day_ago = current_time - timedelta(days=5)
        query = db.session.query(Province.owner_id,
                                 ((func.sum(
                                     case(
                                         [((or_(
                                             and_(Province.valid_from <= current_time,
                                                  Province.valid_until > current_time),

                                             (Province.valid_from == current_time),

                                             and_(Province.valid_until == None,
                                                  Province.valid_from < current_time)
                                         )), Province.victory_points)], else_=0
                                     )
                                 ))
                                  -
                                  func.sum(
                                      case(
                                          [((or_(
                                              and_(Province.valid_from <= day_ago,
                                                   Province.valid_until > day_ago),

                                              (Province.valid_from == day_ago),

                                              and_(Province.valid_until == None,
                                                   Province.valid_from < day_ago)
                                          )), Province.victory_points)], else_=0
                                      )
                                  )
                                  ).label("day_5")) \
            .filter(Province.game_id == game.game_id) \
            .order_by(desc("day_5")) \
            .group_by(Province.owner_id)
    elif mode == "research":
        query = db.session.query(Research).filter(Research.game_id == game_id)
        if country_id != -1:
            query = query.filter(Research.owner_id == country_id)
    else:
        if not date_timestamp:
            return
        query = db.session \
            .query(Country.country_id, Country.capital_id, Country.computer, Country.defeated, Country.team_id,
                   StaticCountry.name.label("country_name"), StaticCountry.native_computer,
                   Player.player_id, Player.site_user_id, Player.name.label("player_name")) \
            .join(GameHasPlayer, and_(
            Country.country_id == GameHasPlayer.country_id,
            or_(
                and_(Country.valid_from <= date_timestamp,
                     Country.valid_until > date_timestamp),

                (Country.valid_from == date_timestamp),

                and_(Country.valid_until == None,
                     Country.valid_from < date_timestamp),

                and_(Country.valid_until == None,
                     date_timestamp == None)

            )
        )) \
            .join(Player) \
            .join(StaticCountry) \
            .filter(GameHasPlayer.game_id == game_id)

        if country_id != -1:
            query = query.filter(Country.country_id == country_id)
    # Execute different Queries

    if mode == "stats":
        output = {}
        for country in query.all():
            if country.owner_id not in output:
                output[country.owner_id] = {
                    "cid": country.owner_id,
                    "ts": {},
                }
            if isinstance(country.valid_from, str):
                valid_from = round(datetime.fromisoformat(country.valid_from).timestamp())
            else:
                valid_from = round(country.valid_from.timestamp())
            output[country.owner_id]["ts"][valid_from] = {
                "ct": valid_from,
                "vp": int(country.victory_points),
                "ml": round(country.morale),
                "t_p": int(country.total_provinces),
                "t_c": int(country.total_cities),
                "t_ac": int(country.total_annexed_cities),
                "t_mlc": int(country.total_mainland_cities),
                "t_pc": int(country.total_provinces_cities),
                "1": int(country.r2),
                "2": int(country.r3),
                "4": int(country.r5),
                "5": int(country.r6),
                "6": int(country.r7),
                "20": int(country.tax_production),
                "trp": int(country.total_resource_production),
            }
        return jsonify(output)

    elif mode == "rising_power":
        # Countrys sorted by last 5 days victorys
        output = {}
        for pos, country in enumerate(query.all()):
            output[country.owner_id] = {
                "cid": country.owner_id,
                "rs_pos": pos,
                "day_5": int(country.day_5),
            }
        return jsonify(output)

    elif mode == "research":
        output = {}
        for country in query.all():
            if country.owner_id not in output:
                output[country.owner_id] = {
                    "cid": country.owner_id,
                    "rs": {}
                }
            output[country.owner_id]["rs"][country.universal_research_id] = {
                "usrid": country.universal_research_id,
                "rscid": country.column_id,
                "rsmin_id": country.research_min_id,
                "rsmax_id": country.research_max_id,
                "vf": round(country.valid_from.timestamp()),
                "vu": round(country.valid_until.timestamp()),
            }
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


@app.route('/api/v2/trade/<int:game_id>')
def trade(game_id):
    output = {}
    query = db.session.query(Trade).filter(Trade.game_id == game_id).filter(Trade.valid_until == None)
    for trade in query.all():
        output[trade.trade_id] = {
            "tdid": trade.trade_id,
            "am": trade.amount,
            "b": trade.buy,
            "ct": round(trade.valid_from.timestamp()),
            "lm": trade.limit,
            "odid": trade.order_id,
            "oid": trade.owner_id,
            "rsrt": trade.resource_type,
        }
    return jsonify(output)


@app.route('/api/v2/static/province/<int:map_id>')
def static_province(map_id):
    output = {}

    query = db.session.query(StaticProvince.static_province_id, StaticProvince.coordinate_x,
                             StaticProvince.coordinate_y,
                             StaticProvince.b, StaticProvince.mainland_id, StaticProvince.name, StaticProvince.region,
                             StaticProvince.resource_production_type, StaticProvince.terrain_type
                             ) \
        .filter(StaticProvince.map_id == map_id)

    for static_province in query.all():
        output[static_province.static_province_id] = {
            "plid": static_province.static_province_id,
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


@app.route('/api/v2/static/research')
def static_research():
    return jsonify(data_researches)


@app.route('/api/v2/static/warfare_types')
def static_warfare_types():
    return jsonify(data_warfare_types)


@app.route('/api/v2/static/upgrade')
def static_upgrade():
    return jsonify(data_upgrades)


@app.route('/api/v2/static/scenario')
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
    game = db.session.query(Game.game_id, Game.start_time, Game.current_time, Game.end_time,
                            Scenario.scenario_id, Scenario.speed).join(Scenario).filter(
        Game.game_id == game_id).first()
    return game


def getScenarios():
    scenarios = Scenario.query.all()
    return scenarios


def add_timestamp_filter_building(date_timestamp, query):
    if date_timestamp:
        return query.filter(or_(Building.valid_from == date_timestamp,
                                and_(Building.valid_from < date_timestamp, date_timestamp < Building.valid_until),
                                and_(Building.valid_until == None,
                                     Building.valid_from < date_timestamp)))
    else:
        return query.filter(Building.valid_until == None)


def add_timestamp_filter_province(date_timestamp, query):
    if date_timestamp:
        return query.filter(or_(Province.valid_from == date_timestamp,
                                and_(Province.valid_from < date_timestamp,
                                     date_timestamp < Province.valid_until),
                                and_(Province.valid_until == None,
                                     Province.valid_from < date_timestamp)))
    else:
        return query.filter(Province.valid_until == None)


# run flask app
if __name__ == "__main__":
    app.run(debug=True, port=4444)
