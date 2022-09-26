import datetime
import time

import requests
import json
import logging
from charset_normalizer.api import logger

from Bot.constants import SHORT_SCAN_SORTED_DATA_SAVE
from Bot.sort.helper import DateTimeEncoder
from Bot.sort.sort import sort
from Bot.sql.sql_filler import Filler

logger.setLevel(logging.ERROR)


def short_scan(data_requests, auth_data, states_data):
    # Exiting if no long_scan is made
    if not data_requests or not auth_data:
        return states_data

    # Combining Data from long_scan and old short_scan
    bot_data = {**auth_data, **states_data}
    stateIDs = {"@c": "java.util.HashMap", **bot_data["stateIDs"]} if "stateIDs" in bot_data else {
        "@c": "java.util.HashMap"}
    tstamps = {"@c": "java.util.HashMap", **bot_data["tstamps"]} if "tstamps" in bot_data else {
        "@c": "java.util.HashMap"}

    # Making the actual request
    data2_data = f'{{"requestID":1,"@c":"ultshared.action.UltUpdateGameStateAction","stateType":0,"stateID":"0","addStateIDsOnSent":true,"option":null,"actions":null,"lastCallDuration":0,"version":{bot_data["version"]},"tstamps": {json.dumps(tstamps)}, "stateIDs": {json.dumps(stateIDs)}, "tstamp":"{bot_data["tstamp"]}","client":"con-client","hash":"{bot_data["hash"]}","sessionTstamp":0,"gameID":"{bot_data["game_id"]}","playerID":{bot_data["playerID"]},"siteUserID":"{bot_data["siteUserID"]}","adminLevel":null,"rights":"chat","userAuth":"{bot_data["userAuth"]}"}}'
    response = requests.post(data_requests["2"]["url"], data=data2_data)
    if response.status_code != 200:
        return states_data
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError:
        logging.exception("Couldn't load short_scan data")
        return states_data
    else:
        logging.debug(f"Loaded short_scan data successfully. Took {round(response.elapsed.microseconds / 1000)} ms.")

    # If the request didn't fail sort the data
    sorted_data = sort(bot_data["game_id"], data, data_requests)

    if SHORT_SCAN_SORTED_DATA_SAVE:
        with open(f"{time.time()}.json", "w") as f:
            f.write(json.dumps(sorted_data, indent=2, cls=DateTimeEncoder))

    with Filler(game_id=bot_data["game_id"], data=sorted_data) as filler:
        filler.fill()

    return getStates(data, states_data)


def getStates(data, states_data):
    stateIDs = {}
    tstamps = {}
    for state in data["result"]["states"]:
        if data["result"]["states"][state] == "java.util.HashMap":
            continue
        stateIDs[state] = data["result"]["states"][state]["stateID"]
        tstamps[state] = data["result"]["states"][state]["timeStamp"]

    return {"stateIDs": {**states_data["stateIDs"], **stateIDs}, "tstamps": {**states_data["tstamps"], **tstamps}}
