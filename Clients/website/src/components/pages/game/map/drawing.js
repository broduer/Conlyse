import {decodeBorder} from "../../../../helper/map";
import * as PIXI from "pixi.js";
import {color_schema} from "../../../../helper/color";

function getPoints(b) {
    const points = decodeBorder(b)
    let points_arr = []
    for (let point in points){
        point = points[point]
        points_arr.push( new PIXI.Point(point["x"], point["y"]))
    }
    return points_arr
}

export function getGraphics(provinces){
    let g = new PIXI.Graphics()
    g.interactive = true
    g.lineStyle(2, 0x000000)
    for (let province in provinces){
        province = provinces[province]
        let polygon = new PIXI.Polygon(getPoints(province["bt"]))
        province["points"] = polygon.points
        g.beginFill(color_schema[province["oid"] % 150])
        g.drawPolygon(polygon)
        g.endFill()
    }
    return g
}