import json
from datetime import datetime

from helper import get_normal_timestamp


def sort_trades(game_id, data_2):
    timestamp = data_2["result"]["states"]["4"]["timeStamp"]
    data_2_trades = data_2["result"]["states"]["4"]["asks"][1] + data_2["result"]["states"]["4"]["bids"][1]
    trades = {}
    for resource in data_2_trades:
        for group in resource:
            if group == "ultshared.UltAskList" or group == "ultshared.UltBidList":
                continue
            for trade in group:
                if trade["playerID"] == 0:
                    continue
                trades[trade["orderID"]] = dict({
                    "order_id": int(trade["orderID"]),
                    "owner_id": int(trade["playerID"]),
                    "amount": int(trade["amount"]),
                    "resource_type": int(trade["resourceType"]),
                    "limit": float(trade["limit"]),
                    "buy": bool(trade["buy"]),
                    "game_id": int(game_id),
                    "valid_from": datetime.fromtimestamp(get_normal_timestamp(timestamp)),
                })
    return trades