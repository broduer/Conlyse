import React from 'react';
import {Grid, Typography} from "@mui/material";
import Teamranking from "./dashboard/teamranking";
import {
    getTeamsbyVP,
    getcurrent_provinces,
    getCountrysByTimestamp,
} from "../../helper/staticinformation";
import Countryranking from "./dashboard/countryranking";
import {useLocation, useParams} from "react-router-dom";
import CustomDrawer from "../CustomDrawer";
import {getDatefromTimestamp, getDifference} from "../../helper/time";
import {useDashboard, useGame} from "./useLoad";
import Gameinformation from "./dashboard/gameinformation";
import Map from "./dashboard/map";
import Risingpowers from "./dashboard/risingpowers";
import getRisingPowers from "../../helper/dashboard/RisingPowersGetter";
import Trades from "./dashboard/trades";
import HighvalueCities from "./dashboard/highvalueCities";
import {getCombinedProvinces} from "../../helper/dashboard/CombinedProvinces";

export default function Dashboard(){
    const {game_id} = useParams()
    const {datas, loading} = useGame(game_id)
    if (loading){
        return (
            <div>
                Loading
            </div>
        )
    }else {
        return (
            <DashboardDiv game={datas["game"].data[0]} scenario={datas["scenario"].data[datas["game"].data[0]["scenario_id"]]}/>
        )
    }


}

function DashboardDiv({game, scenario}){
    const {datas, loading} = useDashboard(game, scenario)

    if (loading){
        return (<div>
            Loading
        </div>)
    }

    const provinces = datas["provinces"].data
    const static_provinces = datas["static_provinces"].data
    const trades = datas["trades"].data
    const highvaluecities = datas["provinces_buildings"].data
    const upgrades = datas["upgrades"].data
    const current_provinces = getcurrent_provinces(provinces, game["current_time"])
    const countrys = getCountrysByTimestamp(datas["countrys"].data, current_provinces)
    const teams = getTeamsbyVP(datas["teams"].data, countrys)
    const rising_powers_countrys = getRisingPowers(datas["countrys"].data, datas["countrys_adv"].data, game["start_time"], game["current_time"])
    const combined_provinces = getCombinedProvinces(static_provinces, current_provinces)

    return(
        <div>
            <CustomDrawer game_id={game["game_id"]}>
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
                            Day: {getDifference(game["start_time"], game["current_time"], "D")}
                        </Typography>
                    </Grid>
                    <Grid item xs={6} sm={4} >
                        <Typography>
                            Time: {getDatefromTimestamp(game["current_time"], "h:m:s")}
                        </Typography>
                    </Grid>
                    <Grid item xs={6} sm={4} >
                        <Typography>
                            Game ID: {game["game_id"]}
                        </Typography>
                    </Grid>
                    <Grid item xs={16} sm={6}>
                        <Typography textAlign={"end"}>
                            Next Heal Time: {getDatefromTimestamp(game["next_heal_time"], "h:m")}
                        </Typography>
                    </Grid>
                </Grid>
                <Grid container columns={12} spacing={2} sx={{
                    mt: 0.5,
                }}>
                    <Grid item xs={12} lg={2}>
                        <Grid container columns={6} columnSpacing={1} rowSpacing={2}>
                            <Grid item xs={6} sm={2} lg={6} width={"100%"}>
                                <Gameinformation game={game} scenario={scenario}/>
                            </Grid>
                            <Grid item xs={6} sm={2} lg={6} width={"100%"}>
                                <Countryranking countrys={countrys}/>
                            </Grid>
                            <Grid item xs={6} sm={2} lg={6} width={"100%"}>
                                <Teamranking teams={teams}/>
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item xs={12} lg={7}>
                        <Grid container rowSpacing={2}>
                            <Grid item width={"100%"}>
                                <Map static_provinces={combined_provinces}/>
                            </Grid>
                            <Grid item width={"100%"}>
                                <Risingpowers rising_powers_countrys={rising_powers_countrys}/>
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item xs={12} lg={3}>
                        <Grid container rowSpacing={2}>
                            <Grid item width={"100%"} minHeight={300}>
                                <HighvalueCities cities={highvaluecities} countrys={datas["countrys"].data}/>
                            </Grid>
                            <Grid item width={"100%"} minHeight={300}>
                                <Trades trades={trades} countrys={datas["countrys"].data} game={game} speed={scenario["speed"]}/>
                            </Grid>
                        </Grid>
                    </Grid>
                </Grid>
            </CustomDrawer>
        </div>
    )
}

