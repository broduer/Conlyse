import {Card, CardContent, CardHeader, List, ListItem} from "@mui/material";
import {Block, Check} from "@mui/icons-material";
import * as React from "react";

export default function Basicinformation({country}){
    return (
        <div>
            <Card>
                <CardHeader title={"Basic Information"}/>
                <CardContent>
                    <List>
                        <ListItem>
                            Player: {country["player_name"]}
                        </ListItem>
                        <ListItem>
                            Team: {Object.keys(country).includes("team") ? country["team"]["name"] : "Unknown"}
                        </ListItem>
                        <ListItem>
                            Computer: {country["computer"] === false ?  <Block color={"error"}/> : <Check color={"success"}/> }
                        </ListItem>
                        <ListItem>
                            Defeated: {country["defeated"] === false ?  <Block color={"error"}/> : <Check color={"success"}/> }
                        </ListItem>
                        <ListItem>
                            Capital: {country["capital_id"] === -1 ?  <Block color={"error"}/> : country["capital"]["name"] }
                        </ListItem>
                    </List>
                </CardContent>
            </Card>
        </div>
    )
}