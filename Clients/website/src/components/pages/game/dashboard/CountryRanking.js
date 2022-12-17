import React from 'react';
import {Box, List, ListItem, Typography} from "@mui/material";
import {Link, NavLink} from "react-router-dom";
import CountryLink from "../../../CountryLink";

export default function CountryRanking({countrys, game}){
    let sorted_countrys = Object.values(countrys)
    sorted_countrys = sorted_countrys.sort((a, b) =>{
        a["vp"] = "vp" in a ? a["vp"] : 0
        b["vp"] = "vp" in b ? b["vp"] : 0
        return b["vp"] - a["vp"]
    })
    return (
        <Box sx={{
            bgcolor: "divider",
            border: 3,
            borderColor: "primary.main",
            borderRadius: 10,
        }}>
            <List sx={{
                lineHeight: 0.75
            }}>
                <Typography variant={"h2"} fontSize={"x-large"} textAlign={"center"} color={"white"} sx={{
                    textDecoration:"underline"
                }}>
                    Country Ranking <br/>
                    by Victory Points
                </Typography>
                {sorted_countrys.slice(0,10).map((country => (
                    <ListItem key={country["cid"]} sx={{m:0}}>
                        {sorted_countrys.indexOf(country)+1}.
                        <CountryLink game_id={game["gid"]} country_id={country["cid"]}>
                            {country["cn"]}</CountryLink>: {country["vp"]}
                    </ListItem>
                )))}
            </List>
        </Box>
    )
}
