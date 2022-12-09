import {getInterestingBuilding} from "./buildings_getter";

export function get_combined_province(provinces, static_provinces){
    for (let province in provinces){
        province = provinces[province]
        province = Object.assign(province, static_provinces[province["plid"]])
    }
    return provinces
}

export default function getRows(countrys, provinces, static_upgrades){
    for (let province in provinces){
        province = provinces[province]
        province["id"] = province["plid"]
        province["cn"] = countrys.find((country) => country["cid"] === province["oid"])?.cn
        for (let building in province["bd"]){
            building = province["bd"][building]
            let ibid = getInterestingBuilding(static_upgrades[building["upid"]]["name"])
            if (ibid !== undefined){
                province[`b${ibid}`] = building["lv"]
            }
        }
    }
    return Object.values(provinces)
}