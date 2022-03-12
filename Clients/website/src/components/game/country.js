import {useParams} from "react-router-dom";
import {useCountry, useGame} from "./useLoad";
import React from "react";
import Reseachbar from "./country/reseachbar";
import {getResearches} from "../../helper/country/ResearchGetter";
import CustomDrawer from "../CustomDrawer";
import {Card, CardContent, Grid, Typography} from "@mui/material";
import Basicinformation from "./country/basicinformation";
import Province_stats from "./country/province_stats";
import Economy_stats from "./country/economy_stats";
import getRisingPowers from "../../helper/dashboard/RisingPowersGetter";
import RisingpowerCard from "./dashboard/risingpowerCard";
import Risingpower from "./dashboard/risingpower";

export default function Country(){
    const {game_id, country_id} = useParams()
    const {datas, loading} = useGame(game_id)
    if (loading){
        return (
            <div>
                Loading
            </div>
        )
    }else {
        return (
            <CountryDiv game={datas["game"].data[0]} scenario={datas["scenario"].data[datas["game"].data[0]["scenario_id"]]} country_id={country_id}/>
        )
    }
}

function CountryDiv({game, scenario, country_id}){
    const {datas, loading} = useCountry(game, scenario, country_id)
    if (loading) {
        return (
            <div>
                Loading
            </div>
        )
    }

    let country = datas["countrys"]["data"][country_id]
    if (country["team_id"] !== null){
        country["team"] = datas["teams"]["data"][country["team_id"]]
    }
    if (country["capital_id"] !== -1){
        country["capital"] = Object.values(datas["static_provinces"]["data"]).filter((static_province) => static_province["province_location_id"] === country["capital_id"])[0]
    }
    country["province_stats"] = datas["countrys_stats"]["data"][country_id]
    country["economy"] = datas["countrys_adv"]["data"][country_id + "_" + game["current_time"]]
    const rising_powers = Object.values(getRisingPowers(datas["countrys"]["data"], datas["countrys_adv"]["data"], game["start_time"], game["current_time"]))
    let rising_power_place = rising_powers.map(function (e) {
        return parseInt(e["country_id"]);
    }).indexOf(parseInt(country_id));
    country["rising_power_country"] = rising_powers[rising_power_place]
    country["researches"] = getResearches(datas["countrys_rs"]["data"][country_id])
    return (
        <div>
            <CustomDrawer game_id={game["game_id"]}>
                <Typography variant={"h1"}>
                    {country["country_name"]}
                </Typography>
                <Grid container columns={4} rowSpacing={6} columnSpacing={4}>
                    <Grid item xs={4} md={2}>
                        <Basicinformation country={country}/>
                    </Grid>
                    <Grid item xs={4} md={2}>
                        <Province_stats country={country["province_stats"]}/>
                    </Grid>
                    <Grid item xs={4} width={"100%"}>
                        <Economy_stats country={country["economy"]} rising_power={country["rising_power_country"]}/>
                    </Grid>
                    <Grid item xs={4} width={"100%"}>
                        <Card sx={{width:"100%"}}>
                            <CardContent sx={{width:"100%"}}>
                                <Risingpower country={country} number={rising_power_place + 1}/>
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={4}>
                        <Reseachbar researches={country["researches"]}/>
                    </Grid>
                </Grid>
            </CustomDrawer>
        </div>
    )
}