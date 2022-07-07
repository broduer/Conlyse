import React from 'react';
import {Grid, Typography} from "@mui/material";
import {getDatefromTimestamp, getDifference} from "../../../../helper/time";


export default function HeaderDashboard({game}){
    return (
        <Grid container columns={{xs:10,md:16, lg: 24}} border={2}>
            <Grid item xs={2}>
                <Typography align={"left"}>
                    Day: {getDifference(game.start_time, game.current_time, "D").toString()}
                </Typography>
            </Grid>
            <Grid item xs={4}>
                <Typography align={"center"}>
                    Time: {getDatefromTimestamp(game.current_time, "h:m:s")}
                </Typography>
            </Grid>
            <Grid item xs={4} >
                <Typography align={"center"}>
                    Game ID: {game.game_id}
                </Typography>
            </Grid>
            <Grid item xs={6} className={"typo-next_heal_time"}>
                <Typography align={"right"}>
                    Next Heal Time: {getDatefromTimestamp(game.next_heal_time,"h:m: D.M.Y")}
                </Typography>
            </Grid>
            <Grid item xs={8}>

            </Grid>
        </Grid>
    )
}
