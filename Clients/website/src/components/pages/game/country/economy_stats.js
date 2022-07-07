import {Card, CardContent, CardHeader, Grid, List, ListItem} from "@mui/material";
import * as React from "react";
import EconomyGraph from "./EconomyGraph";
import getTotalEconomy, {getGraphData} from "../../../../helper/country/EconomyGetter";
import {getDifference} from "../../../../helper/time";
import {getResourceName} from "../../../../helper/gameTypes";

export default function Economy_stats({country, game}){
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
        "2": 0,
        "3": 0,
        "5": 0,
        "6": 0,
        "7": 0,
        "21": 0,
        "trp": 0,
    };
    if (Object.keys(country["ts"]).includes(game["ct"].toString())){
        current_country = country["ts"][game["ct"]]
    }
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