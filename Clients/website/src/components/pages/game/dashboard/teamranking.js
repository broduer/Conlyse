import React from 'react';
import {List, ListItem, Typography, Box} from "@mui/material";

export default function Teamranking({teams}){
    return (
        <Box sx={{
            bgcolor: "divider",
            border: 3,
            borderColor: "primary.main",
            borderRadius: 10,
        }}>
            <List sx={{
                lineHeight:0.75
            }}>
                <Typography variant={"h2"} fontSize={"x-large"} textAlign={"center"} color={"white"} sx={{
                    textDecoration:"underline",
                }}>
                    Teams Ranking <br/>
                    by Victory Points
                </Typography>
                {teams.slice(0,5).map((team => (
                    <ListItem key={team["utid"]}>
                        {teams.indexOf(team)+1}. {team["tn"]}: {team["vp"]}
                    </ListItem>
                )))}
            </List>
        </Box>
    )
}
