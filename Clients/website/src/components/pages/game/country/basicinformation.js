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
                            Player: {country["pyn"]}
                        </ListItem>
                        <ListItem>
                            Team: {Object.keys(country).includes("team") ? country["team"]["name"] : "Unknown"}
                        </ListItem>
                        <ListItem>
                            Computer: {country["cp"] === false ?  <Block color={"error"}/> : <Check color={"success"}/> }
                        </ListItem>
                        <ListItem>
                            Defeated: {country["df"] === false ?  <Block color={"error"}/> : <Check color={"success"}/> }
                        </ListItem>
                    </List>
                </CardContent>
            </Card>
        </div>
    )
}