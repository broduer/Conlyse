import {useParams} from "react-router-dom";
import React from "react";
import ProductionBar from "./country/productionBar";
import {getResearches} from "../../../helper/country/ResearchGetter";
import CustomDrawer from "../../CustomDrawer";
import {Card, CardContent, CircularProgress, Grid, Typography} from "@mui/material";
import Basicinformation from "./country/basicinformation";
import Province_stats from "./country/province_stats";
import Economy_stats from "./country/economy_stats";
import getRisingPowers from "../../../helper/dashboard/RisingPowersGetter";
import Risingpower from "./dashboard/risingpower";
import {useQueries, useQuery} from "react-query";
import {getDifference} from "../../../helper/time";
import * as api from "../../../helper/api";


export default function Country(){
    const {game_id, country_id} = useParams()
    const {data} = useQuery(["game", game_id], () => api.getGame(game_id), {keepPreviousData : true});
    let defined = data ? data[game_id] : undefined;
    let game = {};
    let day = 0;

    if(!!defined){
        game = data[game_id]
        day = getDifference(game["st"], game["ct"], "D")
    }
    let results = useQueries([
        { queryKey: ['countrys', game["gid"], "normal", "-1", "-1"], queryFn: () => api.getCountrys(game["gid"], "normal", "-1", "-1"), enabled: !!defined},
        { queryKey: ['countrys', game["gid"], "production", country_id, day], queryFn: () => api.getCountrys(game["gid"], "production", country_id, day), enabled: !!defined},
        { queryKey: ['countrys', game["gid"], "rising_power", "-1", day], queryFn: () => api.getCountrys(game["gid"], "rising_power", "-1", day), enabled: !!defined},
        { queryKey: ['countrys', game["gid"], "stats", country_id, day], queryFn: () => api.getCountrys(game["gid"], "stats", country_id, day), enabled: !!defined},
    ])



    let country;
    if (!results[0].isLoading && !!defined) {
        country = results[0]["data"][country_id]
        if (!results[1].isLoading) country = Object.assign(country, results[1]["data"][country_id])
        if (!results[2].isLoading) country = Object.assign(country, results[2]["data"][country_id])
        if (!results[3].isLoading) country = Object.assign(country, results[3]["data"][country_id])
    }
    if (results[0].isLoading || !defined) return <div>Loading</div>
    let keys  = Object.keys(country)
    return (
        <div>
            <CustomDrawer game_id={game["gid"]}>
                <Typography variant={"h3"}>
                    {!results[0].isLoading ? country["cn"] : <CircularProgress/>}
                </Typography>
                <Grid container columns={4} rowSpacing={6} columnSpacing={4}>
                    <Grid item xs={4} md={2}>
                        <Basicinformation country={country}/>
                    </Grid>
                    <Grid item xs={4} md={2}>
                        {results[3].isSuccess && keys.includes("ts") ? <Province_stats country={country["ts"][game["ct"]]}/> : <CircularProgress/>}
                    </Grid>
                    <Grid item xs={4}>
                        {results[3].isSuccess ? <Economy_stats country={country} game={game}/> : <CircularProgress/> }
                    </Grid>
                    <Grid item xs={4} width={"100%"}>
                        <Card sx={{width:"100%"}}>
                            <CardContent sx={{width:"100%"}}>
                                {(results[2].isSuccess && keys.includes("ts")) ? <Risingpower country={getRisingPowers([country], game)[0]} number={country["rspos"] + 1}/> : <CircularProgress/>}
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={4}>
                        {results[1].isSuccess ? <ProductionBar weapons={getResearches(country["prd"])} /> : <CircularProgress/>}
                    </Grid>
                </Grid>
            </CustomDrawer>
        </div>
    )
}