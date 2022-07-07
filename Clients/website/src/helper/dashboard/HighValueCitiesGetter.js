export default function getHighValueCities(cities, countrys, upgrades){
    for (let city in cities){
        city = cities[city]
        city["id"] = city["plid"]
        city["country"] = countrys[city["oid"]]["cn"]
        city["province"] = city["pn"]

        let building = city["bd"][0]
        let upgrade = upgrades[building["upid"]]
        city["building"] = upgrade["name"] + " - " + building["lv"]

        for (let building in city["bd"]){
            building = city["bd"][building]
            let upgrade = upgrades[building["upid"]]
            if (!["Arms Industry", "Recruiting Office"].includes(upgrade["name"])){
                city["building"] = upgrade["name"] + " - " + building["lv"]
                break
            }
        }
        city["total"] = city["tc"]
    }
    return cities
}
