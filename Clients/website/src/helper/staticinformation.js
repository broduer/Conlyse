export function getTeamsbyVP(teams, countrys){
    for (var team in teams){
        team = teams[team]
        team["players"] = []
        team["victory_points"] = 0
        for (var country in countrys){
            country = countrys[country]
            if (country.team_id===team.universal_team_id){
                team["victory_points"] += country.victory_points
                team["players"].push(country.country_id)
            }
        }
    }
    var teams_sorted = Object.values(teams)
    teams_sorted.sort((a, b) => {
        return b.victory_points - a.victory_points;
    });

    return teams_sorted
}

export function getCountrysByTimestamp(countrys, provinces){
    for (var country in countrys) {
        country = countrys[country]
        country["victory_points"] = 0
        for (var province in provinces){
            province = provinces[province]
            if (province.owner_id===country.country_id){
                country["victory_points"]+=province.victory_points
            }
        }
    }
    var countrys_sorted = Object.values(countrys)
    countrys_sorted.sort((a, b) => {
        return b.victory_points - a.victory_points;
    });
    return countrys_sorted
}


export function getcurrent_provinces(provinces, current_time){
    var current_provinces = {}
    for(var province in provinces){
        province = provinces[province]
        if (province.current_time===current_time){
            current_provinces[province.province_id] = province
        }
    }
    return current_provinces
}

export function sortbylatestDate(a, b) {
    var dateA = new Date(a.date).getTime();
var dateB = new Date(b.date).getTime();
return dateA > dateB ? 1 : -1;
}