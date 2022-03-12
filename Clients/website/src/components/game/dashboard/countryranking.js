import React from 'react';
import {Box, List, ListItem, ListItemText, ListSubheader, Typography} from "@mui/material";
import {Star} from "@mui/icons-material";

export default function Countryranking({countrys}){
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
                {Object.values(countrys).slice(0,10).map((country => (
                    <ListItem key={country.country_id} sx={{m:0}}>
                        {countrys.indexOf(country)+1}. {country.country_name}: {country.victory_points}
                    </ListItem>
                )))}
            </List>
        </Box>
    )
}
