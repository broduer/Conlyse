from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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
