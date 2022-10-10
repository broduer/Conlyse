from typing import List

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, inspect, desc
from dotenv import load_dotenv
from os import getenv

from Networking.packet_types import AccountRegisterAnswer
from Bot_Manager.sql.Models import Account, Game, GamesAccount, Scenario

load_dotenv()


class Filler:
    def __init__(self):
        connection_string = f"mysql+mysqlconnector://{getenv('DB_USERNAME')}:{getenv('DB_PASSWORD')}@{getenv('DB_IP')}/{getenv('DB_NAME')}?charset=utf8mb4"

        engine = create_engine(connection_string, echo=False)
        session_maker = sessionmaker()
        session_maker.configure(bind=engine)
        self.session = session_maker()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.commit()
        self.session.close()

    def close(self):
        self.session.commit()
        self.session.close()

    def get_accounts(self) -> List[Account]:
        return self.session.query(Account).all()

    def get_free_accounts(self):
        accounts = self.session.query(Account.account_id, Account,
                                      func.count(GamesAccount.account_id).label("games_count")) \
            .join(GamesAccount, isouter=True).group_by(Account).all()
        return [account for account in accounts if account.games_count < int(getenv("MAX_GAMES_PER_ACCOUNT"))]

    def fill_account(self, account_request: AccountRegisterAnswer):
        account = Account(email=account_request.email,
                          username=account_request.username,
                          password=account_request.password)
        self.session.add(account)
        self.session.flush()
        return account.account_id

    def fill_game_account(self, game_id, account_id):
        self.session.add(GamesAccount(game_id=game_id, account_id=account_id))
        self.session.flush()

    def get_game_accounts(self):
        return self.session.query(GamesAccount).all()

    def get_games(self):
        return self.session.query(Game).all()

    def get_rounds_details(self):
        return self.session.query(GamesAccount, Game, Account).join(Game).join(Account).all()

    def get_unassigned_games(self) -> List[Game]:
        assigned_games = self.session.query(GamesAccount.game_id)
        unassigned_games = self.session.query(
            Game.game_id, Game.start_time, Game.current_time, Game.end_time, Game.next_day_time, Game.next_heal_time,
            Game.open_slots, Scenario.scenario_id, Scenario.name, Scenario.map_id, Scenario.speed
        ).join(Scenario).filter(~Game.game_id.in_(assigned_games)).order_by(desc(Game.start_time)).all()
        return unassigned_games

    def get_assigned_games(self):
        return self.session.query(GamesAccount.game_id, GamesAccount.account_id, GamesAccount.server_uuid,
                                  GamesAccount.joined, Game.start_time, Game.end_time, Game.current_time,
                                  Game.open_slots, Game.scenario_id, Game.next_heal_time, Game.next_heal_time
                                  ).join(GamesAccount).all()


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
