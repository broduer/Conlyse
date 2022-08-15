def sort_static_scenarios(data_3):
    data_3_scenarios = data_3["result"]
    scenarios = dict({})
    for item in data_3_scenarios:
        if item["@c"] == "ultshared.UltScenario":
            if "scenarioSpeedUpFactor" in item["options"]:
                speed = int(item["options"]["scenarioSpeedUpFactor"])
            else:
                speed = 1
            scenarios[item["itemID"]] = dict({
                "scenario_id": int(item["itemID"]),
                "map_id": int(item["mapID"]),
                "name": item["ingameName"],
                "speed": speed,
            })
    return scenarios