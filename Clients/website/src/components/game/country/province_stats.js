import {Card, CardContent, CardHeader, List, ListItem} from "@mui/material";
import {Block, Check} from "@mui/icons-material";
import * as React from "react";

export default function Province_stats({country}){
    if (typeof country === "undefined") return (
        <div>
            <Card>
                <CardHeader title={"Province Statistic"}/>
                <CardContent>
                    No Data
                </CardContent>
            </Card>
        </div>
    )
    return (
        <div>
            <Card>
                <CardHeader title={"Province Statistic"}/>
                <CardContent>
                    <List>
                        <ListItem>
                            Average Moral: {country["morale"]} %
                        </ListItem>
                        <ListItem>
                            Provinces: {country["total_provinces"]}
                        </ListItem>
                        <ListItem>
                            Cities: {country["total_cities"]}
                        </ListItem>
                        <ListItem>
                            Annexed Cities: {country["total_annexed_cities"]}
                        </ListItem>
                        <ListItem>
                            Total: {country["total"]}
                        </ListItem>
                    </List>
                </CardContent>
            </Card>
        </div>
    )
}