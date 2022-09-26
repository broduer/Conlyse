import logging

from Bot.packet_types import AccountRegisterRequest, AccountRegisterAnswer
from Bot.webbrowser import Webbrowser


def create_account(packet: AccountRegisterRequest):
    webbrowser = Webbrowser(packet)
    result = webbrowser.run_register_account()
    if result:
        logging.debug(f"Created Account {packet.username} successfully")
        return AccountRegisterAnswer(server_uuid=packet.server_uuid,
                                     proxy_id=packet.proxy_id,
                                     email=packet.email,
                                     username=packet.username,
                                     password=packet.password,
                                     local_ip=packet.local_ip,
                                     local_port=packet.local_port,
                                     successful=True)
    else:
        return AccountRegisterAnswer(server_uuid=packet.server_uuid,
                                     proxy_id=packet.proxy_id,
                                     email=packet.email,
                                     username=packet.username,
                                     password=packet.password,
                                     local_ip=packet.local_ip,
                                     local_port=packet.local_port,
                                     successful=False)
