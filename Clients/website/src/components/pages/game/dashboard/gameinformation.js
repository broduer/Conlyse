import React from 'react';
import {Box, List, ListItem, Typography} from "@mui/material";
import {getDatefromTimestamp, getRealtime} from "../../../../helper/time";

export default function Gameinformation({game}){
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
                    Realtime Scan: {getDatefromTimestamp(getRealtime(game["st"], game["ct"], game["sp"]), "h:m: D.M.Y")}
                </ListItem>
                <ListItem>
                        Start Time: {getDatefromTimestamp(game["st"], "h:m: D.M.Y")}
                </ListItem>
                <ListItem>
                        Status: {game["et"]==null ? "Running" : "Ended"}
                </ListItem>
                <ListItem>
                        Game Mode: {game["sn"]}
                </ListItem>
            </List>
        </Box>
    )
}