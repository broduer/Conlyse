import logging

from Networking.exceptions import GameJoinError
from long_scan import long_scan
from short_scan import short_scan
from Networking.packet_types import GameDetail


class Game:
    def __init__(self, game_detail: GameDetail):
        self.login_job = None
        self.dynamic_job = None
        self.states_data = {"tstamps": {}, "stateIDs": {}}
        self.game_id = game_detail.game_id
        self.game_detail = game_detail
        self.data_requests = {}
        self.auth_data = {}

    def short_game_scan(self):
        self.states_data, game_ended = short_scan(self.data_requests, self.auth_data, self.states_data,
                                                  self.game_detail)
        if game_ended:
            logging.debug(f"G: {self.game_id} - Game Ended")
            self.remove_jobs()

    def long_game_scan(self):
        try:
            self.data_requests, self.auth_data = long_scan(self.game_detail)
        except GameJoinError:
            logging.debug(f"G: {self.game_id} - Remove Game Jobs because of GameJoinError ")
            self.remove_jobs()

    def remove_jobs(self):
        if self.login_job:
            self.login_job.remove()
        if self.dynamic_job:
            self.dynamic_job.remove()
