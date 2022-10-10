from datetime import datetime, timedelta
from typing import List

from dotenv import load_dotenv
from os import getenv

from Networking.packet_types import DynamicTimeSchedule, LoginTimeSchedule, GamesListSchedule, TimeTable, Proxy
from sql.sql_filler import Filler

load_dotenv()


class TimePlanner:
    def __init__(self):
        self.sql_filler = Filler()

    def close(self):
        self.sql_filler.close()

    def get_time_table(self, server, proxies: List[Proxy]):
        games = self.sql_filler.get_assigned_games()
        accounts = self.sql_filler.get_accounts()
        accounts_dict = {account.account_id: account for account in accounts}
        proxies_dict = {proxy.account_id: proxy for proxy in proxies}

        # Calculate the offset of every game
        count_games = len(games)
        if count_games > 0:
            every_dynamic_data_report = int(getenv("DYNAMIC_DATA_REPORT_INTERVAL")) / count_games  # in seconds
            every_login_data_report = int(getenv("LOGIN_DATA_REPORT_INTERVAL")) / count_games  # in hours

        date_now = datetime.now()
        schedules = []
        for number, game in enumerate(games):
            try:
                if not game.server_uuid:
                    return
            except AttributeError:
                continue
            try:
                proxy = proxies_dict[game.account_id]
                account = accounts_dict[game.account_id]
            except KeyError:
                continue
            dynamic_schedule = DynamicTimeSchedule(
                game_id=game.game_id,
                server_uuid=game.server_uuid,
                start_date=date_now + timedelta(seconds=every_dynamic_data_report * number),
                interval=int(getenv("DYNAMIC_DATA_REPORT_INTERVAL")),
                account_id=account.account_id,
                email=account.email,
                username=account.username,
                password=account.password,
                joined=game.joined,
                local_ip=proxy.local_ip,
                local_port=proxy.local_port,
                proxy_username=proxy.proxy_username,
                proxy_password=proxy.proxy_password,
            )
            login_schedule = LoginTimeSchedule(
                game_id=game.game_id,
                server_uuid=game.server_uuid,
                start_date=date_now + timedelta(seconds=every_login_data_report * number),
                interval=int(getenv("LOGIN_DATA_REPORT_INTERVAL")),
                account_id=account.account_id,
                email=account.email,
                username=account.username,
                password=account.password,
                joined=game.joined,
                local_ip=proxy.local_ip,
                local_port=proxy.local_port,
                proxy_username=proxy.proxy_username,
                proxy_password=proxy.proxy_password,
            )
            schedules.append(dynamic_schedule)
            schedules.append(login_schedule)
        if server and len(proxies) > 0:
            proxy = proxies[0]
            # Schedule for updates on new added games to conflict of nations server
            games_list_schedule = GamesListSchedule(server_uuid=server["server_uuid"],
                                                    start_date=date_now,
                                                    interval=int(getenv("GAMES_LIST_DATA_REPORT_INTERVAL")),
                                                    account_id=-123,
                                                    email="salkjfiaj",
                                                    game_id=-123,
                                                    joined=False,
                                                    username=getenv("MANAGER_USERNAME"),
                                                    password=getenv("MANAGER_PASSWORD"),
                                                    local_ip=proxy.local_ip,
                                                    local_port=proxy.local_port,
                                                    proxy_username=proxy.proxy_username,
                                                    proxy_password=proxy.proxy_password)
            schedules.append(games_list_schedule)
        time_table = TimeTable(schedules=schedules)
        return time_table
