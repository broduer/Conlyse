import json
import re
import logging
from time import sleep

from sql.game_list_filler import GameListFiller
from webbrowser import Webbrowser
from Networking.exceptions import GameJoinError
from Networking.packet_types import GameDetail


def long_scan(game_detail: GameDetail):
    # Retrieve Login Data

    logging.debug("Starting Webbrowser")
    with Webbrowser(packet=game_detail) as browser:
        try:
            data_requests = browser.run_game()
            with GameListFiller() as glf:
                glf.update_single_game({
                    "game_id": game_detail.game_id,
                    "joined": True,
                })
        except GameJoinError:
            # If Join wasn't possible it should remove the round -> Not possible to join
            with GameListFiller() as glf:
                glf.update_single_game({
                    "game_id": game_detail.game_id,
                    "open_slots": 0,
                })
                glf.remove_game_account(game_detail)
            raise GameJoinError

    error = False

    for data_type in ["1", "2", "3"]:
        if data_type not in data_requests:
            logging.error(f"Data {data_type} couldn't fetch")
            error = True
    if error:
        return data_requests, {}
    auth_data = get_auth_data(data_requests)
    return data_requests, auth_data


def get_auth_data(data_requests):
    return (
        {
            "game_id": data_requests["2"]["body"]["gameID"],
            "version": data_requests["2"]["body"]["version"],
            "hash": data_requests["2"]["body"]["hash"],
            "playerID": data_requests["2"]["body"]["playerID"],
            "siteUserID": data_requests["2"]["body"]["siteUserID"],
            "tstamp": data_requests["2"]["body"]["tstamp"],
            "userAuth": data_requests["2"]["body"]["userAuth"],
        }
    )
