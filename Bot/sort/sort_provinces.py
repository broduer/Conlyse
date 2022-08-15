from datetime import datetime

from Bot.sort.helper import get_province_from_id, get_normal_timestamp


def sort_provinces(game_id, data_1, data_2, data_2_old):
    timestamp = data_2["result"]["states"]["3"]["timeStamp"]
    data_1_locations = data_1["locations"][1]
    data_2_locations = data_2["result"]["states"]["3"]["map"]["locations"][1]
    provinces = dict({})
    for province_2 in data_2_locations:
        province_1 = get_province_from_id(province_2["id"], data_1_locations)
        if province_2["@c"] == "p":
            if "sa" not in province_2:
                stationary_army_id = 0
            else:
                stationary_army_id = int(province_2["sa"])
            if "rp" not in province_2:
                resource_production = 0
            else:
                resource_production = int(province_2["rp"])
            if "m" not in province_2:
                morale = 0
            else:
                morale = int(province_2["m"])
            provinces[province_1["id"]] = dict({
                "province_location_id": int(province_1["id"]),
                "owner_id": int(province_2["o"]),
                "morale": int(morale),
                "province_state_id": int(province_2["pst"]),
                "stationary_army_id": stationary_army_id,
                "victory_points": int(province_2["plv"]),
                "resource_production": int(resource_production),
                "tax_production": int(province_2["tp"]),
                "game_id": int(game_id),
                "valid_from": datetime.fromtimestamp(get_normal_timestamp(timestamp)),
            })
    return provinces


def sort_buildings(game_id, data_2):
    timestamp = data_2["result"]["states"]["3"]["timeStamp"]
    data_2_locations = data_2["result"]["states"]["3"]["map"]["locations"][1]
    buildings = []
    for province_2 in data_2_locations:
        if province_2["@c"] == "p":
            for upgrade in province_2["us"][1]:
                buildings.append({
                    "province_location_id": int(province_2["id"]),
                    "upgrade_id": int(upgrade["id"]),
                    "health": int(upgrade["c"]),
                    "game_id": int(game_id),
                    "valid_from": datetime.fromtimestamp(get_normal_timestamp(timestamp)),
                })
    return buildings
