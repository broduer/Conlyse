import {getDifference} from "../time";

export default function getTotalEconomy(country, game){
    let factor = Object.keys(country["ts"]).length / (getDifference(game["st"], Object.keys(country["ts"])[Object.keys(country["ts"]).length - 1], "D") + 1)
    let res = Object.values(country["ts"]).reduce((acc, obj) =>
    {
        Object.entries(obj).forEach(([k, v]) =>
        {
            acc[k] = (acc[k] || 0) + v;
        });

        return acc;
    }, {});
    for (let key in res){
        res[key] = res[key] / factor
    }
    return res;
}

export function getGraphData(country, game){
    country["economy"] = {}
    country["economy"]["labels"] = Object.keys(country["ts"]).map((ts) => getDifference(game["st"], ts, "D_c"))
    for (let key in Object.keys(Object.values(country["ts"])[0])){
        let type = (Object.keys(Object.values(country["ts"])[0])[key])
        country["economy"][type] = Object.values(country["ts"]).map((item) => item[type])
    }
    return country
}