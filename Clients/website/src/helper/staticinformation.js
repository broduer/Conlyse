export function get_teams_by_vp(teams, countrys){
    for (let team in teams){
        team = teams[team]
        team["vp"] = 0
        for (let country in countrys){
            country = countrys[country]
            if (country["utid"]===team["utid"]){
                team["vp"] += country["vp"]
            }
        }
    }
    var teams_sorted = Object.values(teams)
    teams_sorted.sort((a, b) => {
        return b["vp"] - a["vp"];
    });

    return teams_sorted
}