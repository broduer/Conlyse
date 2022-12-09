import {world_width} from "./map_const";
import {Point} from "pixi.js";


export function distance(x1, y1, x2, y2) {
    return Math.hypot(x2-x1, y2-y1)
}

export function getWorld(point) {
    return Math.floor(point.x / world_width)
}

export function getPoint(point){
    return new Point(point.x - getWorld(point) * world_width, point.y)
}

export function getDrawingLevelName(drawingLevel) {
    let names = {
        "-1": "Selector",
        "0": "Pencil",
        "1": "Line",
        "2": "Circle",
        "3": "Polygon",
    }
    return names[`${drawingLevel}`]
}