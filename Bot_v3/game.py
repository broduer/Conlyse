import threading

from long_scan import long_scan
from short_scan import short_scan
from time import sleep


class Game:
    def __init__(self, login_data, interval):
        self.interval = interval
        self.states_data = {"tstamps": {}, "stateIDs": {}}
        self.login_data = login_data
        self.data_requests = {}
        self.auth_data = {}

    def setup(self):
        short_game = threading.Thread(target=self.short_game_loop)
        short_game.start()

    def short_game_loop(self):
        while True:
            self.short_game_scan()
            sleep(self.interval)

    def short_game_scan(self):
        self.states_data = short_scan(self.data_requests, self.auth_data, self.states_data)

    def long_game_scan(self):
        self.data_requests, self.auth_data = long_scan(self.login_data)
