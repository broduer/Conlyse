import {getDifference} from "../time";

export default function getRisingPowers(countrys, countrys_adv, start_time, current_time){
    var countrys_new = {}
    for (var country in countrys){
        country = countrys[country]
        countrys_new[country.country_id] = {}
        countrys_new[country.country_id]["country_id"] = country.country_id
        countrys_new[country.country_id]["victory_points"] = {
            "last_1": 0,
            "last_5": 0,
            "last_10": 0,
        }
        countrys_new[country.country_id]["economy"] = {
            "last_1": 0,
            "last_5": 0,
            "last_10": 0,
        }
        countrys_new[country.country_id]["economy"]["data"] = []
        countrys_new[country.country_id]["victory_points"]["data"] = []
        countrys_new[country.country_id]["labels"] = []
        countrys_new[country.country_id]["name"] = country["country_name"]
        let current_country = Object.values(countrys_adv).filter(country_adv => {
            return(country["country_id"] === country_adv["country_id"]
            && country_adv["current_time"] === current_time)
        })[0]
        if(current_country == null) continue
        let current_country_economy = getTotalEconomy(current_country)
        let country_times = Object.values(countrys_adv).filter(country_adv => country["country_id"] === country_adv["country_id"])
        for(let country_time in country_times){
            country_time = country_times[country_time]
            let total_economy = getTotalEconomy(country_time)
            let day_difference = getDifference(country_time["current_time"] - 300, current_time,"D")
            if(day_difference <=10){
                countrys_new[country.country_id]["labels"].push(getDifference(start_time, country_time["current_time"], "D"))
                countrys_new[country.country_id]["economy"]["data"].push(total_economy)
                countrys_new[country.country_id]["victory_points"]["data"].push(country_time["victory_points"])
            }
            // eslint-disable-next-line default-case
            switch (day_difference){
                case 1:
                    countrys_new[country.country_id]["economy"]["last_1"] = current_country_economy - total_economy
                    countrys_new[country.country_id]["victory_points"]["last_1"] = current_country["victory_points"] - country_time["victory_points"]
                    continue
                case 5:
                    countrys_new[country.country_id]["economy"]["last_5"] = current_country_economy - total_economy
                    countrys_new[country.country_id]["victory_points"]["last_5"] = current_country["victory_points"] - country_time["victory_points"]
                    continue
                case 10:
                    countrys_new[country.country_id]["economy"]["last_10"] = current_country_economy - total_economy
                    countrys_new[country.country_id]["victory_points"]["last_10"] = current_country["victory_points"] - country_time["victory_points"]
            }
        }
    }
    var countrys_sorted = Object.values(countrys_new)
    countrys_sorted.sort((a, b) => {
        return b.victory_points.last_5 - a.victory_points.last_5;
    });
    return countrys_sorted
}

function getTotalEconomy(economy){
    return economy["2"] + economy["3"] + economy["5"] + economy["6"] + economy["7"]
}