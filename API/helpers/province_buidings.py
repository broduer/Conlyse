def get_province_buildings(province, upgrades, ranked):
    province["bd"] = {}
    province["tc"] = 0

    """
    Calculate for every building their cost and their children by using a recursive function.  
    Example Level 4 Harbour has also level 3, 2 and 1 inside it.
    """
    for upgrade in province["upg"]:
        upgrade = province["upg"][upgrade]
        building = upgrades[f'{upgrade["upid"]}']
        required = getChildBuildings(upgrade["upid"], upgrades, [upgrade["upid"]])
        province["bd"][upgrade["upid"]] = {
            "upid": upgrade["upid"],
            "ht": upgrade["ht"],
            "lv": getLevel(upgrade["upid"], building["level"]),
            "rq": required
        }
        child_resources = getChildTotalResources(upgrades, required)
        province["bd"][upgrade["upid"]].pop("rq")
        province["tc"] += child_resources["tc"]
    province.pop("upg")

    # Sort buildings in province by level and type
    if ranked:
        province["bd"] = sorted(province["bd"].values(), reverse=True, key=buildingLevelSort)
    return province


def getChildBuildings(upgrade_id, upgrades, childs):
    if type(upgrade_id) == str:
        upgrade_id = int(upgrade_id)
    upgrade_child = upgrades[f"{upgrade_id}"]
    for upgrade in upgrade_child["required_upgrade"]:
        upgrade = upgrades[upgrade]
        if upgrade["upgrade_id"] not in childs:
            childs.append(upgrade["upgrade_id"])
            getChildBuildings(upgrade["upgrade_id"], upgrades, childs)
    return childs


def getChildTotalResources(upgrades, childs):
    total_resources = 0
    child = {
        "cost": {
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0,
            21: 0,
        },
        "tc": 0,
    }
    for upgrade in childs:
        upgrade = upgrades[f"{upgrade}"]
        for resource in upgrade["cost"]:
            resource_typ = int(resource)
            resource = upgrade["cost"][f"{resource}"]
            child["cost"][resource_typ + 1] += resource
            if resource_typ == 20: continue
            total_resources += resource
    child["tc"] = total_resources
    return child


def province_sort_by_building_cost(p):
    return p["tc"]


def buildingLevelSort(b):
    return b["lv"]


def getLevel(u, l):
    switch = {
        2294: 5,
        2293: 4,
        2292: 3,
        2291: 2,
        2263: 5,
        2262: 4,
        2261: 3,
        2260: 2,
        2269: 5,
        2268: 4,
        2267: 3,
        2265: 2,
    }
    return switch.get(u, l)
