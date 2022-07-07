import {TextField} from "@mui/material";

export default function RadiusChanger({index, drawings, setDrawings}){
    let drawing = drawings[index]
    const changeRadius = (e) => {
        let cp = [...drawings]
        cp[index]["data"]["r"] = Math.max(Math.round(e.target.value), 1)
        setDrawings(cp)
    }
    return (
        <TextField value={drawing["data"]["r"]} type={"number"} label={"Radius"} variant={"standard"} sx={{maxWidth: 70}} onChange={changeRadius}/>
    )
}