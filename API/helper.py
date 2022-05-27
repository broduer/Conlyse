from datetime import datetime


def getDayofGame(start_time, current_time):
    delta = current_time.timestamp() - start_time.timestamp()
    day = round(delta / 3600 * 24)
    return day


def getProvinceBuildings(provinces, upgrades, ranked):
    province_new = {}
    for province in provinces:
        province = provinces[province]
        if province["province_id"] not in province_new:
            province_new[province["province_id"]] = dict({
                "province_id": province["province_id"],
                "owner_id": province["owner_id"],
                "province_name": province["province_name"],
                "buildings": [],
                "total": 0
            })
        building = upgrades[f'{province["upgrade_id"]}']
        required = getChildBuildings(province["upgrade_id"], upgrades, [province["upgrade_id"]])
        province_new[province["province_id"]]["buildings"].append(dict({
            "upgrade_id": province["upgrade_id"],
            "health": province["health"],
            "name": building["name"],
            "level": getLevel(province["upgrade_id"], building["level"]),
            "required": required
        }))
        child_resources = getChildTotalResources(upgrades, required)
        province_new[province["province_id"]]["total"] += child_resources["total"]

    for province in province_new:
        province = province_new[province]
        province["buildings"] = sorted(province["buildings"], reverse=True, key=buildingLevelSort)
    if ranked:
        list_province_new = list(province_new.values())
        return sorted(list_province_new, reverse=True, key=province_TotalSort)[0:30]
    return province_new


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
        "total": 0,
    }
    for upgrade in childs:
        upgrade = upgrades[f"{upgrade}"]
        for resource in upgrade["cost"]:
            resource_typ = int(resource)
            resource = upgrade["cost"][f"{resource}"]
            child["cost"][resource_typ + 1] += resource
            if resource_typ == 20: continue
            total_resources += resource
    child["total"] = total_resources
    return child


def province_TotalSort(p):
    building = p["buildings"][0]
    if building["name"] == "Arms Industry": return -1
    if building["name"] == "Local Industry": return -1
    return p["total"]


def buildingLevelSort(b):
    return b["level"]


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
