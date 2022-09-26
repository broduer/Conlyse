import logging
import random
import string

from Bot_Manager.sql.Models import Account
from constants import ACCOUNT_CREATE_RETRIES
from sql.sql_filler import Filler
from packet_types import AccountRegisterRequest


class AccountPlanner:
    def __init__(self):
        self.sql_filler = Filler()

    def get_register_account(self):
        proxies = self.sql_filler.get_free_proxies()
        accounts = self.sql_filler.get_accounts()
        servers = self.sql_filler.get_servers()
        if len(servers) == 0:
            logging.debug("No Server available to create account!")
            return False
        else:
            server = servers[0]
        if len(proxies) == 0:
            logging.debug(f"No Proxy available to create account!")
            return False
        else:
            proxy = proxies[0]  # Lock to the first proxy
        for _ in ACCOUNT_CREATE_RETRIES:
            registration_data = AccountPlanner.generate_registration_data()
            if not self.account_exists(registration_data["username"],
                                       registration_data["password"],
                                       accounts):
                break
        else:
            return None

        return AccountRegisterRequest(
            server_uuid=server.server_uuid,
            proxy_id=proxy.proxy_id,
            email=registration_data["email"],
            username=registration_data["username"],
            password=registration_data["password"],
            local_ip=proxy.local_ip,
            local_port=proxy.local_port,
        )

    # Checks if username or email is already in use
    @staticmethod
    def account_exists(username, email, accounts: list[Account]):
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
