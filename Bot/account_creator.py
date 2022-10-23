import logging

from Networking.packet_types import AccountRegisterRequest, AccountRegisterAnswer
from webbrowser import Webbrowser


def create_account(packet: AccountRegisterRequest):
    with Webbrowser(packet) as web:
        result = web.run_register_account()
    if result:
        logging.debug(f"Created Account {packet.username} successfully")
        return AccountRegisterAnswer(server_uuid=packet.server_uuid,
                                     email=packet.email,
                                     username=packet.username,
                                     password=packet.password,
                                     local_ip=packet.local_ip,
                                     local_port=packet.local_port,
                                     successful=True)
    else:
        return AccountRegisterAnswer(server_uuid=packet.server_uuid,
                                     email=packet.email,
                                     username=packet.username,
                                     password=packet.password,
                                     local_ip=packet.local_ip,
                                     local_port=packet.local_port,
                                     successful=False)
