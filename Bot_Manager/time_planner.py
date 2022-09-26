from datetime import datetime, timedelta

import constants as const
from constants import MANAGER_USERNAME, MANAGER_PASSWORD
from packet_types import DynamicTimeSchedule, LoginTimeSchedule, GamesListSchedule, TimeTable
from sql.sql_filler import Filler


class TimePlanner:
    def __init__(self):
        self.sql_filler = Filler()

    def get_time_table(self, server):
        games = self.sql_filler.get_assigned_games()
        count_games = len(games)
        if count_games > 0:
            every_dynamic_data_report = const.DYNAMIC_DATA_REPORT_INTERVAL / count_games  # in seconds
            every_login_data_report = const.LOGIN_DATA_REPORT_INTERVAL / count_games  # in hours

        date_now = datetime.now()
        schedules = []
        for number, game in enumerate(games):
            dynamic_schedule = DynamicTimeSchedule(
                game_id=game.game_id,
                server_uuid=game.server_uuid,
                start_date=date_now + timedelta(seconds=every_dynamic_data_report * number),
                interval=const.DYNAMIC_DATA_REPORT_INTERVAL)
            login_schedule = LoginTimeSchedule(
                game_id=game.game_id,
                server_uuid=game.server_uuid,
                start_date=date_now + timedelta(seconds=every_login_data_report * number),
                interval=const.LOGIN_DATA_REPORT_INTERVAL)
            schedules.append(dynamic_schedule)
            schedules.append(login_schedule)

        if server:
            # Schedule for updates on new added games to conflict of nations server
            games_list_schedule = GamesListSchedule(server_uuid=server["server_uuid"],
                                                    start_date=date_now,
                                                    interval=const.GAMES_LIST_DATA_REPORT_INTERVAL,
                                                    username=MANAGER_USERNAME,
                                                    password=MANAGER_PASSWORD)
            schedules.append(games_list_schedule)
        time_table = TimeTable(schedules=schedules)
        return time_table
