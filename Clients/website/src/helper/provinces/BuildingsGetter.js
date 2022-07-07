const interesting_buildings = ["Army Base", "Naval Base", "Air Base", "Military Hospital", "Underground Bunkers", "Secret Weapons Lab"]
const levels = {
    2294: 5,
    2293: 4,
    2292: 3,
    2291: 2,
    2263: 5,
    2262: 4,
    2261: 3,
    2260: 2,
    2269: 5,
    2268: 4,
    2267: 3,
    2265: 2,
}
export function getInterestingBuildingName(ibid){
    return interesting_buildings[ibid]
}

export function getLevel(upid, lv){
    if (Object.keys(levels).includes(parseInt(upid))) return levels[parseInt(upid)]
    else return lv
}

export function getInterestingBuilding(name){
    if (interesting_buildings.includes(name)) return interesting_buildings.indexOf(name)
    else return undefined
}