import {Box} from "@mui/material";
import {useEffect, useState,} from "react";
import React from "react";
import {decodeBorder} from "../../../../helper/map";
import {color_schema} from "../../../../helper/color";
import * as PIXI from "pixi.js";
import { Viewport } from 'pixi-viewport'



const world_width = 16000
const world_height = 6700

const map_app = new PIXI.Application({
})

const viewport = new Viewport({
    worldWidth: world_width,
    worldHeight: world_height,
    ticker: map_app.ticker,
    interaction: map_app.renderer.plugins.interaction, // the interaction module is important for wheel to work properly when renderer.view is placed or scaled
    divWheel: null,
    passiveWheel: false,
})  .drag()
    .pinch()
    .wheel()
    .clampZoom({
        maxScale: 10,
        minScale: 0.1,
    })


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




export default function DashboardMap({provinces}){
    const div_ref = React.createRef();
    const [loaded, setLoaded] = useState(false)
    useEffect(() => {
        if (div_ref.current && !loaded) {
            map_app.start()
            div_ref.current.appendChild(map_app.view)
            let left = getGraphics(provinces)
            let middle = getGraphics(provinces)
            let right = getGraphics(provinces)
            middle.x = world_width
            right.x = world_width * 2
            viewport.addChild(left, middle, right)
            map_app.stage.addChild(viewport)
            resize()

            viewport.fit()
            viewport.moveCenter(world_width * 1.75, world_height)


            setLoaded(true)
        }
        return () => {
            viewport.removeChildren(0, viewport.children.length-1)
            map_app.stop()
        }
    }, [])


    function resize(){
        let ratio = 0.6;
        if (window.innerWidth < 1200){
            ratio = 0.8
        }
        let width = window.innerWidth * ratio
        map_app.renderer.resize( width, 400 )

    }
    window.addEventListener("resize", resize)
    return (
        <Box
            sx={{
                bgcolor: "divider",
                border: 3,
                borderColor: "primary.main",
                borderRadius: 10,
                width: "100%",
                overflow: "hidden",
            }}
            ref={div_ref}/>
    )
}