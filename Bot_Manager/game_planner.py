import logging
from dataclasses import dataclass

from Bot_Manager.packet_types import GameDetail, GameTable
from Bot_Manager.sql.sql_filler import Filler
from constants import MIN_JOIN_GAME_OPEN_SLOTS, JOIN_SCENARIO_IDS


class GamePlanner:
    def __init__(self):
        self.sql_filler = Filler()

    def allocate_games_to_accounts(self):
        accounts = self.sql_filler.get_free_accounts()
        games = self.sql_filler.get_unassigned_games()
        new_game_allocated = False
        account_creation_needed = False
        # No Free Accounts -> Account needs to be created
        if len(accounts) == 0:
            account_creation_needed = True
        for game in games:
            if (game.open_slots if game.open_slots else 0) > MIN_JOIN_GAME_OPEN_SLOTS and \
                    game.scenario_id in JOIN_SCENARIO_IDS:
                for account in accounts:
                    self.sql_filler.fill_game_account(game.game_id, account.account_id)
                    logging.debug(f"Game {game.game_id} added to account {account.account_id}")
                    new_game_allocated = True
                    break
        if account_creation_needed:
            logging.debug(f"No account/s available for Game/s")
        return new_game_allocated, account_creation_needed

    def get_rounds_details_table(self):
        sql_rounds_details = self.sql_filler.get_rounds_details()
        rounds_details = []
        for round_detail in sql_rounds_details:
            rounds_details.append(GameDetail(
                game_id=round_detail.game_id,
                account_id=round_detail.account_id,
                server_uuid=round_detail.server_uuid,
                email=round_detail.email,
                username=round_detail.username,
                password=round_detail.password,
                local_ip=round_detail.local_ip,
                local_port=round_detail.local_port,
                joined=round_detail.joined,
            ))
        return GameTable(game_details=rounds_details)
