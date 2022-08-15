from Bot.sort.helper import get_province_from_id


def sort_static_provinces(data_1, data_2_old):
    data_1_locations = data_1["locations"][1]
    data_2_old_locations = data_2_old["result"]["states"]["3"]["map"]["locations"][1]
    provinces = dict({})
    for province_2 in data_2_old_locations:
        province_1 = get_province_from_id(province_2["id"], data_1_locations)
        if province_2["@c"] == "p":
            if province_2["pst"] > 52:
                typ = 1
            else:
                typ = 2
            if "co" in province_2:
                coastal = True
            else:
                coastal = False
            provinces[province_2["id"]] = dict({
                "province_location_id": int(province_2["id"]),
                "map_id": data_2_old["result"]["states"]["12"]["mapID"],
                "typ": typ,
                "name": province_2["n"],
                "coordinate_x": int(province_1["c"]["x"]),
                "coordinate_y": int(province_1["c"]["y"]),
                "mainland_id": int(province_1["ci"][0]),
                "region": int(province_1["r"]),
                "base_production": int(province_2["bp"]),
                "terrain_type": int(province_1["tt"]),
                "resource_production_type": int(province_2["r"]),
                "b": province_1["b"],
                "coastal": coastal,
            })

        else:
            provinces[province_1["id"]] = dict({
                "province_location_id": int(province_1["id"]),
                "map_id": data_2_old["result"]["states"]["12"]["mapID"],
                "typ": 3,
                "name": province_2["n"],
                "coordinate_x": int(province_1["c"]["x"]),
                "coordinate_y": int(province_1["c"]["y"]),
                "mainland_id": None,
                "region_id": None,
                "base_production": None,
                "terrain_type": int(province_1["tt"]),
                "resource_production_type": None,
                "b": province_1["b"],
                "coastal": None,
            })
    return provinces