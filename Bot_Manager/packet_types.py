from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class ServerRegisterRequest:
    server_uuid: str
    maximum_accounts: int


@dataclass
class ServerRegisterAnswer:
    server_uuid: str
    successful: bool
    response_code: Exception = None


@dataclass
class AccountRegisterRequest:
    server_uuid: str
    proxy_id: int
    email: str
    username: str
    password: str
    local_ip: str
    local_port: int


@dataclass
class AccountRegisterAnswer:
    server_uuid: str
    proxy_id: int
    email: str
    username: str
    password: str
    local_ip: str
    local_port: int
    successful: bool
    response_code: Exception = None


@dataclass
class TimeSchedule:
    server_uuid: str
    start_date: datetime
    interval: int


@dataclass
class GamesListSchedule(TimeSchedule):
    username: str
    password: str


@dataclass
class LoginTimeSchedule(TimeSchedule):
    game_id: int = None


@dataclass
class DynamicTimeSchedule(TimeSchedule):
    game_id: int = None


@dataclass
class TimeTable:
    schedules: List[TimeSchedule]


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


@dataclass
class GameTable:
    game_details: List[GameDetail]
