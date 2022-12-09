import {InputAdornment, TextField} from "@mui/material";
import {maxStrokeWidth, minStrokeWidth} from "../../map_const";
import {LineWeight} from "@mui/icons-material";

export default function StrokeWidthSelector({strokeWidth, setStrokeWidth}){
    const handelChange = (e) => {
        setStrokeWidth(Math.min(Math.max(e.target.value, minStrokeWidth), maxStrokeWidth))
    }

    return (
        <TextField
            type={"number"}
            sx={{width: 80}}
            variant={"standard"}
            value={strokeWidth}
            InputProps={{
                startAdornment: (
                    <InputAdornment position="start">
                        <LineWeight />
                    </InputAdornment>
                ),
            }}
            onChange={handelChange}/>
    )
}