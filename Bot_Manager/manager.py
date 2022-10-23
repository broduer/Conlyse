import logging
import pickle
import time
from contextlib import closing
from threading import Thread
from operator import attrgetter
import socket
from dotenv import load_dotenv
from os import getenv

import logger
from manager_helper import generate_random_string
from Networking.packet_types import ServerRegisterAnswer, ServerRegisterRequest, TimeTable,\
    AccountRegisterAnswer, BotRegisterRequest, ProxyRegisterRequest, ProxyTable, Proxy
from sql.sql_filler import Filler
from time_planner import TimePlanner
from game_planner import GamePlanner
from account_planner import AccountPlanner
from Networking.exceptions import ServerUUIDinUse

load_dotenv()


class Manager:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOL_SOCKET)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind(("127.0.0.1", int(getenv("COMMUNICATION_PORT"))))
        self.socket.listen()

        self.account_planner = AccountPlanner()
        self.game_planner = GamePlanner()
        self.time_planner = TimePlanner()
        self.sql_filler = Filler()
        self.proxies = {}
        self.clients = {}
        self.sending_account_create_request = False

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        self.account_planner.close()
        self.game_planner.close()
        self.time_planner.close()
        self.sql_filler.close()

    def run(self):
        communication_accept_thread = Thread(target=self.connection_accept_listen)
        communication_accept_thread.start()
        self.main_loop()

    def main_loop(self):
        start_time = time.time()
        i = 1
        while True:
            new_game_allocated, account_creation_needed = self.game_planner.allocate_games_to_accounts()

            # Allocates the games to servers and updates their allocated_games value in self.clients dictionary
            updated_servers = self.game_planner.allocate_games_to_servers(self.get_clients_by("type", "bot"))
            self.update_game_allocation_on_servers(updated_servers)

            if new_game_allocated:
                self.send_plans_to_servers()

            if account_creation_needed:
                self.send_account_register_request()

            self.account_planner.sql_filler.session.commit()
            self.game_planner.sql_filler.session.commit()
            self.time_planner.sql_filler.session.commit()
            self.sql_filler.session.commit()
            time.sleep(abs(start_time + i * int(getenv("MAIN_LOOP_INTERVAL")) - time.time()))
            i = i + 1

    def listen(self, conn):
        while True:
            try:
                buffer_size = conn.recv(int(getenv("HEADER"))).decode(getenv("FORMAT"))
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

            elif isinstance(packet, AccountRegisterAnswer):
                self.register_account(packet)

            elif isinstance(packet, ProxyTable):
                self.register_proxy_table(packet)

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

    def update_game_allocation_on_servers(self, servers):
        if not servers:
            return
        for server in servers.values():
            self.clients[server["client_uuid"]]["allocated_games"] = server["allocated_games"]

    def register_server(self, conn, packet):
        if isinstance(packet, BotRegisterRequest):
            type = "bot"
        elif isinstance(packet, ProxyRegisterRequest):
            type = "proxy_controller"
        else:
            type = "server"
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
                                                   "type": type}

            result = ServerRegisterAnswer(server_uuid=packet.server_uuid,
                                          successful=True)
            self.send_packet(conn, result)

            if type == "bot":
                self.clients[client["client_uuid"]]["maximum_games"] = packet.maximum_games
                self.clients[client["client_uuid"]]["allocated_games"] = 0
                updated_servers = self.game_planner.allocate_games_to_servers(self.get_clients_by("type", "bot"))
                self.update_game_allocation_on_servers(updated_servers)
                self.send_plans_to_servers()

    def register_proxy_table(self, packet: ProxyTable):
        for new_proxy in packet.proxies:
            self.proxies[new_proxy.exit_node_id] = new_proxy

        proxies_account_ids = [proxy.account_id for proxy in self.proxies.values()]

        self.account_planner.allocate_proxies_to_accounts(self.proxies)

    def get_proxy_by(self, datas: dict) -> Proxy | None:
        if len(datas.values()) <= 1:
            data = list(datas.values())[0]
        else:
            data = tuple(datas.values())

        try:
            return next(proxy for proxy in self.proxies.values()
                        if attrgetter(*datas.keys())(proxy) == data)
        except StopIteration:
            return None
        except AttributeError:
            return None

    def send_plans_to_servers(self):
        time_table = self.time_planner.get_time_table(self.get_client_by("type", "bot"), list(self.proxies.values()))
        logging.debug("Sending plans to all servers")
        game_ids = set([schedule.game_id for schedule in time_table.schedules])
        logging.debug(f"Surveillance on {len(game_ids) - 1} games.")
        if len(time_table.schedules) < 1:
            return
        for client_uuid, server_data in self.clients.items():
            if server_data["type"] == "bot":
                server_uuid = server_data["server_uuid"]
                custom_schedules = [schedule for schedule in time_table.schedules
                                    if schedule.server_uuid == server_uuid]

                self.send_packet(server_data["conn"], TimeTable(schedules=custom_schedules))

    def send_account_register_request(self):
        if self.sending_account_create_request:
            logging.debug("Already sending account create request")
            return
        account_register_request = self.account_planner.get_register_account(list(self.get_clients_by("type", "bot")
                                                                                  .values()),
                                                                             self.get_proxy_by({
                                                                                 "account_id": None
                                                                             }))
        if account_register_request:
            self.sending_account_create_request = True
            client = self.get_client_by("server_uuid", account_register_request.server_uuid)
            logging.debug(f"Sending Account Register Request to {client['client_uuid']}")
            self.send_packet(client["conn"], account_register_request)

    def register_account(self, packet: AccountRegisterAnswer):
        if not packet.successful:
            logging.warning(f"Couldn't register new Account {packet.username}")
            return
        logging.debug(f"Registered Account {packet}")
        account_id = self.sql_filler.fill_account(packet)
        proxy = self.get_proxy_by({
            "local_ip": packet.local_ip,
            "local_port": packet.local_port,
        })
        self.proxies[proxy.exit_node_id].account_id = account_id
        self.sending_account_create_request = False

    def disconnect_client(self, key, data):
        client = self.get_client_by(key, data)
        if client:
            logging.debug(f"Lost Connection to {client['type']} client_uuid: {client['client_uuid']}")
            self.clients.pop(client["client_uuid"])
            if client["conn"]:
                client["conn"].close()

    def get_clients_by(self, key, data):
        return {client_uuid: client for client_uuid, client in self.clients.items()
                if client.get(key) == data}

    def get_client_by(self, key, data):
        if key and data:
            for client_uuid, client_data in self.clients.items():
                if client_data.get(key) == data:
                    return client_data
        return None

    def send_to_all_bot(self, packet):
        for client_uuid, client_data in self.clients.items():
            if client_data["type"] == "bot":
                self.send_packet(client_data["conn"], packet)

    def send_packet(self, conn, packet):
        packet_encoded = pickle.dumps(packet)
        buffer_length = len(packet_encoded)

        buffer_enc_length = str(buffer_length).encode(getenv("FORMAT"))
        buffer_enc_length += b' ' * (
                int(getenv("HEADER")) - len(buffer_enc_length))  # fill up buffer, until it has the expected size

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
    with Manager() as manager:
        manager.run()
