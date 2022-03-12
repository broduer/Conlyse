import {IconButton, Stack, TextField} from "@mui/material";
import {theme} from "../helper/theme";
import {ArrowLeft, ArrowRightOutlined} from "@mui/icons-material";
import * as React from "react";
export default function DayChanger({day}) {
    return (
        <Stack direction={"row"} height={40} spacing={1} sx={{
            right:0
        }}>
            <IconButton sx={{
                border: 1,
                borderColor: theme.palette.primary.main,
                height: 36,
                width: 36,
            }} variant={"outlined"}>
                <ArrowLeft color={"primary"}/>
            </IconButton>
            <TextField
                type="text"
                pattern="[0-9]*"
                onKeyPress={(event) => {
                    if (!/[0-9]/.test(event.key)) {
                        event.preventDefault();
                    }
                }}
                onInput={event => {
                    if (event.target.value >= 130){
                        event.target.value = 130
                    }else if(event.target.value < 0){
                        event.target.value = 0
                    }else {

                    }
                }}
                variant={"standard"}
                margin={"none"}
                size={"small"}
                sx={{
                    width: 35,
                }}
                value={day}
            />
            <IconButton variant={"outlined"} sx={{
                border: 1,
                borderColor: theme.palette.primary.main,
                height: 36,
                width: 36,
            }}>
                <ArrowRightOutlined color={"primary"}/>
            </IconButton>
        </Stack>
    )
}