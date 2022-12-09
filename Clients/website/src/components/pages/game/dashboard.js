import React from 'react';
import {Grid, Typography} from "@mui/material";
import TeamRanking from "./dashboard/TeamRanking";
import CountryRanking from "./dashboard/CountryRanking";
import {useParams} from "react-router-dom";
import CustomDrawer from "../../CustomDrawer";
import {getDatefromTimestamp, getDifference} from "../../../helper/time";
import GameInformation from "./dashboard/GameInformation";
import DashboardMap from "./dashboard/DashboardMap";
import RisingPowersCarousel from "./dashboard/RisingPowersCarousel";
import getRisingPowers from "../../../helper/dashboard/rising_power_getters";
import Trades from "./dashboard/Trades";
import HighValueCities from "./dashboard/HighValueCities";
import {get_combined} from "../../../helper/array_helper";
import {useQueries, useQuery} from "react-query";
import * as api from "../../../helper/api";
import {get_teams_by_vp} from "../../../helper/staticinformation";
import getHighValueCities from "../../../helper/dashboard/high_value_cities_getter";
import getTrades from "../../../helper/dashboard/trades_getter";
import CircularProgressWithLabel from "../../CircularProgressWithLabel";

export default function Dashboard(){
    const {game_id} = useParams()
    const {data: game, status} = useQuery(["game", game_id], () => api.getGame(game_id));
    if (status === "loading") {return (<div>Loading</div>)}
    else if (status === "error") {return (<div>Error</div>)}
    else {
        return (
            <DashboardDiv game={game[game_id]}/>
        )
    }


}

function DashboardDiv({game}){
    let from_timestamp = game["ct"] - 10 * 3600 * 24
    let results = useQueries([
        { queryKey: ['teams', game.gid], queryFn: () => api.getTeams(game.gid)},
        { queryKey: ['countrys', game.gid, "normal", "-1", "0", "0"], queryFn: () => api.getCountrys(game.gid, "normal", "-1", "0", "0")},
        { queryKey: ['countrys', game.gid, "stats", "-1", from_timestamp, game["ct"]], queryFn: () => api.getCountrys(game.gid, "stats", "-1", game["ct"], game["ct"])},
        { queryKey: ['countrys', game.gid, "rising_power", "0", "0", "0"], queryFn: () => api.getCountrys(game.gid, "rising_power", "-1","0", "0")},
        { queryKey: ['trades', game.gid], queryFn: () => api.getTrades(game.gid)},
        { queryKey: ['provinces', game.gid, "normal", "0"], queryFn: () => api.getProvinces(game.gid, "normal", "0")},
        { queryKey: ['provinces', game.gid, "value", "0"], queryFn: () => api.getProvinces(game.gid, "value", "0")},
        { queryKey: ['static_provinces', game.mid], queryFn: () => api.getStaticProvinces(game.mid)},
        { queryKey: ['static_upgrades'], queryFn: api.getStaticUpgrades},
    ])
    // Does the queries for the podium of rising power countries
    let countrys_rising_power_podium = [{"cid": 0, "pos": 1}, {"cid": 1, "pos":2}, {"cid": 2, "pos": 3}]
    if (results[3].isSuccess){
        countrys_rising_power_podium = Object.values(results[3]["data"]).sort(function(first, second) {
            return first["rs_pos"] - second["rs_pos"];
        })}
    let queries = []
    for (let i = 0; i < 3; i++){
        queries.push(
            { queryKey: ['countrys', game.gid, "stats", countrys_rising_power_podium[i]["cid"], "-1"],
                queryFn: () => api.getCountrys(game.gid, "stats", countrys_rising_power_podium[i]["cid"], from_timestamp, game["ct"]),
                enabled: countrys_rising_power_podium.length !== 3
            },
         )
    }
    const countrys_rising_power_queries = useQueries(queries)
    results = results.concat(countrys_rising_power_queries)
    const isLoading = results.some(query => query.isLoading)
    const isError = results.some(query => query.isError)
    const isFetching = results.some(query => query.isFetching)
    let loaded = results.reduce((current, query) => {
        return current + +query.isSuccess
    }, 0)


    if (isLoading){
        return (<CircularProgressWithLabel value={(loaded / 12) * 100}/>)
    }else if (isFetching){
        return (<div>Refreshing</div>)
    }
    else if (isError){
        return (<div>Error</div>)
    }
    const teams = results[0]["data"]
    const countrys = results[1]["data"]
    const countrys_stats = results[2]["data"]
    const countrys_rising_power = results[3]["data"]
    const trades = results[4]["data"]
    const provinces = results[5]["data"]
    const provinces_value = results[6]["data"]
    const static_provinces = results[7]["data"]
    const static_upgrades = results[8]["data"]

    const combined_countrys = get_combined(
        [Object.values(countrys_rising_power), Object.values(countrys), Object.values(countrys_stats),
        Object.values(results[9]["data"]), Object.values(results[10]["data"]), Object.values(results[11]["data"])],
        "cid")
    for (let country in combined_countrys){
        if ("ts" in combined_countrys[country]) {
            combined_countrys[country]["vp"] =
                combined_countrys[country]["ts"][Object.keys(combined_countrys[country]["ts"])[Object.keys(combined_countrys[country]["ts"]).length-1]]["vp"]
        }
    }
    const combined_provinces = get_combined([Object.values(provinces), Object.values(static_provinces)], "plid")
    const combined_provinces_value = get_combined([provinces_value, Object.values(static_provinces)], "plid")

    return(
        <CustomDrawer game_id={game["gid"]}>
            <div style={{margin: 20}}>
                <Grid container direction="row" columns={16} sx={{
                    width:"100%",
                    minHeight: 40,
                    border: 3,
                    borderRadius: 30,
                    borderColor: "primary.main",
                    alignItems:"center",
                    justifyContent:"center",
                }}>
                    <Grid item xs={4} sm={2} sx={{
                        maxHeight:"10vh",
                    }}>
                        <Typography>
                            Day: {getDifference(game["st"], game["ct"], "D")}
                        </Typography>
                    </Grid>
                    <Grid item xs={6} sm={4} >
                        <Typography>
                            Time: {getDatefromTimestamp(game["ct"], "h:m:s")}
                        </Typography>
                    </Grid>
                    <Grid item xs={6} sm={4} >
                        <Typography>
                            Game ID: {game["gid"]}
                        </Typography>
                    </Grid>
                    <Grid item xs={16} sm={6}>
                        <Typography textAlign={"end"}>
                            Next Heal Time: {getDatefromTimestamp(game["nht"], "h:m")}
                        </Typography>
                    </Grid>
                </Grid>
                <Grid container columns={12} spacing={2} sx={{
                    mt: 0.5,
                }}>
                    <Grid item xs={12} lg={2}>
                        <Grid container columns={6} columnSpacing={1} rowSpacing={2}>
                            <Grid item xs={6} sm={2} lg={6} width={"100%"}>
                                <GameInformation game={game}/>
                            </Grid>
                            <Grid item xs={6} sm={2} lg={6} width={"100%"}>
                                <CountryRanking countrys={combined_countrys}/>
                            </Grid>
                            <Grid item xs={6} sm={2} lg={6} width={"100%"}>
                                <TeamRanking teams={get_teams_by_vp(teams, combined_countrys)}/>
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item xs={12} lg={7}>
                        <Grid container rowSpacing={2}>
                            <Grid item width={"100%"}>
                                <DashboardMap provinces={combined_provinces}/>
                            </Grid>
                            <Grid item width={"100%"}>
                                <RisingPowersCarousel rising_powers_countrys={getRisingPowers(combined_countrys, game)}/>
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item xs={12} lg={3}>
                        <Grid container rowSpacing={2}>
                            <Grid item xs={12} minHeight={300}>
                                <HighValueCities cities={getHighValueCities(combined_provinces_value, countrys, static_upgrades)} />
                            </Grid>
                            <Grid item xs={12} minHeight={300}>
                                <Trades trades={getTrades(trades, countrys, game)}/>
                            </Grid>
                        </Grid>
                    </Grid>
                </Grid>
            </div>
        </CustomDrawer>
    )
}

