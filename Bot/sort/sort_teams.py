def sort_teams(game_id, data_2):
    data_teams = data_2["result"]["states"]["1"]["teams"]
    teams = dict({})
    for team in data_teams:
        team = data_teams[team]
        if "java.util.HashMap" in team:
            continue
        teams[int(team["teamID"])] = dict({
            "team_id": int(team["teamID"]),
            "leader_id": int(team["leaderID"]),
            "name": team["name"],
            "deleted": bool(team["disbanded"]),
            "game_id": int(game_id)
        })
    return teams