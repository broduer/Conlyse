def get_production(country):
    country["prd"] = {}
    for weapon in country["wp"]:
        weapon = country["wp"][weapon]
        if weapon["wtyp"] == 0:  # Weapon is undifined
            continue
        elif weapon["wtyp"] in [2363, 2971, 2978]:  # Starting with one Towed Artillery
            country["prd"][weapon["wtyp"]] = {
                "wtyp": weapon["wtyp"],
                "count": max(weapon["ntw"], weapon["lsw"] - 1),
            }
        elif weapon["wtyp"] in [3023, 3030, 2435]:  # Starting with one Air Superiority Fighter
            country["prd"][weapon["wtyp"]] = {
                "wtyp": weapon["wtyp"],
                "count": max(weapon["ntw"], weapon["lsw"] - 1),
            }
        elif weapon["wtyp"] in [2943, 2950, 2335]:  # Starting with sometimes two Combat Recon Vehicle
            country["prd"][weapon["wtyp"]] = {
                "wtyp": weapon["wtyp"],
                "count": max(weapon["ntw"], weapon["lsw"] - 2),
            }
        elif weapon["wtyp"] in [2901, 2299, 2908]:   # Starting with sometimes up to 10 Infantry
            country["prd"][weapon["wtyp"]] = {
                "wtyp": weapon["wtyp"],
                "count": max(weapon["ntw"], weapon["lsw"] - 10),
            }
        else:
            country["prd"][weapon["wtyp"]] = {
                "wtyp": weapon["wtyp"],
                "count": max(weapon["ntw"], weapon["lsw"]),
            }
    country.pop("wp")
    return country
