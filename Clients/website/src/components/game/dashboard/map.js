import {Box, Fab, IconButton, Stack} from "@mui/material";
import {useEffect, useRef, useState,} from "react";
import React from "react";
import * as d3 from 'd3';
import {decodeBorder} from "../../../helper/map";
import {ZoomIn, ZoomOut} from "@mui/icons-material";
import {theme} from "../../../helper/theme";
import {getCountryColor} from "../../../helper/color";
import {getTime} from "date-fns";

const height = 400
const width = 1000


let scale = 1.0;
const scaleMultiplier = 0.8;

let yScale = d3.scaleLinear()
    .domain([0, 6452])
    .range([-200, 200])
let xScale = d3.scaleLinear()
    .domain([0, 15700])
    .range([-500, 500])

function getPoints(b) {
    const points = decodeBorder(b)
    let points_arr = []
    for (let point in points){
        point = points[point]
        points_arr.push( { "x" : xScale(point["x"]), "y": yScale(point["y"])})
    }
    return points_arr
}

function draw(canvasRef, static_provinces,scale, translatePos) {
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    const time1 = new Date().getTime()
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save()

    ctx.translate(translatePos.x, translatePos.y)
    ctx.scale(scale, scale)
    //Our first draw
    for (let static_province in static_provinces){
        const time2 = new Date().getTime()
        static_province = static_provinces[static_province]
        if (static_province["terrain_type"] === 19 || static_province["terrain_type"] === 20) continue
        let points = getPoints(static_province["b"])
        const time3 = new Date().getTime()
        ctx.beginPath()
        ctx.moveTo(points[0]["x"], points[0]["y"])
        let i = 0
        points.map((point) => ctx.lineTo(point["x"], point["y"]))
        ctx.closePath()
        ctx.strokeStyle = theme.palette.secondary.main
        ctx.lineWidth = 0.4
        ctx.fillStyle = getCountryColor(static_province["owner_id"])
        ctx.fill()
        ctx.stroke()
        ctx.fillStyle = "#999999"
        const time4 = new Date().getTime()
    }
    ctx.restore()
    const time5 = new Date().getTime()
    // console.log(time5-time1)
}


export default function Map({static_provinces}){
    const [didLoad, setDidLoad] = useState(false);
    const [translatePos, settranslatePos] = useState({})
    const [mouseDown, setMouseDown] = useState(false)
    const [startDragOffset, setStartDragOffset] = useState({})
    const canvasRef = useRef()




    useEffect(() => {
        let canvas = canvasRef.current
        if (!didLoad) {
            let pos = {
                x: 500,
                y: 200,
            }
            settranslatePos(pos)
            draw(canvasRef, static_provinces,scale, pos)
        }
        setDidLoad(true)
    })
    console.log(static_provinces)
    return (
        <Box className={"Map"} sx={{
            bgcolor: "divider",
            border: 3,
            borderColor: "primary.main",
            borderRadius: 10,
            overflow: "hidden",
            position: "relative",
        }}>
            <canvas ref={canvasRef}
                    width={width}
                    height={height}
                    style={{
                        width:"100%",
                        cursor: "grab",
                    }}
                    onMouseDown={(event => {
                        setMouseDown(true)
                        setStartDragOffset({
                            x: event.clientX - translatePos.x,
                            y: event.clientY - translatePos.y,
                        })
                        event.target.style.cursor = "grabbing"
                    })}
                    onMouseUp={(event) => {
                        setMouseDown(false);
                        event.target.style.cursor = "grab"
                    }}
                    onMouseOver={() => setMouseDown(false)}
                    onMouseOut={() => setMouseDown(false)}
                    onMouseMove={(event => {
                        if(mouseDown){
                            settranslatePos({
                                x: event.clientX - startDragOffset.x,
                                y: event.clientY - startDragOffset.y,
                            })
                            let pos = {
                                x: event.clientX - startDragOffset.x,
                                y: event.clientY - startDragOffset.y,
                            }
                            draw(canvasRef, static_provinces, scale, pos)
                        }
                    })}
                    onWheel={(event => {

                        if (event.deltaY <= 0) {
                            let pos = {
                                x: translatePos.x,
                                y: translatePos.y,
                            }
                            settranslatePos(pos)
                            draw(canvasRef, static_provinces, scale /= scaleMultiplier, pos)
                            return
                        }
                        let pos = {
                            x: translatePos.x,
                            y: translatePos.y,
                        }
                        settranslatePos(pos)
                        draw(canvasRef, static_provinces, scale *= scaleMultiplier, pos)

                    })}
            />
            <Stack direction={"row"}
                   spacing={2}
                   style={{
                position: "absolute",
                bottom: 10,
                right: 20,
            }}>
                <Fab color={"primary"} size={"small"} onClick={() => {
                    console.log(scale)
                    let pos = {
                        x: translatePos.x + (scale * (translatePos.x * 0.1)),
                        y: translatePos.y + (scale * (translatePos.y * 0.1)),
                    }
                    settranslatePos(pos)
                    draw(canvasRef, static_provinces, scale /= scaleMultiplier, pos)
                }} style={{
                }}>
                    <ZoomIn/>
                </Fab>
                <Fab color={"primary"} size={"small"} onClick={() => {
                    let pos = {
                        x: translatePos.x,
                        y: translatePos.y,
                    }
                    settranslatePos(pos)
                    draw(canvasRef, static_provinces, scale *= scaleMultiplier, pos)
                }} style={{
                }}>
                    <ZoomOut/>
                </Fab>
            </Stack>

        </Box>
    )
}