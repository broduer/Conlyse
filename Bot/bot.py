import logging
import pickle
import socket
from apscheduler.schedulers.background import BackgroundScheduler
from time import sleep

from Bot.GameList import GameList
from Bot.account_creator import create_account
from constants import SERVER_UUID, MAXIMUM_ACCOUNTS, COMMUNICATION_IP, COMMUNICATION_PORT, HEADER, FORMAT, \
    RECONNECT_TRIES
from packet_types import ServerRegisterRequest, ServerRegisterAnswer, TimeTable, DynamicTimeSchedule, \
    LoginTimeSchedule, GamesListSchedule, GameTable, GameDetail, AccountRegisterRequest
from game import Game
import logger
import exceptions


class Bot:
    def __init__(self):
        logger.initLogger(logging.DEBUG)
        self.registered = False
        self.server_uuid = SERVER_UUID
        self.client = socket.socket()
        self.connected = False
        self.scheduler = BackgroundScheduler()
        self.scheduler.remove_all_jobs()
        self.games_list = None
        self.games = []
        self.game_table = None
        self.time_table = None

    def run(self):
        self.scheduler.start()
        self.connect_to_server((COMMUNICATION_IP, COMMUNICATION_PORT))
        if self.connected:
            self.register_server()
            self.main_loop()

    def connect_to_server(self, server_addr):
        for i in range(RECONNECT_TRIES):
            try:
                self.client = socket.socket()
                self.client.connect(server_addr)
                self.connected = True
                logging.debug(f"Connected to Manager {server_addr[0]}")
                break
            except socket.error:
                sleep(2)
        else:
            logging.debug(f"Connecting to Manager {server_addr[0]} failed")

    def send_packet(self, packet):
        packet_encoded = pickle.dumps(packet)
        buffer_length = len(packet_encoded)

        buffer_enc_length = str(buffer_length).encode(FORMAT)
        buffer_enc_length += b' ' * (HEADER - len(buffer_enc_length))  # fill up buffer, until it has the expected size

        self.client.send(buffer_enc_length)
        self.client.send(packet_encoded)

    def register_server(self):
        server = ServerRegisterRequest(server_uuid=SERVER_UUID,
                                       maximum_accounts=MAXIMUM_ACCOUNTS)
        self.send_packet(server)

    def main_loop(self):
        while True:
            try:
                buffer_size = self.client.recv(HEADER).decode(FORMAT)
                if not buffer_size:
                    break
            except OSError:
                break

            data = self.client.recv(int(buffer_size))
            if not data:
                break

            packet = pickle.loads(data)

            if isinstance(packet, ServerRegisterAnswer):
                self.handle_register_server_answer(packet)
            elif isinstance(packet, AccountRegisterRequest):
                self.handle_register_account_request(packet)
            elif isinstance(packet, GameTable):
                self.handle_game_table(packet)
            elif isinstance(packet, TimeTable):
                self.handle_time_table(packet)

    def handle_register_server_answer(self, packet: ServerRegisterAnswer):
        if packet.successful:
            logging.debug("Registered successful")
        else:
            raise packet.response_code

    def handle_register_account_request(self, packet: AccountRegisterRequest):
        answer = create_account(packet)
        self.send_packet(answer)

    def handle_game_table(self, packet: GameTable):
        self.game_table = packet
        for game_detail in self.game_table.game_details:
            if not any([game_detail.game_id == game.game_id for game in self.games]):
                self.games.append(Game(game_detail))

    def handle_time_table(self, packet: TimeTable):
        self.time_table = packet

        self.scheduler.remove_all_jobs()
        print(packet)
        for schedule in self.time_table.schedules:
            if isinstance(schedule, GamesListSchedule):
                pass
                # game = Game(GameDetail(6106314, 231, "SAZUGFASJIUGBIORFGISODBQPYIJGIOBASIBASU9",
                #                       "iashdih", "asdgsrds", "rSsUe3NXwzs56Md7", "None", "None", False))
                # game.long_game_scan()
                # game.short_game_scan()
                # self.games_list = GameList(schedule)
                # self.games_list.game_list_run()
                # self.scheduler.add_job(self.games_list.login, "interval", hours=12)
                # self.scheduler.add_job(self.games_list.game_list_scan, "interval", seconds=schedule.interval)
            else:
                schedule: DynamicTimeSchedule | LoginTimeSchedule
                game = self.get_game("game_id", schedule.game_id)
                if isinstance(schedule, DynamicTimeSchedule):
                    self.scheduler.add_job(game.short_game_scan, "interval", seconds=schedule.interval)
                elif isinstance(schedule, LoginTimeSchedule):
                    self.scheduler.add_job(game.long_game_scan, "interval", seconds=schedule.interval)

    def get_game(self, key, data):
        for game in self.games:
            if getattr(game, key) == data:
                return game


if __name__ == "__main__":
    bot = Bot()
    bot.run()
