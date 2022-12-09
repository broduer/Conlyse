import React from 'react';
import {Button, Card, CardContent, CardHeader, Grid, Tooltip, Typography} from "@mui/material";
import VideogameAssetIcon from '@mui/icons-material/VideogameAsset';
import PlayCircleFilledWhiteIcon from '@mui/icons-material/PlayCircleFilledWhite';
import {getDatefromTimestamp, getDifference} from "../helper/time";
import {useNavigate} from "react-router-dom";
function GameCard({game}) {
    const navigate = useNavigate()
    const handleClick = (game) => {
        navigate("/game/" + game.gid + "/dashboard")
    }
    return (
        <div>
            <Card elevation={2}>
                <CardHeader
                    title={game.gid}
                    subheader={getDatefromTimestamp(game.st, "D:M h:m")}
                    action={
                        <Tooltip title={game.et==null ? "Running" : "Ended"}>
                            <VideogameAssetIcon color={game.et==null ? "success" : "info"}/>
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
                                {game.sn.split("(")[0]}
                            </Typography>
                            <Typography variant={"subtitle1"}>
                                Day:
                            </Typography>
                            <Typography>
                                {getDifference(game.st, game.et===null ? game.ct : game.et, "D")}
                            </Typography>
                        </Grid>
                        <Grid item >
                            <Typography variant={"subtitle1"}>
                                Speed:
                            </Typography>
                            <Typography variant={"body2"} color={"textSecondary"}>
                                {game.sp}x
                            </Typography>
                        </Grid>
                        <Grid container justifyContent={"flex-end"}>
                            <Button variant={"contained"} onClick={() => {
                                handleClick(game)
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