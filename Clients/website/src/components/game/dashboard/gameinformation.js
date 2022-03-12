import React from 'react';
import {Box, List, ListItem, ListItemText, ListSubheader, Typography} from "@mui/material";
import {getDatefromTimestamp, getRealtime} from "../../../helper/time";

export default function Gameinformation({game, scenario}){
    return(
        <Box sx={{
            bgcolor: "divider",
            border: 3,
            borderColor: "primary.main",
            borderRadius: 10,
        }}>
            <List dense={true} sx={{
                lineHeight: 1
            }}>
                <Typography variant={"h2"} fontSize={"x-large"} textAlign={"center"} color={"white"} sx={{
                    textDecoration:"underline"
                }}>
                    Game Information <br/>
                </Typography>
                <ListItem key={"Realtime Scan"}>
                    Realtime Scan: {getDatefromTimestamp(getRealtime(game["start_time"], game["current_time"], scenario["speed"]), "h:m: D.M.Y")}
                </ListItem>
                <ListItem>
                        Start Time: {getDatefromTimestamp(game["start_time"], "h:m: D.M.Y")}
                </ListItem>
                <ListItem>
                        Status: {game["end_time"]==null ? "Running" : "Ended"}
                </ListItem>
                <ListItem>
                        Game Mode: {scenario["name"]}
                </ListItem>
            </List>
        </Box>
    )
}