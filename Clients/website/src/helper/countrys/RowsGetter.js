export default function getRows(datas){
    let countrys = datas["countrys"].data
    let countrys_adv = datas["countrys_adv"].data
    let teams = datas["teams"].data
    const row_countrys = []
    for (let country in countrys){
        country = countrys[country]
        country["id"] = country["country_id"]
        for (let team in teams){
            team = teams[team]
            if (team["universal_team_id"] === country["team_id"]){
                country["team_name"] = team["name"]
            }
        }


        let country_adv = countrys_adv[country["country_id"]]
        if (country_adv !== undefined) {
            country["victory_points"] = country_adv["victory_points"]
            country["2"] = country_adv["2"]
            country["3"] = country_adv["3"]
            country["5"] = country_adv["5"]
            country["6"] = country_adv["6"]
            country["7"] = country_adv["7"]
            country["21"] = country_adv["21"]
            country["total_economy"] = 0
            for (let type in country_adv){
                if (["2","3","5","6","7"].includes(type)){
                    country["total_economy"]+=country_adv[type]
                }
            }
        }
        row_countrys.push(country)
    }

    return row_countrys
}