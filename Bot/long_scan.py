import re
import logging

from Bot.webbrowser import Webbrowser


def long_scan(login_data):
    # Retrieve Login Data

    logging.debug("Starting Webbrowser")
    with Webbrowser(login_data=login_data) as browser:
        data_requests = browser.run()
    auth_data = get_auth_data(data_requests)

    return data_requests, auth_data


def get_auth_data(data_requests):
    print(data_requests["2"]["body"])
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
