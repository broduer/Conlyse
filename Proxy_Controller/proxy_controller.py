import json
import logging
import pickle
import socket
from threading import Thread
from time import sleep, time
from dotenv import load_dotenv
from os import getenv

import logger
from Networking.packet_types import ProxyRegisterRequest, ServerRegisterAnswer, Proxy, ProxyTable
import requests

load_dotenv()

logging.getLogger("requests").setLevel(logging.WARNING)


class ProxyController:
    def __init__(self):
        logger.initLogger(logging.DEBUG)
        self.registered = False
        self.server_uuid = getenv("SERVER_UUID")
        self.client = socket.socket()
        self.connected = False
        self.own_ip = socket.gethostbyname(socket.gethostname())
        self.proxies = {}

    def run(self):
        self.connect_to_server((getenv("COMMUNICATION_IP"), int(getenv("COMMUNICATION_PORT"))))
        communication_thread = Thread(target=self.listen)
        communication_thread.start()
        if self.connected:
            self.register_proxy_controller()
            self.main_loop()

    def connect_to_server(self, server_addr):
        for i in range(int(getenv("RECONNECT_TRIES"))):
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

    def get_proxies(self):
        response = requests.get(
            "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=100",
            headers={"Authorization": f"Token {getenv('WEBSHARE_API_KEY')}"}
        )
        if response.status_code != 200:
            return
        data = json.loads(response.text)
        for new_proxy in data["results"]:
            self.proxies[new_proxy["id"]] = Proxy(local_ip=new_proxy["proxy_address"],
                                                  local_port=new_proxy["port"],
                                                  proxy_username=new_proxy["username"],
                                                  proxy_password=new_proxy["password"],
                                                  exit_node_ip=new_proxy["proxy_address"],
                                                  exit_node_id=new_proxy["id"])

    def main_loop(self):
        start_time = time()
        i = 1
        while True:
            self.send_proxies()
            sleep(start_time + i * int(getenv("MAIN_LOOP_INTERVAL")) - time())
            i = i + 1

    def listen(self):
        while True:
            try:
                buffer_size = self.client.recv(int(getenv("HEADER"))).decode(getenv("FORMAT"))
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

    def send_proxies(self):
        self.get_proxies()
        packet = ProxyTable(proxies=list(self.proxies.values()))
        logging.debug("Sending Proxies")
        self.send_packet(packet)

    def send_packet(self, packet):
        packet_encoded = pickle.dumps(packet)
        buffer_length = len(packet_encoded)

        buffer_enc_length = str(buffer_length).encode(getenv("FORMAT"))
        buffer_enc_length += b' ' * (
                int(getenv("HEADER")) - len(buffer_enc_length))  # fill up buffer, until it has the expected size

        self.client.send(buffer_enc_length)
        self.client.send(packet_encoded)

    def register_proxy_controller(self):
        packet = ProxyRegisterRequest(getenv("SERVER_UUID"))
        self.send_packet(packet)

    def handle_register_server_answer(self, packet: ServerRegisterAnswer):
        if packet.successful:
            logging.debug("Registered successful")
        else:
            raise packet.response_code

    def get_proxy_by(self, key, data):
        try:
            return next(proxy for _, proxy in self.proxies.items()
                        if getattr(proxy, key) == data)
        except StopIteration:
            return None


if __name__ == "__main__":
    proxy_controller = ProxyController()
    proxy_controller.run()
