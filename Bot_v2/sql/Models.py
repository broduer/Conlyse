# coding: utf-8
from sqlalchemy import BigInteger, Column, Float, ForeignKey, Integer, String, TIMESTAMP, BOOLEAN
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Building(Base):
    __tablename__ = 'building'

    building_id = Column(BigInteger, primary_key=True, autoincrement=True)
    upgrade_id = Column(Integer, nullable=False)
    health = Column(Integer)

    provinces = relationship('Province', secondary='province_has_building')


class Player(Base):
    __tablename__ = 'player'

    player_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    site_user_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(75, 'utf8mb4_unicode_ci'), nullable=False)


class Scenario(Base):
    __tablename__ = 'scenario'

    scenario_id = Column(Integer, primary_key=True)
    map_id = Column(Integer)
    name = Column(String(45))
    speed = Column(Integer)


class StaticProvince(Base):
    __tablename__ = 'static_province'

    static_province_id = Column(Integer, primary_key=True)
    province_location_id = Column(Integer, nullable=False)
    map_id = Column(Integer)
    province_type = Column(Integer)
    name = Column(String(50))
    coordinate_x = Column(Integer)
    coordinate_y = Column(Integer)
    mainland_id = Column(Integer)
    region = Column(Integer)
    base_production = Column(Integer)
    terrain_type = Column(Integer)
    resource_production_type = Column(Integer)
    b = Column(String(10000))
    coastal = Column(BOOLEAN)


class Game(Base):
    __tablename__ = 'game'

    game_id = Column(Integer, primary_key=True)
    scenario_id = Column(ForeignKey('scenario.scenario_id'), nullable=False, index=True)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    current_time = Column(TIMESTAMP)
    next_day_time = Column(TIMESTAMP)
    next_heal_time = Column(TIMESTAMP)

    scenario = relationship('Scenario')


class Team(Base):
    __tablename__ = 'team'

    universal_team_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    team_id = Column(Integer)
    name = Column(String(45, 'utf8mb4_unicode_ci'))
    leader_id = Column(Integer)
    deleted = Column(BOOLEAN)

    game = relationship('Game')


class Country(Base):
    __tablename__ = 'country'

    country_id = Column(BigInteger, primary_key=True, autoincrement=True)
    player_id = Column(Integer)
    team_id = Column(ForeignKey('team.universal_team_id'), index=True)
    name = Column(String(45))
    capital_id = Column(Integer)
    defeated = Column(BOOLEAN)
    computer = Column(BOOLEAN)

    team = relationship('Team')


class GameHasPlayer(Base):
    __tablename__ = 'game_has_player'

    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    player_id = Column(ForeignKey('player.player_id'), primary_key=True, nullable=False, index=True)
    country_id = Column(ForeignKey('country.country_id'), primary_key=True, nullable=False, index=True)

    country = relationship('Country')
    game = relationship('Game')
    player = relationship('Player')


class Newspaper(Base):
    __tablename__ = 'newspaper'

    article_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    msg_typ = Column(Integer, nullable=False)
    country_id = Column(ForeignKey('country.country_id'), primary_key=True, nullable=False, index=True)
    wtyp = Column(Integer, nullable=False)
    whtyp = Column(Integer)
    division = Column(Integer)
    count = Column(Integer)
    time = Column(TIMESTAMP)

    country = relationship('Country')


class Province(Base):
    __tablename__ = 'province'

    province_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    province_location_id = Column(Integer, nullable=False)
    owner_id = Column(ForeignKey('country.country_id'), primary_key=True, nullable=False, index=True)
    morale = Column(Integer)
    province_state_id = Column(Integer)
    stationary_army_id = Column(Integer)
    victory_points = Column(Integer)
    resource_production = Column(Integer)
    tax_production = Column(Integer)
    current_time = Column(TIMESTAMP, nullable=False)
    map_id = Column(Integer)
    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)

    game = relationship('Game')
    owner = relationship('Country')


class Trade(Base):
    __tablename__ = 'trade'

    trade_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    order_id = Column(String(45))
    owner_id = Column(ForeignKey('country.country_id'), primary_key=True, nullable=False, index=True)
    amount = Column(Integer)
    resource_type = Column(Integer)
    limit = Column(Float)
    buy = Column(BOOLEAN)
    current_time = Column(TIMESTAMP)

    game = relationship('Game')
    owner = relationship('Country')


class ProvinceHasBuilding(Base):
    __tablename__ = 'province_has_building'

    province_id = Column(ForeignKey('province.province_id'), primary_key=True, nullable=False, index=True)
    building_id = Column(ForeignKey('building.building_id'), primary_key=True, nullable=False, index=True)

    province = relationship("Province", overlaps="provinces")
    building = relationship("Building", overlaps="provinces")
