import {Card, CardContent, CardHeader, List, ListItem} from "@mui/material";
import * as React from "react";

export default function Province_stats({country}){
    if(typeof country === "undefined"){
        country = {
            "ml": 0,
            "t_p": 0,
            "t_c": 0,
            "t_ac": 0,
            "t_pc": 0,
        }
    }
    return (
        <Card>
            <CardHeader title={"Province Statistic"}/>
            <CardContent>
                <List>
                    <ListItem>
                        Average Moral: {country["ml"]} %
                    </ListItem>
                    <ListItem>
                        Provinces: {country["t_p"]}
                    </ListItem>
                    <ListItem>
                        Cities: {country["t_c"]}
                    </ListItem>
                    <ListItem>
                        Annexed Cities: {country["t_ac"]}
                    </ListItem>
                    <ListItem>
                        Total: {country["t_pc"]}
                    </ListItem>
                </List>
            </CardContent>
        </Card>
    )
}