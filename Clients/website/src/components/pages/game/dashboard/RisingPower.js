import {Grid, Typography} from "@mui/material";
import VictoryGraph from "../country/VictoryGraph";
import React from "react";
import RisingPowerCard from "./RisingPowerCard";

export default function RisingPower({country, number}){
    return (
        <Grid container direction={"row"} columns={2}>
            <Grid item xs={2} lg={1}>
                <Grid container>
                    <Grid item>
                        <Typography variant={"h2"} fontSize={"x-large"} color={"white"} sx={{
                            textDecoration:"underline",
                            lineHeight: 0.75,
                            mt: 1,
                            ml: 2,
                        }}>
                            Rising Powers
                        </Typography>
                    </Grid>
                    <Grid item width={"100%"}>
                        <VictoryGraph victory_data={country}/>
                    </Grid>
                </Grid>
            </Grid>
            <Grid item xs={2} lg={1}>
                <Typography fontSize={"larger"}>
                    {number}. {country.name}
                </Typography>
                <Grid container columns={2} columnSpacing={1} mt={0.5}>
                    <Grid item xs={2} sm={2}>
                        <RisingPowerCard type={"Economy"} data={country["trp"]}/>
                    </Grid>
                    <Grid item xs={2} sm={2}>
                        <RisingPowerCard type={"Victory Points"} data={country["vps"]}/>
                    </Grid>
                </Grid>

            </Grid>
        </Grid>
    )
}