import * as React from "react";
import {Card, CardContent, CardHeader, Grid, Paper, Typography} from "@mui/material";

export default function Reseachbar({researches}){
    if (researches.length === 0){
        return (
            <div>
                <Card>
                    <CardHeader
                        title={"Minimum Research"}
                    />
                    <CardContent>
                        No Research Detected
                    </CardContent>
                </Card>
            </div>
        )
    }
    console.log(researches)
    return (
        <div>
            <Card>
                <CardHeader
                    title={"Minimum Research"}
                />
                <CardContent>
                    <Grid container direction={"row"} spacing={4} width={"100%"}>
                        {Object.values(researches).map((research) => {
                            console.log(research)
                            return (
                                <Grid item key={research}>
                                    <img src={require(`../../../images/researches/${research}.png`)} height={200}/>
                                </Grid>
                            )
                        })}
                    </Grid>
                </CardContent>
            </Card>
        </div>
    )
}