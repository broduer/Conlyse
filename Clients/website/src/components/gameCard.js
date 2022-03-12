import React from 'react';
import {Button, Card, CardContent, CardHeader, Grid, Tooltip, Typography} from "@mui/material";
import VideogameAssetIcon from '@mui/icons-material/VideogameAsset';
import PlayCircleFilledWhiteIcon from '@mui/icons-material/PlayCircleFilledWhite';
import {getDatefromTimestamp, getDifference} from "../helper/time";
import {useNavigate} from "react-router-dom";
function GameCard({game, scenario}) {

    const navigate = useNavigate()
    const handleClick = (game, scenario) => {
        navigate("/game/" + game.game_id + "/dashboard", { state: {game: game, scenario: scenario}})
    }
    return (
        <div>
            <Card elevation={2}>
                <CardHeader
                    title={game.game_id}
                    subheader={getDatefromTimestamp(game.start_time, "D:M h:m")}
                    action={
                        <Tooltip title={game.end_time==null ? "Running" : "Ended"}>
                            <VideogameAssetIcon color={game.end_time==null ? "success" : "info"}/>
                        </Tooltip>
                    }
                />
                <CardContent>
                    <Grid container columns={16} >
                        <Grid item xs={12} md={12} lg={12}>
                            <Typography variant={"subtitle1"}>
                                Scenario:
                            </Typography>
                            <Typography variant={"body2"} color={"textSecondary"}>
                                {scenario.name.split("(")[0]}
                            </Typography>
                            <Typography variant={"subtitle1"}>
                                Day:
                            </Typography>
                            <Typography>
                                {getDifference(game.start_time, game.end_time===null ? game.current_time : game.end_time, "D")}
                            </Typography>
                        </Grid>
                        <Grid item >
                            <Typography variant={"subtitle1"}>
                                Speed:
                            </Typography>
                            <Typography variant={"body2"} color={"textSecondary"}>
                                {scenario.speed}x
                            </Typography>
                        </Grid>
                        <Grid container justifyContent={"flex-end"}>
                            <Button variant={"contained"} onClick={() => {
                                handleClick(game, scenario)
                            }} color={"success"} startIcon={<PlayCircleFilledWhiteIcon/>}>
                                Play
                            </Button>
                        </Grid>
                    </Grid>


                </CardContent>
            </Card>
        </div>
    );
}

export default GameCard;