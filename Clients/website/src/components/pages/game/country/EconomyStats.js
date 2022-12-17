import {Card, CardContent, CardHeader, Grid, List, ListItem} from "@mui/material";
import * as React from "react";
import EconomyGraph from "./EconomyGraph";
import getTotalEconomy, {getGraphData} from "../../../../helper/country/economy_getter";
import {getDifference} from "../../../../helper/time";
import {getResourceName} from "../../../../helper/game_types";

export default function EconomyStats({country, game, last_ts}){
    if (typeof country === "undefined") return (
        <div>
            <Card>
                <CardHeader title={"Economy Statistic"}/>
                <CardContent>
                    No Data
                </CardContent>
            </Card>
        </div>
    )
    let current_country = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "20": 0,
        "trp": 0,
    };
    current_country = country["ts"][last_ts]
    let total_country = getTotalEconomy(country, game)
    country = getGraphData(country, game)
    let days = getDifference(game["st"], game["ct"], "D") + 1
    return (
        <Grid container columns={2} columnSpacing={4} rowSpacing={6}>
            <Grid item xs={2} md={1}>
               <Card>
                   <CardHeader title={"Economy Statistic - Last Day"} />
                   <CardContent>
                       <List>
                           {Object.keys(current_country).map((key) => {
                               let am = current_country[key]
                               let name = getResourceName(key)
                               if (name){
                                   return (
                                       <ListItem key={key}>
                                           {name}: {am.toFixed()} per Day / {(am/days).toFixed(1)} per Hour
                                       </ListItem>
                                   )
                               }
                           })}
                       </List>
                   </CardContent>
               </Card>
            </Grid>
            <Grid item xs={2} md={1}>
                <Card>
                    <CardHeader title={"Economy Statistic - Entire Game"} />
                    <CardContent>
                        <List>
                            {Object.keys(total_country).map((key) => {
                                let am = total_country[key]
                                let name = getResourceName(key)
                                if (name){
                                    return (
                                        <ListItem key={key}>
                                            {name}: {am.toFixed()} Total / {(am/days).toFixed(1)} per Day
                                        </ListItem>
                                    )
                                }
                            })}
                        </List>
                    </CardContent>
                </Card>
            </Grid>
            <Grid item xs={2}>
                <Card>
                    <CardHeader title={"Economy - Graph"}/>
                    <CardContent>
                        <EconomyGraph country={country}/>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
    )
}