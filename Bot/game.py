from threading import Thread

from long_scan import long_scan
from short_scan import short_scan
from time import sleep
from packet_types import GameDetail


class Game:
    def __init__(self, game_detail: GameDetail):
        self.states_data = {"tstamps": {}, "stateIDs": {}}
        self.game_id = game_detail.game_id
        self.game_detail = game_detail
        self.data_requests = {}
        self.auth_data = {}

    def short_game_scan(self):
        self.states_data = short_scan(self.data_requests, self.auth_data, self.states_data)

    def long_game_scan(self):
        self.data_requests, self.auth_data = long_scan(self.game_detail)
