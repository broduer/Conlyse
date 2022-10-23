from datetime import datetime, timedelta

from sql.game_list_filler import GameListFiller
from webbrowser import Webbrowser
from Networking.packet_types import GamesListSchedule


class GameList:
    def __init__(self, games_list_schedule: GamesListSchedule):
        self.games_list_schedule = games_list_schedule
        self.game_list_filler = GameListFiller()

    def game_list_run(self):
        with Webbrowser(packet=self.games_list_schedule) as web:
            game_list_raw = web.run_game_list()
        game_list = self.sort_game_list(game_list_raw)
        self.game_list_filler.fill(game_list)

    @staticmethod
    def sort_game_list(game_list_raw):
        games = []
        for game_raw in game_list_raw:
            game_raw = game_raw["properties"]
            time_scale = 4 if "(4X SPEED)" in game_raw["title"] else 1
            start_time = datetime.now() - timedelta(days=int(game_raw["dayofgame"]) / time_scale)
            current_time = start_time + timedelta(days=int(game_raw["dayofgame"]) * time_scale)
            if int(game_raw["gameID"]) not in [game["game_id"] for game in games]:
                games.append({
                    "game_id": int(game_raw["gameID"]),
                    "scenario_id": int(game_raw["scenarioID"]),
                    "start_time": start_time,
                    "current_time": current_time,
                    "open_slots": int(game_raw["openSlots"])
                })
        return games
