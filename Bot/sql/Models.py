# coding: utf-8
from sqlalchemy import BigInteger, Boolean, Column, Float, ForeignKey, Index, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Player(Base):
    __tablename__ = 'player'

    player_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    site_user_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(75, 'utf8mb4_unicode_ci'), nullable=False)


class Research(Base):
    __tablename__ = 'research'

    universal_research_id = Column(Integer, autoincrement=True, primary_key=True)
    owner_id = Column(Integer)
    column_id = Column(Integer)
    research_min_id = Column(Integer)
    research_max_id = Column(Integer)
    valid_from = Column(TIMESTAMP, nullable=False)
    valid_until = Column(TIMESTAMP)
    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)

    game = relationship('Game')


class Scenario(Base):
    __tablename__ = 'scenario'

    scenario_id = Column(Integer, primary_key=True)
    map_id = Column(Integer)
    name = Column(String(45))
    speed = Column(Integer)


class StaticCountry(Base):
    __tablename__ = 'static_country'

    static_country_id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(45))
    map_id = Column(Integer)
    native_computer = Column(Boolean)
    country_id = Column(Integer)
    faction = Column(Integer)


class StaticProvince(Base):
    __tablename__ = 'static_province'

    static_province_id = Column(Integer, autoincrement=True, primary_key=True)
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
    coastal = Column(Boolean)


class Game(Base):
    __tablename__ = 'game'

    game_id = Column(Integer, primary_key=True)
    scenario_id = Column(ForeignKey('scenario.scenario_id'), nullable=False, index=True)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    current_time = Column(TIMESTAMP)
    next_day_time = Column(TIMESTAMP)
    next_heal_time = Column(TIMESTAMP)
    open_slots = Column(Integer)

    scenario = relationship('Scenario')


class Army(Base):
    __tablename__ = 'army'

    universal_army_id = Column(BigInteger, autoincrement=True, primary_key=True, nullable=False, unique=True)
    army_id = Column(BigInteger)
    owner_id = Column(BigInteger)
    presentation_warfare_id = Column(Integer)
    army_number = Column(Integer)
    kills = Column(Integer)
    health_point = Column(Float)
    next_attack_time = Column(TIMESTAMP)
    next_anti_aircraft_attack_time = Column(TIMESTAMP)
    radar_type = Column(Integer)
    radar_size = Column(Integer)
    valid_from = Column(TIMESTAMP, nullable=False)
    valid_until = Column(TIMESTAMP)
    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    static_province_id = Column(ForeignKey('static_province.static_province_id'), index=True)

    game = relationship('Game')
    static_province = relationship('StaticProvince')


class ArmyLossesGain(Base):
    __tablename__ = 'army_losses_gains'

    army_loss_gain_id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    owner_id = Column(BigInteger, nullable=False)
    warfare_type_id = Column(Integer, nullable=False)
    division = Column(Integer)
    count = Column(Integer)
    time = Column(TIMESTAMP)
    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)

    game = relationship('Game')


class Building(Base):
    __tablename__ = 'building'
    __table_args__ = (
        Index('index2', 'building_id', 'health', 'upgrade_id'),
    )

    building_id = Column(BigInteger, autoincrement=True, primary_key=True, nullable=False)
    upgrade_id = Column(Integer, nullable=False)
    health = Column(Integer)
    valid_from = Column(TIMESTAMP, nullable=False)
    valid_until = Column(TIMESTAMP)
    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    static_province_id = Column(ForeignKey('static_province.static_province_id'), primary_key=True, nullable=False,
                                index=True)

    game = relationship('Game')
    static_province = relationship('StaticProvince')


class Command(Base):
    __tablename__ = 'command'

    command_id = Column(BigInteger, autoincrement=True, primary_key=True, nullable=False)
    army_id = Column(BigInteger)
    command_type = Column(String(4))
    transport_level = Column(Integer)
    start_coordinate_x = Column(Integer)
    start_coordinate_y = Column(Integer)
    target_coordinate_x = Column(Integer)
    target_coordinate_y = Column(Integer)
    start_time = Column(TIMESTAMP)
    arrival_time = Column(TIMESTAMP)
    valid_from = Column(TIMESTAMP)
    valid_until = Column(TIMESTAMP)
    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)

    game = relationship('Game')


class GameHasPlayer(Base):
    __tablename__ = 'game_has_player'

    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    player_id = Column(ForeignKey('player.player_id'), primary_key=True, nullable=False, index=True)
    country_id = Column(BigInteger, nullable=False, index=True)

    game = relationship('Game')
    player = relationship('Player')


class Province(Base):
    __tablename__ = 'province'
    __table_args__ = (
        Index('ix_gid_plid_vf_vl', 'game_id', 'province_id', 'valid_from', 'valid_until'),
        Index('ix_game_id_valid_from_valid_until', 'game_id', 'valid_from', 'valid_until'),
        Index('ix_game_id_province_location_id_valid_from_valid_until', 'game_id', 'valid_from', 'valid_until')
    )

    province_id = Column(BigInteger, autoincrement=True, primary_key=True, nullable=False)
    owner_id = Column(BigInteger, nullable=False)
    morale = Column(Integer)
    province_state_id = Column(Integer)
    stationary_army_id = Column(Integer)
    victory_points = Column(Integer)
    resource_production = Column(Integer)
    tax_production = Column(Integer)
    valid_from = Column(TIMESTAMP, nullable=False)
    valid_until = Column(TIMESTAMP)
    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    static_province_id = Column(ForeignKey('static_province.static_province_id'), primary_key=True, nullable=False,
                                index=True)

    game = relationship('Game')
    static_province = relationship('StaticProvince')


class Team(Base):
    __tablename__ = 'team'

    universal_team_id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    team_id = Column(Integer)
    name = Column(String(45))
    leader_id = Column(Integer)
    deleted = Column(Boolean)

    game = relationship('Game')


class Trade(Base):
    __tablename__ = 'trade'

    trade_id = Column(BigInteger, autoincrement=True, primary_key=True, nullable=False)
    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    order_id = Column(Integer)
    owner_id = Column(BigInteger, nullable=False)
    amount = Column(Integer)
    resource_type = Column(Integer)
    limit = Column(Float)
    buy = Column(Boolean)
    valid_from = Column(TIMESTAMP)
    valid_until = Column(TIMESTAMP)

    game = relationship('Game')


class Country(Base):
    __tablename__ = 'country'

    universal_country_id = Column(BigInteger, autoincrement=True, primary_key=True, nullable=False)
    country_id = Column(BigInteger, nullable=False)
    team_id = Column(ForeignKey('team.universal_team_id'), index=True)
    capital_id = Column(Integer)
    defeated = Column(Boolean)
    computer = Column(Boolean)
    valid_from = Column(TIMESTAMP, nullable=False)
    valid_until = Column(TIMESTAMP)
    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    static_country_id = Column(ForeignKey('static_country.static_country_id'), primary_key=True, nullable=False,
                               index=True)

    game = relationship('Game')
    static_country = relationship('StaticCountry')
    team = relationship('Team')


class WarfareUnit(Base):
    __tablename__ = 'warfare_unit'

    universal_warfare_id = Column(BigInteger, autoincrement=True, primary_key=True, nullable=False)
    warfare_id = Column(BigInteger, nullable=False)
    universal_army_id = Column(ForeignKey('army.universal_army_id'), primary_key=True, nullable=False)
    warfare_type_id = Column(Integer)
    size = Column(Integer)
    health_point = Column(Integer)

    universal_army = relationship('Army')


class GamesAccount(Base):
    __tablename__ = 'games_accounts'

    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    account_id = Column(ForeignKey('account.account_id'), primary_key=True, nullable=False, index=True)
    joined = Column(Boolean)
    server_uuid = Column(String(45))

    account = relationship('Account')
    game = relationship('Game')


class Account(Base):
    __tablename__ = 'account'

    account_id = Column(Integer, primary_key=True)
    email = Column(String(45))
    username = Column(String(45))
    password = Column(String(45))
