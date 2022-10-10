import logging
from datetime import datetime
from typing import Dict

from dotenv import load_dotenv
from os import getenv

from Bot_Manager.sql.sql_filler import Filler

load_dotenv()


class GamePlanner:
    def __init__(self):
        self.sql_filler = Filler()

    def close(self):
        self.sql_filler.close()

    def allocate_games_to_accounts(self):
        accounts = self.sql_filler.get_free_accounts()
        games = self.sql_filler.get_unassigned_games()
        join_scenario_ids = [int(scenario_id) for scenario_id in getenv("JOIN_SCENARIO_IDS").split(",")]
        new_game_allocated = False
        account_creation_needed = False
        # No Free Accounts -> Account needs to be created
        if len(accounts) == 0:
            account_creation_needed = True
        account_games = {account.account_id: account.games_count for account in accounts}
        games_count_total = sum(account_games.values())
        for game in games:
            time_diff = (datetime.now() - game.start_time) / game.speed
            if games_count_total < int(getenv("MAX_GAMES_TOTAL")) and \
                    (game.open_slots if game.open_slots else 0) > int(getenv("MIN_JOIN_GAME_OPEN_SLOTS")) and \
                    game.scenario_id in join_scenario_ids and \
                    time_diff.total_seconds() < int(getenv("MAX_HOURS_OLD_GAME")) * 3600:
                for account in accounts:
                    if account_games[account.account_id] < int(getenv("MAX_GAMES_PER_ACCOUNT")):
                        self.sql_filler.fill_game_account(game.game_id, account.account_id)
                        logging.debug(f"Game {game.game_id} added to account {account.account_id}")
                        new_game_allocated = True
                        account_games[account.account_id] += 1
                        games_count_total += 1
                        break
        if account_creation_needed:
            logging.debug(f"No account/s available for Game/s")
        return new_game_allocated, account_creation_needed

    def allocate_games_to_servers(self, servers):
        game_accounts = self.sql_filler.get_game_accounts()
        servers_list = list(servers.values())
        server_uuids = list(servers)
        if len(servers_list) == 0:
            return []
        for game_account in game_accounts:
            if game_account.server_uuid in server_uuids:
                # Game is assigned to active Server
                continue
            servers_list.sort(key=self.sort_function)
            selected_server = servers_list[0]
            game_account.server_uuid = selected_server["server_uuid"]
            servers[selected_server["client_uuid"]]["allocated_games"] += 1
        self.sql_filler.session.flush()
        self.sql_filler.session.commit()
        return servers

    @staticmethod
    def sort_function(server):
        return server["maximum_games"] - server["allocated_games"]
