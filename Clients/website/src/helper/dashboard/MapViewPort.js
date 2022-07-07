import React from "react";
import * as PIXI from "@inlet/react-pixi";
import { PixiComponent, useApp } from "@inlet/react-pixi";
import { Viewport as PixiViewport } from "pixi-viewport";

export interface ViewportProps {
    width: number;
    height: number;
    children?: React.ReactNode;
}

export interface PixiComponentViewportProps extends ViewportProps {
    app: PIXI.Application;
}

const PixiComponentViewport = PixiComponent("Viewport", {
    create: (props: PixiComponentViewportProps) => {
        const viewport = new PixiViewport({
            screenWidth: props.width,
            screenHeight: props.height,
            worldWidth: props.width,
            worldHeight: props.height,
            ticker: props.app.ticker,
            interaction: props.app.renderer.plugins.interaction
        });
        viewport.drag().pinch().wheel().clampZoom({
            minScale: 1,
            maxScale: 14,
        });
        viewport.bounce({
            time: 500,
        })

        return viewport;
    }
});

const Viewport = (props: ViewportProps) => {
    const app = useApp();
    return <PixiComponentViewport app={app} {...props} />;
};

export default Viewport;
