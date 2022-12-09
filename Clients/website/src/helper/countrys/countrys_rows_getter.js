export default function get_rows(teams, countrys){
    for (let country in countrys){
        country = countrys[country]
        country["id"] = country["cid"]
        country["tn"] = teams.find((team) => team["utid"] === country["utid"])?.tn
        if("ts" in country){
            country = Object.assign(country, country["ts"][Object.keys(country["ts"])[Object.keys(country["ts"]).length-1]])
        }
    }
    return Object.values(countrys)
}