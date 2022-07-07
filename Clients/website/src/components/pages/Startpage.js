import React from 'react';
import {Container, Grid} from "@mui/material";
import GameCard from "../gameCard";
import {useQuery} from "react-query";
import * as api from "../../helper/api";

export default function Startpage(){

    const {data: games, status} = useQuery("games", api.getGames);
    if (status === "loading"){
        return (<div>Loading ...</div>)
    }
    else if (status === "error"){
        return (<div>Error</div>)
    }
    else {
        return (
            <Container>
                <Grid container spacing={3}>
                    {Object.values(games).map((game => (
                        <Grid item key={game["gid"]} xs={12} md={6} lg={4}>
                            <GameCard game={game}/>
                        </Grid>
                    )))}
                </Grid>
            </Container>
        );
    }
}