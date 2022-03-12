import {Card, CardContent, CardHeader, Grid, List, ListItem} from "@mui/material";
import {Block, Check} from "@mui/icons-material";
import * as React from "react";
import VictoryGraph from "../components/VictoryGraph";
import EconomyGraph from "../components/EconomyGraph";

export default function Economy_stats({country, rising_power}){
    if (typeof country === "undefined" || typeof rising_power === "undefined") return (
        <div>
            <Card>
                <CardHeader title={"Economy Statistic"}/>
                <CardContent>
                    No Data
                </CardContent>
            </Card>
        </div>
    )
    return (
        <div>
            <Grid container columns={2} columnSpacing={4}>
                <Grid item xs={2} md={1}>
                   <Card>
                       <CardHeader title={"Economy Statistic"}/>
                       <CardContent>
                           <List>
                               <ListItem>
                                   Supplies: {country["2"]} pro D / {(country["2"] / 24).toFixed(1)} pro h
                               </ListItem>
                               <ListItem>
                                   Components: {country["3"]} pro D / {(country["3"] / 24).toFixed(1)} pro h
                               </ListItem>
                               <ListItem>
                                   Fuel: {country["6"]} pro D / {(country["6"] / 24).toFixed(1)} pro h
                               </ListItem>
                               <ListItem>
                                   Electronics: {country["7"]} pro D / {(country["7"] / 24).toFixed(1)} pro h
                               </ListItem>
                               <ListItem>
                                   Rare Materials: {country["5"]} pro D / {(country["5"] / 24).toFixed(1)} pro h
                               </ListItem>
                               <ListItem>
                                   Money: {country["21"]} pro D / {(country["21"] / 24).toFixed(1)} pro h
                               </ListItem>
                               <ListItem>
                                   Total: {country["total"]} pro D / {(country["total"] / 24).toFixed(1)} pro h
                               </ListItem>
                           </List>
                       </CardContent>
                   </Card>
                </Grid>
                <Grid item xs={2} md={1}>
                    <Card>
                        <CardContent>
                            <EconomyGraph economy_data={rising_power}/>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </div>
    )
}