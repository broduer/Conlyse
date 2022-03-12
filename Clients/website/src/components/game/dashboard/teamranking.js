import React from 'react';
import {List, ListItem, ListItemText, ListSubheader, Typography, Box} from "@mui/material";
import {Star} from "@mui/icons-material";

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
                {Object.values(teams).slice(0,5).map((team => (
                    <ListItem key={team.universal_team_id}>
                        {teams.indexOf(team)+1}. {team.name}: {team.victory_points}
                    </ListItem>
                )))}
            </List>
        </Box>
    )
}
