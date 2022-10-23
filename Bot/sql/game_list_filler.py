import logging
from dotenv import load_dotenv
from os import getenv

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from sql.Models import Game, GamesAccount, Scenario


class GameListFiller:
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

    def fill(self, game_list):
        existing_games = self.session.query(Game).all()
        existing_game_ids = [old_game.game_id for old_game in existing_games]
        existing_scenario_ids = [scenario.scenario_id for scenario in self.session.query(Scenario).all()]
        new_games = []
        for game in game_list:
            if game["game_id"] not in existing_game_ids and game["scenario_id"] in existing_scenario_ids:
                new_games.append(game)

        for old_game in existing_games:
            for game in game_list:
                if game["game_id"] == old_game.game_id:
                    old_game.open_slots = game["open_slots"]
                    break
        logging.debug(f"Adding {len(new_games)} to Database")
        self.session.bulk_insert_mappings(Game, new_games)
        self.session.commit()

    def update_single_game(self, data: dict):
        old_game = self.session.query(Game).filter(Game.game_id == data["game_id"]).scalar()
        if old_game:
            old_game.open_slots = data["open_slots"]
        self.session.commit()

    def remove_game_account(self, game_detail):
        self.session.query(GamesAccount).filter(GamesAccount.game_id == game_detail.game_id,
                                                GamesAccount.account_id == game_detail.account_id).delete()
        self.session.commit()
