import React from 'react';
import {Grid, Typography} from "@mui/material";
import Teamranking from "./dashboard/teamranking";
import Countryranking from "./dashboard/countryranking";
import {useParams} from "react-router-dom";
import CustomDrawer from "../../CustomDrawer";
import {getDatefromTimestamp, getDifference} from "../../../helper/time";
import Gameinformation from "./dashboard/gameinformation";
import Map from "./dashboard/Map/map";
import Risingpowers from "./dashboard/risingpowers";
import getRisingPowers from "../../../helper/dashboard/RisingPowersGetter";
import Trades from "./dashboard/trades";
import HighvalueCities from "./dashboard/highvalueCities";
import {getCombined} from "../../../helper/CombinedArray";
import {useQueries, useQuery} from "react-query";
import * as api from "../../../helper/api";
import {getTeamsbyVP} from "../../../helper/staticinformation";
import getHighValueCities from "../../../helper/dashboard/HighValueCitiesGetter";
import getTrades from "../../../helper/dashboard/TradesGetter";

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
    const day = getDifference(game.st, game.ct, "D")
    const results = useQueries([
        { queryKey: ['teams', game.gid], queryFn: () => api.getTeams(game.gid)},
        { queryKey: ['countrys', game.gid, "normal", "-1", "-1"], queryFn: () => api.getCountrys(game.gid, "normal", "-1", "-1")},
        { queryKey: ['countrys', game.gid, "stats", "-1", day], queryFn: () => api.getCountrys(game.gid, "stats", "-1", day)},
        { queryKey: ['countrys', game.gid, "rising_power", "-1", day], queryFn: () => api.getCountrys(game.gid, "rising_power", "-1",day)},
        { queryKey: ['trades', game.gid], queryFn: () => api.getTrades(game.gid)},
        { queryKey: ['provinces', game.gid, "normal", day], queryFn: () => api.getProvinces(game.gid, "normal", day)},
        { queryKey: ['provinces', game.gid, "value", day], queryFn: () => api.getProvinces(game.gid, "value", day)},
        { queryKey: ['static_provinces', game.mid], queryFn: () => api.getStaticProvinces(game.mid)},
        { queryKey: ['static_upgrades'], queryFn: api.getStaticUpgrades},
    ])
    const isLoading = results.some(query => query.isLoading)
    const isError = results.some(query => query.isError)
    const isFetching = results.some(query => query.isFetching)

    if (isLoading){
        return (<div>Loading</div>)
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

    const combined_countrys = getCombined([Object.values(countrys), Object.values(countrys_stats), Object.values(countrys_rising_power)], "cid")

    const combined_provinces = getCombined([Object.values(provinces), Object.values(static_provinces)], "plid")
    const combined_provinces_value = getCombined([provinces_value, Object.values(static_provinces)], "plid")


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
                                <Gameinformation game={game}/>
                            </Grid>
                            <Grid item xs={6} sm={2} lg={6} width={"100%"}>
                                <Countryranking countrys={combined_countrys}/>
                            </Grid>
                            <Grid item xs={6} sm={2} lg={6} width={"100%"}>
                                <Teamranking teams={getTeamsbyVP(teams, combined_countrys)}/>
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item xs={12} lg={7}>
                        <Grid container rowSpacing={2}>
                            <Grid item width={"100%"}>
                                <Map provinces={combined_provinces}/>
                            </Grid>
                            <Grid item width={"100%"}>
                                <Risingpowers rising_powers_countrys={getRisingPowers(combined_countrys, game)}/>
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item xs={12} lg={3}>
                        <Grid container rowSpacing={2}>
                            <Grid item xs={12} minHeight={300}>
                                <HighvalueCities cities={getHighValueCities(combined_provinces_value, countrys, static_upgrades)} />
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

