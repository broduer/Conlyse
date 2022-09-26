import logging
from sqlalchemy.orm import sessionmaker

from Bot.sql.Models import Game
from Bot.sql.sql import engine


class GameListFiller:
    def __init__(self):
        session_maker = sessionmaker()
        session_maker.configure(bind=engine)
        self.session = session_maker()

    def fill(self, game_list):
        existing_games = [old_game.game_id for old_game in self.session.query(Game.game_id).all()]
        new_games = []
        print(existing_games)
        for game in game_list:
            if game["game_id"] not in existing_games:
                new_games.append(game)

        self.session.bulk_insert_mappings(Game, new_games)
        self.session.commit()

