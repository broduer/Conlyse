import * as React from "react";
import {Card, CardContent, CardHeader, Grid,Typography} from "@mui/material";
import {get_research_image} from "../../../../helper/country/research_getter";

export default function ResearchBar({country}){
    if (!Object.keys(country).includes("rs") || country["rs"].length===0){
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
                    title={"Minimum Research"}
                />
                <CardContent>
                    <Grid container direction={"row"} spacing={4} width={"100%"}>
                        {Object.values(country["rs"]).map((research) => {
                            return (
                                <Grid item key={research["usrid"]}>
                                    <img src={`/researches/${get_research_image(research["rscid"])}.png`} height={200}/>
                                    <Typography color={"black"} sx={{
                                        position: "relative",
                                        bottom: 40,
                                        left: 15,
                                        paddingLeft: 0.2,
                                    }}>
                                        {research["wn"]}
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