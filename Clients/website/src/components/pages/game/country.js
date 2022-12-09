import {useParams} from "react-router-dom";
import React from "react";
import CustomDrawer from "../../CustomDrawer";
import {Card, CardContent, CircularProgress, Grid, Typography} from "@mui/material";
import BasicInformation from "./country/BasicInformation";
import ProvinceStats from "./country/ProvinceStats";
import EconomyStats from "./country/EconomyStats";
import getRisingPowers from "../../../helper/dashboard/rising_power_getters";
import RisingPower from "./dashboard/RisingPower";
import {useQueries, useQuery} from "react-query";
import * as api from "../../../helper/api";


export default function Country(){
    const {game_id, country_id} = useParams()
    const {data} = useQuery(["game", game_id], () => api.getGame(game_id), {keepPreviousData : true});
    let defined = data ? data[game_id] : undefined;
    let game = {};

    if(!!defined){
        game = data[game_id]
    }
    let results = useQueries([
        { queryKey: ['countrys', game["gid"], "normal", "-1", "0", "0"], queryFn: () => api.getCountrys(game["gid"], "normal", "-1", "0", "0"), enabled: !!defined},
        { queryKey: ['countrys', game["gid"], "rising_power", "-1", game["ct"], game["ct"]], queryFn: () => api.getCountrys(game["gid"], "rising_power", "-1", game["ct"], game["ct"]), enabled: !!defined},
        { queryKey: ['countrys', game["gid"], "stats", country_id, game["st"], game["ct"]], queryFn: () => api.getCountrys(game["gid"], "stats", country_id, game["st"], game["ct"]), enabled: !!defined},
    ])



    let country;
    if (!results[0].isLoading && !!defined) {
        country = results[0]["data"][country_id]
        if (!results[1].isLoading) country = Object.assign(country, results[1]["data"][country_id])
        if (!results[2].isLoading) country = Object.assign(country, results[2]["data"][country_id])
    }
    if (results[0].isLoading || !defined) return <div>Loading</div>
    let keys  = Object.keys(country)
    return (
        <CustomDrawer game_id={game["gid"]}>
            <Typography variant={"h3"}>
                {!results[0].isLoading ? country["cn"] : <CircularProgress/>}
            </Typography>
            <Grid container columns={4} rowSpacing={6} columnSpacing={4}>
                <Grid item xs={4} md={2}>
                    <BasicInformation country={country}/>
                </Grid>
                <Grid item xs={4} md={2}>
                    {results[2].isSuccess && keys.includes("ts") ? <ProvinceStats country={country["ts"][game["ct"]]}/> : <CircularProgress/>}
                </Grid>
                <Grid item xs={4}>
                    {results[2].isSuccess ? <EconomyStats country={country} game={game}/> : <CircularProgress/> }
                </Grid>
                <Grid item xs={4} width={"100%"}>
                    <Card sx={{width:"100%"}}>
                        <CardContent sx={{width:"100%"}}>
                            {(results[2].isSuccess && keys.includes("ts")) ? <RisingPower country={getRisingPowers([country], game)[0]} number={country["rs_pos"] + 1}/> : <CircularProgress/>}
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </CustomDrawer>
    )
}