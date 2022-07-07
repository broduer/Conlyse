import React from 'react';
import {Box, List, ListItem, Typography} from "@mui/material";

export default function Countryranking({countrys}){
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
                        {sorted_countrys.indexOf(country)+1}. {country["cn"]}: {country["vp"]}
                    </ListItem>
                )))}
            </List>
        </Box>
    )
}
