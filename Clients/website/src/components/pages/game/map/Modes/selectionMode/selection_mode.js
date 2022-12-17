import * as PIXI from "pixi.js";
import {getPoint, getWorld} from "../../utils";
import {world_width} from "../../map_const";

export function handleSelection(provinces, countrys, teams, points, current_selection, selectionLevel, add){
    let cs_copy = [... current_selection]
    let [selected_provinces] = getSelected_Provinces(provinces, points);
    console.log(provinces)
    let level_provinces = getLevel_Provinces(provinces, countrys, selected_provinces, selectionLevel)

    if (add){
        if(!selected_provinces.some(selected_province => !cs_copy.includes(selected_province))) {
            level_provinces.map((level_province) => cs_copy.splice([cs_copy.indexOf(level_province)], 1))
            return cs_copy
        }else {
            return [... new Set([...level_provinces, ...cs_copy])]
        }

    }else {
        // If the current selection and the new selection is the same return nothing
        let combined_arr = [... new Set([...cs_copy, ...level_provinces])]
        if (combined_arr.length !== 2 && cs_copy.length === level_provinces.length) return []
        else return level_provinces
    }
}


function getSelected_Provinces(provinces, points){
    let selected_provinces;
    if (points.length === 1){
        // Check which Province contains point
        selected_provinces = Object.values(provinces).filter(pro => new PIXI.Polygon(pro["points"]).contains(getPoint(points[0]).x, getPoint(points[0]).y))
        console.log(provinces)
    }else {
        // Make Rectangle given from two points with a positive width and height
        let rect = new PIXI.Rectangle(
            Math.min(points[0].x, points[1].x),
            Math.min(points[0].y, points[1].y),
            Math.max(points[0].x, points[1].x) - Math.min(points[0].x, points[1].x),
            Math.max(points[0].y, points[1].y) - Math.min(points[0].y, points[1].y))
        rect.x = rect.x - getWorld(new PIXI.Point(rect.x, rect.y)) * world_width

        // After correction for the x coordinate check all provinces if their center is inside the rectangle
        selected_provinces = Object.values(provinces).filter(pro => rect.contains(parseInt(pro["cdx"]), parseInt(pro["cdy"])))
    }
    return [selected_provinces]
}

function getLevel_Provinces(provinces, countrys, selected_provinces, selectionLevel){
    if (selectionLevel === 0) return selected_provinces
    else if (selectionLevel === 1) {
        // all country_ids from the selected provinces and removes duplicates
        let country_ids = [... new Set(Object.values(selected_provinces).map((selected_province) => selected_province["oid"]))]
        return Object.values(provinces).filter(pro => country_ids.includes(pro["oid"]))
    }else if (selectionLevel === 2){
        // all team_ids from the selected provinces and removes duplicates
        let team_ids = [... new Set(Object.values(selected_provinces).map((selected_province) => countrys[selected_province["oid"]]["utid"]))]
        return Object.values(provinces).filter(pro => team_ids.includes(countrys[pro["oid"]]["utid"]))
    }
}
