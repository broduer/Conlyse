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
import {get_combined} from "../../../helper/array_helper";
import LoadingPage from "../LoadingPage";
import {getResearches} from "../../../helper/country/research_getter";
import ResearchBar from "./country/ResearchBar";


export default function Country(){
    const {game_id, country_id} = useParams()
    const {data} = useQuery(["game", game_id], () => api.get_game(game_id), {keepPreviousData : true});
    let defined = data ? data[game_id] : undefined;
    let game = {};

    if(!!defined){
        game = data[game_id]
    }
    let results = useQueries([
        { queryKey: ['countrys', game["gid"], "normal", country_id, "0", "0"], queryFn: () => api.get_countrys(game["gid"], "normal", country_id, "0", "0"), enabled: !!defined},
        { queryKey: ['countrys', game["gid"], "rising_power", country_id, game["ct"], game["ct"]], queryFn: () => api.get_countrys(game["gid"], "rising_power", country_id, game["ct"], game["ct"]), enabled: !!defined},
        { queryKey: ['countrys', game["gid"], "stats", country_id, game["st"], game["ct"]], queryFn: () => api.get_countrys(game["gid"], "stats", country_id, game["st"], game["ct"]), enabled: !!defined},
        { queryKey: ['countrys', game["gid"], "research", country_id, game["st"], game["ct"]], queryFn: () => api.get_countrys(game["gid"], "research", country_id, game["st"], game["ct"]), enabled: !!defined},
         { queryKey: ["static_warfare_types"], queryFn: () => api.get_static_warfare_types()},
    ])


    const isError = results.some(query => query.isError)
    const isLoading = results.some(query => query.isLoading)

    if (isLoading || !defined) return (<LoadingPage game_id={game["gid"]}/>)
    else if (isError) return <div>Error</div>
    let country = get_combined([Object.values(results[0].data), Object.values(results[1].data),
        Object.values(results[2].data), Object.values(getResearches(results[3].data, Object.values(results[4].data)))], "cid")[country_id]
    let last_ts = Object.keys(country["ts"])[Object.keys(country["ts"]).length-1]
    return (
        <CustomDrawer game_id={game["gid"]}>
            <Typography variant={"h3"}>
                {country["cn"]}
            </Typography>
            <Grid container columns={4} rowSpacing={6} columnSpacing={4}>
                <Grid item xs={4} md={2}>
                    <BasicInformation country={country}/>
                </Grid>
                <Grid item xs={4} md={2}>
                    <ProvinceStats country={country["ts"][last_ts]}/>
                </Grid>
                <Grid item xs={4}>
                    <EconomyStats country={country} game={game} last_ts={last_ts}/>
                </Grid>
                <Grid item xs={4} width={"100%"}>
                    <Card sx={{width:"100%"}}>
                        <CardContent sx={{width:"100%"}}>
                            <RisingPower game={game} country={getRisingPowers([country], game)[0]} number={country["rs_pos"] + 1}/>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={4}>
                    <ResearchBar country={country}/>
                </Grid>
            </Grid>
        </CustomDrawer>
    )
}