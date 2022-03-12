def getResearch(countrys):
    new_countrys = {}
    for country in countrys:
        country = countrys[country]
        if country["country_id"] not in new_countrys.keys():
            new_countrys[country["country_id"]] = {
                "country_id": country["country_id"],
                "researches": []
            }
        if country["wtyp"] in [2363, 2971, 2978]:
            if country["count"] < -1:
                new_countrys[country["country_id"]]["researches"].append(country["wtyp"])
            continue
        if country["wtyp"] in [3023, 3030, 2435]:
            if country["count"] < -1:
                new_countrys[country["country_id"]]["researches"].append(country["wtyp"])
            continue
        if country["wtyp"] in [2943, 2950, 2335]:
            if country["count"] < -2:
                new_countrys[country["country_id"]]["researches"].append(country["wtyp"])
            continue
        if country["wtyp"] in [2901, 2299, 2908]:
            if country["count"] < -10:
                new_countrys[country["country_id"]]["researches"].append(country["wtyp"])
            continue
        if country["wtyp"] == 0:
            continue
        if country["wtyp"] not in new_countrys[country["country_id"]]["researches"]:
            new_countrys[country["country_id"]]["researches"].append(country["wtyp"])
        if "whtyp" in country:
            new_countrys[country["country_id"]]["researches"].append(country["whtyp"])
    remove_countrys = []
    for country in new_countrys:
        country = new_countrys[country]
        if len(country["researches"]) <=0:
            remove_countrys.append(country["country_id"])
    for remove_country in remove_countrys:
        new_countrys.pop(remove_country)
    return new_countrys
