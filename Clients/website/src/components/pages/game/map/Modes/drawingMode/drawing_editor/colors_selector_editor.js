import {ButtonGroup, IconButton, Popover} from "@mui/material";
import {Rectangle, RectangleOutlined} from "@mui/icons-material";
import {useState} from "react";
import {RgbaColorPicker} from "react-colorful";
import {customToCSS, customToRgba, rgbaToCustom} from "../../../../../../../helper/color";

export default function ColorsSelectorEditor({index, drawings, setDrawing}){
    let drawing = drawings[index]

    const [anchorFill, setAnchorFill] = useState(null);
    const [anchorOutline, setAnchorOutline] = useState(null);

    const handleSetColour = (rgba, key) => {
        let cp = [...drawings]
        cp[index][key] = rgbaToCustom(rgba)
        setDrawing(cp)
    }


    const handleFillClick = (event) => {
        setAnchorFill(event.currentTarget);
    };

    const handleOutlineClick = (event) => {
        setAnchorOutline(event.currentTarget);
    };

    const handleFillClose = () => {
        setAnchorFill(null);
    };

    const handleOutlineClose = () => {
        setAnchorOutline(null);
    };

    const open_fill = Boolean(anchorFill);
    const open_outline = Boolean(anchorOutline);

    const id_fill = open_fill ? 'simple-popover' : undefined;
    const id_outline = open_outline ? 'simple-popover' : undefined;


    return (
        <ButtonGroup size={"small"}>
            <IconButton onClick={handleFillClick}>
                <Rectangle sx={{color: customToCSS(drawing["fillColor"])}}/>
            </IconButton>
            <Popover
                id={id_fill}
                open={open_fill}
                anchorEl={anchorFill}
                onClose={handleFillClose}
                anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'left',
                }}
                sx={{overflow: "hidden"}}
            >
                <RgbaColorPicker color={customToRgba(drawing["fillColor"])} onChange={(data) => handleSetColour(data, "fillColor")} style={{overflow: "hidden"}}/>
            </Popover>
            <IconButton onClick={handleOutlineClick}>
                <RectangleOutlined sx={{color: customToCSS(drawing["outlineColor"])}}/>
            </IconButton>
            <Popover
                id={id_outline}
                open={open_outline}
                anchorEl={anchorOutline}
                onClose={handleOutlineClose}
                anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'left',
                }}
            >
                <RgbaColorPicker color={customToRgba(drawing["outlineColor"])} onChange={(data) => handleSetColour(data, "outlineColor")} style={{overflow: "hidden"}}/>
            </Popover>
        </ButtonGroup>
    )
}