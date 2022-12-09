import * as React from "react";
import {Card, CardContent, CardHeader, Grid,Typography} from "@mui/material";

export default function ProductionBar({weapons}){
    if (!!weapons && weapons.length === 0){
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
    return (
        <div>
            <Card>
                <CardHeader
                    title={"Minimum Production"}
                />
                <CardContent>
                    <Grid container direction={"row"} spacing={4} width={"100%"}>
                        {Object.values(weapons).map((research) => {
                            return (
                                <Grid item key={research["wtyp"]}>
                                    <img alt={research["wtyp"]} src={require(`../../../../images/researches/${research["wtyp"]}.png`)} height={200}/>
                                    <Typography color={"black"} sx={{
                                        width: 30,
                                        border: 3,
                                        borderRadius: 5,
                                        position: "relative",
                                        bottom: 40,
                                        left: 15,
                                        paddingLeft: 0.2,
                                    }}>
                                        {research["count"]}
                                    </Typography>
                                </Grid>
                            )
                        })}
                    </Grid>
                </CardContent>
            </Card>
        </div>
    )
}