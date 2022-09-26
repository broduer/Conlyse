from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, inspect

from Bot_Manager.packet_types import AccountRegisterAnswer
from Bot_Manager.sql.Models import Account, Game, GamesAccount, Proxy, Server
from Bot_Manager.constants import DB_NAME, DB_IP, DB_USERNAME, DB_PASSWORD
from Bot_Manager import constants as const


class Filler:
    def __init__(self):
        connection_string = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_IP}/{DB_NAME}?charset=utf8mb4"

        engine = create_engine(connection_string, echo=False)
        session_maker = sessionmaker()
        session_maker.configure(bind=engine)
        self.session = session_maker()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.commit()
        self.session.close()

    def get_accounts(self):
        return self.session.query(Account).all()

    def get_free_accounts(self):
        accounts = self.session.query(Account,
                                      func.count(GamesAccount.account_id).label("games_count")) \
            .join(GamesAccount).group_by(Account).all()
        return [accounts for account in accounts if account.games_count < const.MAX_GAMES_PER_ACCOUNT]

    def fill_account(self, account_request: AccountRegisterAnswer):
        self.session.add(Account(email=account_request.email,
                                 username=account_request.username,
                                 password=account_request.password,
                                 proxy_id=account_request.proxy_id,
                                 server_uuid=account_request.server_uuid,)
                         )
        self.session.flush()

    def fill_game_account(self, game_id, account_id):
        self.session.add(GamesAccount(game_id=game_id, account_id=account_id))
        self.session.flush()

    def get_games(self):
        return self.session.query(Game).all()

    def get_rounds_details(self):
        return self.session.query(GamesAccount, Game, Account, Proxy).join(Game).join(Account).join(Proxy).all()

    def get_unassigned_games(self):
        assigned_games = self.session.query(GamesAccount.game_id)
        return self.session.query(Game).filter(~Game.game_id.in_(assigned_games)).all()

    def get_assigned_games(self):
        return self.session.query(Game).join(GamesAccount).join(Account).all()

    def get_free_proxies(self) -> list[Proxy]:
        assigned_proxies = self.session.query(Proxy.proxy_id)
        return self.session.query(Proxy).filter(~Proxy.proxy_id.in_(assigned_proxies)).all()

    def get_free_servers(self):
        return self.session.query(Server).join(Account) \
            .filter(func.count(Account.account_id) < Server.maxmimum_accounts).all()

    def get_servers(self):
        return self.session.query(Server).all()

    def server_exists(self, server_uuid=None):
        if server_uuid:
            return bool(self.session.query(Server).filter(Server.server_uuid == server_uuid).all())

    def fill_server_request(self, server_data):
        self.session.add(Server(server_uuid=server_data.server_uuid,
                                maximum_accounts=server_data.maximum_accounts))
        self.session.flush()


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
