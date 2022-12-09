import {getClosestTime, getDifference} from "../time";
const interval = 5
const max_days = 10
export default function getRisingPowers(countrys, game){
    let countrys_rs = {}
    // Sort Countrys after Rising Powers
    let sorted_countrys = Object.values(countrys)
    sorted_countrys = sorted_countrys.sort((a, b) => {
        return a["rs_pos"] - b["rs_pos"]
    })
    for (let country in sorted_countrys){
        country = sorted_countrys[country]
        countrys_rs[country["cid"]] = {}
        countrys_rs[country["cid"]]["name"] = country["cn"]
        countrys_rs[country["cid"]]["cid"] = country["cid"]
        countrys_rs[country["cid"]]["rs_pos"] = country["rs_pos"]
        countrys_rs[country["cid"]]["vps"] = {}
        countrys_rs[country["cid"]]["trp"] = {}

        if(Object.keys(country).includes("ts")){
            countrys_rs[country["cid"]]["trp"]["data"] = Object.values(country["ts"]).map((ts) => ts["trp"])
            countrys_rs[country["cid"]]["vps"]["data"] = Object.values(country["ts"]).map((ts) => ts["vp"])
            countrys_rs[country["cid"]]["labels"] = Object.keys(country["ts"]).map((ts_k) => getDifference(game["st"], parseInt(ts_k), "D_c"))
            let timestamps = Object.keys(country["ts"])
            for (let day = 0; day <= max_days; day++){
                if (( day === 1 || day % interval === 0) && day <= max_days){
                    let time = getClosestTime(timestamps, game["ct"] - 3600 * 24 * day)
                    if (day === 0){
                        countrys_rs[country["cid"]]["vps"][`${day}`] = country["ts"][time]["vp"]
                        countrys_rs[country["cid"]]["trp"][`${day}`] = country["ts"][time]["trp"]
                    }
                    else if (timestamps.includes(game["ct"].toString())){
                        countrys_rs[country["cid"]]["vps"][`${day}`] = country["ts"][time]["vp"]
                        countrys_rs[country["cid"]]["vps"][`l${day}`] = country["ts"][game["ct"]]["vp"] - country["ts"][time]["vp"]
                        countrys_rs[country["cid"]]["trp"][`${day}`] = country["ts"][time]["trp"]
                        countrys_rs[country["cid"]]["trp"][`l${day}`] = country["ts"][game["ct"]]["trp"] - country["ts"][time]["trp"]

                    }
                }
            }
        }
    }
    countrys_rs = Object.values(countrys_rs).sort((a, b) =>{
        return a["rs_pos"] - b["rs_pos"]
    })
    return countrys_rs
}