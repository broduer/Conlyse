import logging
import random
import string
from dotenv import load_dotenv
from os import getenv
from typing import List

from Bot_Manager.sql.Models import Account
from sql.sql_filler import Filler
from Networking.packet_types import AccountRegisterRequest, Proxy

load_dotenv()


class AccountPlanner:
    def __init__(self):
        self.sql_filler = Filler()

    def close(self):
        self.sql_filler.close()

    def get_register_account(self, servers, proxy):
        accounts = self.sql_filler.get_accounts()
        if len(servers) == 0:
            logging.debug("No Server available to create account!")
            return False
        else:
            server = servers[0]
        if not proxy:
            logging.debug(f"No Proxy available to create account!")
            return False
        for _ in range(int(getenv("ACCOUNT_CREATE_RETRIES"))):
            registration_data = AccountPlanner.generate_registration_data()
            if not self.account_exists(registration_data["username"],
                                       registration_data["password"],
                                       accounts):
                break
        else:
            return None

        return AccountRegisterRequest(
            server_uuid=server["server_uuid"],
            email=registration_data["email"],
            username=registration_data["username"],
            password=registration_data["password"],
            local_ip=proxy.local_ip,
            local_port=proxy.local_port,
            proxy_username=proxy.proxy_username,
            proxy_password=proxy.proxy_password,
        )

    def allocate_proxies_to_accounts(self, proxies):
        accounts = self.sql_filler.get_accounts()
        assigned_accounts = [proxy.account_id for proxy in proxies.values()
                             if proxy.account_id is not None]

        for proxy in proxies.values():
            if proxy.account_id in assigned_accounts:
                continue
            if len(accounts) == 0:
                break
            proxies[proxy.exit_node_id].account_id = accounts.pop(0).account_id
        print(proxies)
        return proxies

    # Checks if username or email is already in use
    @staticmethod
    def account_exists(username, email, accounts: List[Account]):
        return any(account.username == username or account.email == email for account in accounts)

    @staticmethod
    def generate_random_string(length, special=False, email=False):
        characters = list(f'{string.ascii_letters}{string.digits}{"!@#$%^&*()" if special else ""}')
        random.shuffle(characters)
        password = []
        for i in range(length):
            password.append(random.choice(characters))

        random.shuffle(password)
        return f'{"".join(password)}{"@gmail.com" if email else ""}'

    @staticmethod
    def generate_registration_data():
        return {
            "username": AccountPlanner.generate_random_string(random.randint(13, 16), special=False, email=False),
            "password": AccountPlanner.generate_random_string(random.randint(13, 20), special=True, email=False),
            "email": AccountPlanner.generate_random_string(random.randint(16, 20), special=False, email=True),
        }
