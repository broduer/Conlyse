import {Box} from "@mui/material";
import {useEffect, useState,} from "react";
import React from "react";
import * as PIXI from "pixi.js";
import { SmoothGraphics as Graphics } from '@pixi/graphics-smooth';
import { LINE_SCALE_MODE } from '@pixi/graphics-smooth';
import {map_app, viewport} from "./map_app";
import {getGraphics} from "./drawing";
import {handleSelection} from "./Modes/selectionMode/selection_mode";
import {pushDrawing} from "./Modes/drawingMode/drawing_mode";
import {defaultTextStyle, world_width, world_height, selectionColour, selectionLockedColour} from "./map_const";


export default function Map({provinces, countrys, teams, mode, selectionLevel, drawingLevel, fillColor, outlineColor, strokeWidth, drawings, setDrawings, finalDrawing, current_selection, setCurrentSelection}){
    const div_ref = React.createRef();
    // Global
    const [loaded, setLoaded] = useState(false)
    const [mousedown, setMousedown] = useState(false);

    // Selection
    const [selectPosition, setSelectPosition] = useState()


    // Drawing
    const [currentDrawing, setCurrentDrawing] = useState();

    // Drawing Modes
    const [drawPosition, setDrawPosition] = useState()

    useEffect(() => {
        if (div_ref.current && !loaded) {
            div_ref.current.appendChild(map_app.view)
            map_app.start()
            let left = getGraphics(provinces)
            let middle = new PIXI.Graphics(left.geometry)
            let right = new PIXI.Graphics(left.geometry)
            middle.x = world_width
            right.x = world_width * 2
            const selectRect = new Graphics()
            selectRect.name = "selectRect"

            const selection_container = new PIXI.Container()
            selection_container.name = "selection_container"

            const drawings_container = new PIXI.Container()
            drawings_container.name = "drawings_container"

            const drawing_graphic = new Graphics()
            drawing_graphic.name = "drawing_graphic"

            const drawing_info = new PIXI.Text("Test", defaultTextStyle)
            drawing_info.name = "drawing_info"

            viewport.addChild(left, middle, right, selection_container, drawings_container, drawing_graphic, drawing_info, selectRect)

            // Reset Selection if pointer leaves window
            viewport.on("pointerout", () => setSelectPosition())

            // Resets Viewport to enable infinitive scrolling
            viewport.on("moved-end", event => {
                if (event.right < world_width){
                    viewport.right += world_width
                }else if(event.left > world_width * 2){
                    viewport.left -= world_width
                }
            })
            resize()
            map_app.stage.addChild(viewport)
            viewport.fit()
            viewport.moveCenter(world_width * 1.5, world_height / 2)
            setLoaded(true)
        }
        return () => {
            viewport.removeChildren(0, viewport.children.length-1)
            map_app.stop()
        }
    }, [])


    // Resizing of Canvas to window
    const resize = () => map_app.renderer.resize(window.innerWidth , window.innerHeight)

    useEffect(() => {
        window.addEventListener("resize", resize)
        return () => window.removeEventListener("resize", resize)
    }, [])

    // Stop currentDrawing

    const cancelDrawing = (event) => {
        if(event.key === "Escape" && currentDrawing){
            viewport.getChildByName("drawing_graphic").clear()
            viewport.getChildByName("drawing_info").text = ""

            setCurrentDrawing()

        }
    }
    useEffect(() => {
        window.addEventListener("keydown", cancelDrawing)
        return () => window.removeEventListener("keydown", cancelDrawing)
    }, [currentDrawing])

    // Only if Mode changes Mouse-buttons for dragging need to be changed
    useEffect(()=> {
        if (mode === 0 || mode === 2) viewport.drag({mouseButtons: "right"})
        if (mode === 1) {
            viewport.drag({mouseButtons: "all"})
            setCurrentSelection([])
        }
    }, [mode])


    // New Click Listener with new Mode State
    useEffect(()=> {
        const handleSetSelectionPosition = (event) => {
            setMousedown(true)
            if (mode === 0) setSelectPosition(event.data.getLocalPosition(viewport))
        }
        viewport.on("mousedown", handleSetSelectionPosition)
        return () => viewport.removeListener("mousedown")
    }, [mode, drawingLevel])


    // Mouse UP in Selection Mode
    // Mouse UP either normal left click or selection box
    useEffect(()=> {
        const handleSetSelection = (event) => {
            setMousedown(false)
            let pos = event.data.getLocalPosition(viewport)
            if (!!selectPosition && mode === 0){
                if (Math.hypot(Math.abs(pos.x - selectPosition.x), Math.abs(pos.y - selectPosition.y)) < viewport.threshold){
                    setCurrentSelection(handleSelection(provinces, countrys, teams, [pos], current_selection, selectionLevel, event.data.originalEvent.shiftKey))
                }
                else{
                    setCurrentSelection(handleSelection(provinces, countrys, teams, [pos, selectPosition], current_selection, selectionLevel, event.data.originalEvent.shiftKey))
                }
            }
            setSelectPosition()
            let selectRect = viewport.getChildByName("selectRect")
            selectRect.clear()
        }
        viewport.on("mouseup", handleSetSelection)
        return () => viewport.removeListener("mouseup", handleSetSelection)
    }, [selectPosition, mode, current_selection, selectionLevel])





    // Refresh Mousemove Event to draw Selection Rectangular at every mouse Movement
    useEffect(()=> {
        const handleSelectionMove = (event) => {
            // Clear old Rectangular
            let selectRect = viewport.getChildByName("selectRect")
            if (!!selectPosition && mode === 0) {
                let pos = event.data.getLocalPosition(viewport)
                selectRect.clear()
                selectRect.beginFill(selectionColour[0], selectionColour[1])
                selectRect.drawRect(
                    Math.min(pos.x, selectPosition.x),
                    Math.min(pos.y, selectPosition.y),
                    Math.max(pos.x, selectPosition.x) - Math.min(pos.x, selectPosition.x),
                    Math.max(pos.y, selectPosition.y) - Math.min(pos.y, selectPosition.y),
                );
                selectRect.endFill()
            }
        }
        viewport.on("mousemove", handleSelectionMove)

        return () => viewport.removeListener("mousemove", handleSelectionMove)
    }, [mode, selectPosition])

    // Draw Current Selection
    useEffect(() => {
        let selection_container = viewport.getChildByName("selection_container")
        selection_container.removeChildren()
        let selection_graphic = new PIXI.Graphics()
        for (let province in current_selection){
            province = current_selection[province]
            let polygon = new PIXI.Polygon(province["points"])
            selection_graphic.beginFill(selectionLockedColour[0], selectionLockedColour[1])
            selection_graphic.drawPolygon(polygon)
            selection_graphic.endFill()
        }
        let middle = selection_graphic.clone()
        let right = selection_graphic.clone()
        middle.x = world_width
        right.x = world_width * 2
        selection_container.addChild(selection_graphic, middle, right)
    }, [current_selection])


    // Reset Current Drawing if DrawingLevel changes
    useEffect(() => {
        setCurrentDrawing()
        viewport.getChildByName("drawing_graphic").clear()
        viewport.getChildByName("drawing_info").text = ""
    }, [mode, drawingLevel])




    // Mousedown Event Drawing Mode
    useEffect(() => {
        const handleLineSet = (event) => {
            if(mode === 2){
                let pos = event.data.getLocalPosition(viewport)
                let drawing_graphic = viewport.getChildByName("drawing_graphic")
                let drawing_info = viewport.getChildByName("drawing_info")
                drawing_info.text = ""
                drawing_graphic.clear()
                if (drawingLevel === 0){
                    let pos = event.data.getLocalPosition(viewport)
                    let drawing_graphic = viewport.getChildByName("drawing_graphic")
                    drawing_graphic.lineStyle({color: fillColor[0], alpha: fillColor[1],width: strokeWidth})
                    setCurrentDrawing([pos])
                    setDrawPosition(pos)
                }
                else if (drawingLevel === 1){
                    if (currentDrawing) {
                        setDrawings(pushDrawing(drawings, drawingLevel, fillColor, fillColor, strokeWidth, {...currentDrawing, "x2": pos.x, "y2": pos.y}))
                        setCurrentDrawing()
                    }else {
                        setCurrentDrawing({"x1": pos.x, "y1": pos.y})
                    }
                }else if (drawingLevel === 2){
                    if (currentDrawing) {
                        let r = Math.round(Math.hypot(Math.abs(pos.x - currentDrawing["x"]), Math.abs(pos.y - currentDrawing["y"])))
                        setDrawings(pushDrawing(drawings, drawingLevel, fillColor, outlineColor, strokeWidth, {...currentDrawing, "r": r}))
                        setCurrentDrawing()
                    }else {
                        setCurrentDrawing({"x": pos.x, "y": pos.y})
                    }
                }
            }
        }
        viewport.on("mousedown", handleLineSet)
        return () => viewport.removeListener("mousedown", handleLineSet)
    }, [mode, drawingLevel, currentDrawing, finalDrawing, fillColor, outlineColor, strokeWidth])


    useEffect(() => {
        const handlePencilSet = () => {
            if (mode === 2 && drawingLevel === 0){
                if (currentDrawing && currentDrawing.length >= 2) {
                    let drawing_graphic = viewport.getChildByName("drawing_graphic")
                    drawing_graphic.clear()
                    setDrawings(pushDrawing(drawings, drawingLevel, fillColor, fillColor, strokeWidth, currentDrawing))
                }
            }
        }
        viewport.addListener("mouseup", handlePencilSet)
        return () => viewport.removeListener("mouseup", handlePencilSet)
    }, [mode, drawingLevel, currentDrawing, finalDrawing, fillColor, outlineColor, strokeWidth])

    // Refresh Mousemove Event to draw CurrentDrawing at every mouse Movement
    // Refresh Mousemove Event to draw Selection Rectangular at every mouse Movement
    useEffect(()=> {
        const handleDrawingMove = (event) => {
            let drawing_graphic = viewport.getChildByName("drawing_graphic")
            let drawing_info = viewport.getChildByName("drawing_info")
            if(mode === 2){
                if (drawingLevel === 0 && mousedown && currentDrawing){
                    let pos = event.data.getLocalPosition(viewport)
                    if(Math.hypot(Math.abs(pos.x - drawPosition.x), Math.abs(pos.y - drawPosition.y)) > strokeWidth * 0.3){
                        drawing_graphic.moveTo(drawPosition.x, drawPosition.y)
                        drawing_graphic.lineTo(pos.x, pos.y)
                        setDrawPosition(pos)
                        let cp = [...currentDrawing]
                        cp.push(pos)
                        setCurrentDrawing(cp)
                    }
                }else if (drawingLevel === 1 && currentDrawing){
                    let pos = event.data.getLocalPosition(viewport)
                    drawing_info.position = new PIXI.Point(pos.x + 30, pos.y + 20)
                    drawing_info.text = Math.round(Math.hypot(Math.abs(pos.x - currentDrawing["x1"]), Math.abs(pos.y - currentDrawing["y1"])).toString(10))
                    drawing_graphic.clear()
                    drawing_graphic.lineStyle({color: fillColor[0], alpha: fillColor[1],width: strokeWidth, scaleMode: LINE_SCALE_MODE.NORMAL });
                    drawing_graphic.moveTo(currentDrawing["x1"], currentDrawing["y1"])
                    drawing_graphic.lineTo(pos.x, pos.y)
                }else if (drawingLevel === 2 && currentDrawing){
                    let pos = event.data.getLocalPosition(viewport)
                    let r = Math.hypot(Math.abs(pos.x - currentDrawing["x"]), Math.abs(pos.y - currentDrawing["y"]))
                    drawing_info.position = new PIXI.Point(pos.x + 30, pos.y + 20)
                    drawing_info.text = Math.round(r).toString(10)
                    drawing_graphic.clear()
                    drawing_graphic.beginFill(fillColor[0], fillColor[1])
                    drawing_graphic.lineStyle({color: outlineColor[0], alpha: outlineColor[1],width: strokeWidth, scaleMode: LINE_SCALE_MODE.NORMAL });
                    drawing_graphic.drawCircle(currentDrawing["x"], currentDrawing["y"], r)
                    drawing_graphic.endFill()
                }
            }
        }
        viewport.on("mousemove", handleDrawingMove)
        return () => viewport.removeListener("mousemove", handleDrawingMove)
    }, [mode, mousedown, currentDrawing, drawPosition, drawingLevel, fillColor, outlineColor, strokeWidth])


    // Draw all finished Drawings if drawings updated
    useEffect(() => {
        let drawings_container = viewport.getChildByName("drawings_container")
        drawings_container.removeChildren()
        let drawings_graphic = new PIXI.Graphics()
        for (let drawing in drawings){
            drawing = drawings[drawing]
            console.log(drawing)
            drawings_graphic.lineStyle({width: drawing["strokeWidth"], color: drawing["outlineColor"][0], alpha: drawing["outlineColor"][1]})
            switch (drawing["drawingLevel"]){
                case -1:
                    for (let polygon in drawing["data"]){
                        polygon = drawing["data"][polygon]
                        drawings_graphic.beginFill(drawing["fillColor"][0], drawing["fillColor"][1])
                        drawings_graphic.drawPolygon(polygon)
                        drawings_graphic.endFill()
                    }
                    break
                case 0:
                    // Pencil
                    let point = drawing["data"][0]
                    drawings_graphic.moveTo(point.x, point.y)
                    drawings_graphic.lineStyle({width: drawing["strokeWidth"], color: drawing["outlineColor"][0], alpha: drawing["outlineColor"][1]})
                    for (let key in drawing["data"]){
                        let next_point = drawing["data"][parseInt(key) + 1]
                        if (next_point){
                            drawings_graphic.lineTo(next_point.x, next_point.y)
                        }
                    }
                    break
                case 1:
                    // Line
                    drawings_graphic.moveTo(drawing["data"]["x1"], drawing["data"]["y1"])
                    drawings_graphic.lineTo(drawing["data"]["x2"], drawing["data"]["y2"])
                    break
                case 2:
                    drawings_graphic.beginFill(drawing["fillColor"][0], drawing["fillColor"][1])
                    drawings_graphic.drawCircle(drawing["data"]["x"], drawing["data"]["y"], drawing["data"]["r"])
                    drawings_graphic.endFill()
                    break
            }
        }
        let left = drawings_graphic.clone()
        let right = drawings_graphic.clone()
        left.x = -world_width
        right.x = world_width
        drawings_container.addChild(drawings_graphic, left, right)
    }, [drawings])


    return (
        <Box style={{width: "100%", height:"calc(100vh - 65px)", overflow: "hidden"}} ref={div_ref}/>
    )
}