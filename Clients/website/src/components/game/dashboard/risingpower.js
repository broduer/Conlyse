import {Grid, Typography} from "@mui/material";
import VictoryGraph from "../components/VictoryGraph";
import React from "react";
import RisingpowerCard from "./risingpowerCard";

export default function Risingpower({country, number}){
    country = country["rising_power_country"]
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
                    <Grid item xs={2} sm={1}>
                        <RisingpowerCard type={"Economy"} data={country["economy"]}/>
                    </Grid>
                    <Grid item xs={2} sm={1}>
                        <RisingpowerCard type={"Victory Points"} data={country["victory_points"]}/>
                    </Grid>
                </Grid>

            </Grid>
        </Grid>
    )
}