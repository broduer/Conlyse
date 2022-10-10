from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class ServerRegisterRequest:
    server_uuid: str


@dataclass
class ProxyRegisterRequest(ServerRegisterRequest):
    pass


@dataclass
class BotRegisterRequest(ServerRegisterRequest):
    maximum_games: int


@dataclass
class ServerRegisterAnswer:
    server_uuid: str
    successful: bool
    response_code: Exception = None


@dataclass
class AccountRegisterRequest:
    server_uuid: str
    email: str
    username: str
    password: str
    local_ip: str
    local_port: int
    proxy_username: str = None
    proxy_password: str = None


@dataclass
class AccountRegisterAnswer:
    server_uuid: str
    email: str
    username: str
    password: str
    local_ip: str
    local_port: int
    successful: bool
    response_code: Exception = None


@dataclass
class TimeSchedule:
    start_date: datetime
    interval: int
    game_id: int
    account_id: int
    server_uuid: str
    email: str
    username: str
    password: str
    local_ip: str
    local_port: int
    joined: bool
    proxy_username: str = None
    proxy_password: str = None


@dataclass
class GamesListSchedule(TimeSchedule):
    pass


@dataclass
class LoginTimeSchedule(TimeSchedule):
    pass


@dataclass
class DynamicTimeSchedule(TimeSchedule):
    pass


@dataclass
class TimeTable:
    schedules: List[TimeSchedule]


@dataclass
class Proxy:
    local_ip: str
    local_port: int
    account_id: int = None
    proxy_username: str = None
    proxy_password: str = None
    exit_node_ip: str = None
    exit_node_id: str = None


@dataclass
class GameDetail:
    game_id: int
    account_id: int
    server_uuid: str
    email: str
    username: str
    password: str
    local_ip: str
    local_port: int
    joined: bool
    proxy_username: str = None
    proxy_password: str = None


@dataclass
class ProxyTable:
    proxies: List[Proxy]


