import * as PIXI from "pixi.js";
import {Viewport} from "pixi-viewport";
import {world_background_color, world_height, world_width} from "./map_const";





export const map_app = new PIXI.Application({
    backgroundColor: world_background_color,
    antialias: true
})
export const viewport = new Viewport({
    worldWidth: world_width * 3,
    worldHeight: world_height,
    ticker: map_app.ticker,
    interaction: map_app.renderer.plugins.interaction, // the interaction module is important for wheel to work properly when renderer.view is placed or scaled
    divWheel: null,
    passiveWheel: false,
    disableOnContextMenu: true,
})
    .drag()
    .pinch()
    .wheel()
    .clampZoom({
        maxScale: 2,
        minScale: 0.2,
    })
    .bounce({
        sides: "vertical",
        bounceBox: {
            y: -500,
            height: world_height + 500,
        }
    })