export default function getRows(teams, countrys){
    for (let country in countrys){
        country = countrys[country]
        country["id"] = country["cid"]
        country["tn"] = teams.find((team) => team["utid"] === country["utid"])?.tn
    }
    return Object.values(countrys)
}