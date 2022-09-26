import logging
import pickle
import time
from datetime import datetime
from threading import Thread

from Bot_Manager import logger
from Bot_Manager.manager_helper import generate_random_string
from packet_types import ServerRegisterAnswer, ServerRegisterRequest, TimeTable, GameTable, GamesListSchedule, \
    AccountRegisterAnswer
from constants import COMMUNICATION_PORT, MAIN_LOOP_INTERVAL, FORMAT, HEADER
from Bot_Manager.sql.sql_filler import Filler
from time_planner import TimePlanner
from game_planner import GamePlanner
from account_planner import AccountPlanner
from exceptions import ServerUUIDinUse
import socket


class Manager:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOL_SOCKET)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind(("127.0.0.1", COMMUNICATION_PORT))
        self.socket.listen()

        self.account_planner = AccountPlanner()
        self.game_planner = GamePlanner()
        self.time_planner = TimePlanner()
        self.sql_filler = Filler()
        self.clients = {}

    def run(self):
        communication_accept_thread = Thread(target=self.connection_accept_listen)
        communication_accept_thread.start()
        self.main_loop()

    def main_loop(self):
        start_time = time.time()
        i = 1
        while True:
            new_game_allocated, account_creation_needed = self.game_planner.allocate_games_to_accounts()

            if new_game_allocated:
                self.send_plans_to_servers()

            if account_creation_needed:
                self.send_account_register_request()

            time.sleep(start_time + i * MAIN_LOOP_INTERVAL - time.time())
            i = i + 1

    def listen(self, conn):
        while True:
            try:
                buffer_size = conn.recv(HEADER).decode(FORMAT)
                if not buffer_size:
                    self.disconnect_client("conn", conn)
                    break
            except OSError:
                self.disconnect_client("conn", conn)
                break

            data = conn.recv(int(buffer_size))
            if not data:
                break

            packet = pickle.loads(data)

            print(packet)

            if isinstance(packet, ServerRegisterRequest):
                self.register_server(conn, packet)

            if isinstance(packet, AccountRegisterAnswer):
                self.register_account(packet)

    def register_client(self, conn, addr):
        for i in range(10):
            random_uuid = generate_random_string(40)
            if random_uuid not in self.clients:
                self.clients[random_uuid] = {
                    "client_uuid": random_uuid,
                    "type": "client",
                    "ip": addr[0],
                    "port": addr[1],
                    "conn": conn,
                }
                break
        else:
            logging.warning(f"Couldn't register Client {addr[0]}")

    def register_server(self, conn, packet):
        if not self.sql_filler.server_exists(packet.server_uuid):
            self.sql_filler.fill_server_request(packet)
            logging.debug(f"Filled new Server {packet.server_uuid}")
        if self.get_client_by("server_uuid", packet.server_uuid):
            logging.warning(f"{packet.server_uuid} already in use.")
            result = ServerRegisterAnswer(server_uuid=packet.server_uuid,
                                          response_code=ServerUUIDinUse(f"{packet.server_uuid} already in use."),
                                          successful=False)
            self.send_packet(conn, result)
        else:
            logging.debug(f"Server {packet.server_uuid} registered.")
            client = self.get_client_by("conn", conn)
            self.clients[client["client_uuid"]] = {**client,
                                                   "server_uuid": packet.server_uuid,
                                                   "type": "server"}
            result = ServerRegisterAnswer(server_uuid=packet.server_uuid,
                                          successful=True)
            self.send_packet(conn, result)

            self.send_plans_to_servers()

    def send_plans_to_servers(self):
        time_table = self.time_planner.get_time_table(self.get_client_by("type", "server"))
        game_table = self.game_planner.get_rounds_details_table()
        logging.debug("Sending plans to all servers")
        logging.debug(f"Surveillance on {len(time_table.schedules) - 1} games.")
        game_list_schedule = next(schedule for schedule in time_table.schedules
                                  if isinstance(schedule, GamesListSchedule))
        for client_uuid, server_data in self.clients.items():
            if server_data["type"] == "server":
                server_uuid = server_data["server_uuid"]
                custom_schedules = [schedule for schedule in time_table.schedules
                                    if schedule.server_uuid == server_uuid]

                custom_game_details = [game_detail for game_detail in game_table.game_details
                                       if game_detail.server_uuid == server_uuid]

                if game_list_schedule.server_uuid == server_uuid:
                    custom_schedules.append(game_list_schedule)

                self.send_packet(server_data["conn"], GameTable(game_details=custom_game_details))
                self.send_packet(server_data["conn"], TimeTable(schedules=custom_schedules))

    def send_account_register_request(self):
        account_register_request = self.account_planner.get_register_account()
        if account_register_request:
            client = self.get_client_by("server_uuid", account_register_request.server_uuid)
            logging.debug(f"Sending Account Register Request to {client['client_uuid']}")
            self.send_packet(client["conn"], account_register_request)

    def register_account(self, packet: AccountRegisterAnswer):
        if not packet.successful:
            logging.warning(f"Couldn't register new Account {packet.username}")
            return
        logging.debug(f"Registered Account {packet}")
        self.sql_filler.fill_account(packet)

    def disconnect_client(self, key, data):
        client = self.get_client_by(key, data)
        if client:
            logging.debug(f"Lost Connection to {client['type']} client_uuid: {client['client_uuid']}")
            self.clients.pop(client["client_uuid"])
            if client["conn"]:
                client["conn"].close()

    def get_client_by(self, key, data):
        if key and data:
            for client_uuid, client_data in self.clients.items():
                if client_data.get(key) == data:
                    return client_data
        return None

    def send_to_all_server(self, packet):
        for client_uuid, client_data in self.clients.items():
            if client_data["type"] == "server":
                self.send_packet(client_data["conn"], packet)

    def send_packet(self, conn, packet):
        packet_encoded = pickle.dumps(packet)
        buffer_length = len(packet_encoded)

        buffer_enc_length = str(buffer_length).encode(FORMAT)
        buffer_enc_length += b' ' * (HEADER - len(buffer_enc_length))  # fill up buffer, until it has the expected size

        try:
            conn.send(buffer_enc_length)
            conn.send(packet_encoded)
        except BrokenPipeError:
            self.disconnect_client("conn", conn)

    def connection_accept_listen(self):
        while True:
            conn, addr = self.socket.accept()
            logging.debug(f"Client Connected with {addr}")
            self.register_client(conn, addr)

            listen_thread = Thread(target=self.listen, args=(conn,))
            listen_thread.start()


if "__main__" == __name__:
    logger.initLogger(logging.DEBUG)
    manager = Manager()
    manager.run()
