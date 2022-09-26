import re
import logging

from Bot.webbrowser import Webbrowser


def long_scan(game_detail):
    # Retrieve Login Data

    logging.debug("Starting Webbrowser")
    with Webbrowser(packet=game_detail) as browser:
        data_requests = browser.run_game()
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
            "authTstamp": re.findall("(?<=authTstamp=)[0-9]{10}", data_requests["3"]["body"])[0],
            "userAuth": data_requests["2"]["body"]["userAuth"],
        }
    )
