from sqlalchemy import BigInteger, Boolean, Column, Float, ForeignKey, Index, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Player(Base):
    __tablename__ = 'player'

    player_id = Column(BigInteger, primary_key=True, nullable=False)
    site_user_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(75, 'utf8mb4_unicode_ci'), nullable=False)


class Proxy(Base):
    __tablename__ = 'proxy'

    proxy_id = Column(Integer, primary_key=True, autoincrement=True)
    exit_node_ip = Column(String(45))
    exit_node_id = Column(String(45))
    local_ip = Column(String(45))
    local_port = Column(Integer)


class Server(Base):
    __tablename__ = 'server'

    server_uuid = Column(String(45), primary_key=True)
    maximum_accounts = Column(Integer)


class Account(Base):
    __tablename__ = 'account'

    account_id = Column(Integer, primary_key=True)
    email = Column(String(45))
    username = Column(String(45))
    password = Column(String(45))
    proxy_id = Column(ForeignKey('proxy.proxy_id'), index=True)
    server_uuid = Column(ForeignKey('server.server_uuid'), index=True)

    proxy = relationship('Proxy')
    server = relationship('Server')


class Game(Base):
    __tablename__ = 'game'

    game_id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(ForeignKey('scenario.scenario_id'), nullable=False, index=True)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    current_time = Column(TIMESTAMP)
    next_day_time = Column(TIMESTAMP)
    next_heal_time = Column(TIMESTAMP)
    open_slots = Column(Integer)

    scenario = relationship('Scenario')

class Scenario(Base):
    __tablename__ = 'scenario'

    scenario_id = Column(Integer, primary_key=True)
    map_id = Column(Integer)
    name = Column(String(45))
    speed = Column(Integer)

class GamesAccount(Base):
    __tablename__ = 'games_accounts'

    game_id = Column(ForeignKey('game.game_id'), primary_key=True, nullable=False, index=True)
    account_id = Column(ForeignKey('account.account_id'), primary_key=True, nullable=False, index=True)
    joined = Column(Boolean)

    account = relationship('Account')
    game = relationship('Game')
