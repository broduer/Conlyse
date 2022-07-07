import * as React from "react"
import {ArrowDownward, ArrowUpward} from "@mui/icons-material";
import {Button, ButtonGroup} from "@mui/material";

export default function LayerChanger({index, drawings, setDrawings}) {
    const changeOrder = (value) => {
        let cp = [...drawings]
        let drawing = cp[index]
        let temp = cp[index + value]
        if (temp) {
            cp[index] = temp
            cp[index + value] = drawing
        }else {
            if(value === -1){
                temp = cp[0]
                for(let i=0; i<cp.length-1; i++){
                    cp[i] = cp[i+1];
                }
                cp[cp.length - 1] = temp
            }else {
                temp = cp[cp.length -1]
                for (let i= cp.length - 1; i >= 0; i--){
                    cp[i] = cp[i-1];
                }
                cp[0] = temp
            }

        }
        setDrawings(cp)
    }
    return (
        <ButtonGroup size={"small"}>
            <Button onClick={() => changeOrder(-1)}>
                <ArrowUpward/>
            </Button>
            <Button onClick={() => changeOrder(1)}>
                <ArrowDownward/>
            </Button>
        </ButtonGroup>
    )
}