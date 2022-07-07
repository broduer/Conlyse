import {TextField} from "@mui/material";
import {maxStrokeWidth} from "../../../map_const";

export default function StrokeWidthChanger({index, drawings, setDrawings}){
    let drawing = drawings[index]
    const changeStrokeWidth = (e) => {
        let cp = [...drawings]
        cp[index]["strokeWidth"] = Math.max(Math.min(Math.round(e.target.value), maxStrokeWidth), 1)
        setDrawings(cp)
    }
    return (
        <TextField value={drawing["strokeWidth"]} type={"number"} label={"Stroke Width"} variant={"standard"} sx={{maxWidth: 80}} onChange={changeStrokeWidth}/>
    )
}