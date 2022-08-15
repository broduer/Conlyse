def sort_players(data_2):
    data_players = data_2["result"]["states"]["1"]["players"]
    players = dict({})
    for player in data_players:
        player = data_players[player]
        if "siteUserID" in player:
            if int(player["playerID"]) > 0:
                players[int(player["playerID"])] = dict({
                    "player_id": int(player["playerID"]),
                    "site_user_id": int(player["siteUserID"]),
                    "name": player["name"],
                })
    return players