def sort_static_countries(map_id, data_2):
    data_countries = data_2["result"]["states"]["1"]["players"]
    static_countries = []
    for country in data_countries:
        country = data_countries[country]
        if "siteUserID" in country:
            if int(country["playerID"]) > 0:
                static_countries.append({
                    "country_id": int(country["playerID"]),
                    "faction": int(country["faction"]),
                    "name": country["nationName"],
                    "native_computer": bool(country["nativeComputer"]),
                    "map_id": map_id,
                })
    return static_countries
