import React from 'react';
import {Container, Grid} from "@mui/material";
import GameCard from "../components/gameCard";
import {useFetch} from "../helper/useFetch";
export default function Startpage(){

    const games = useFetch("http://127.0.0.1:4444/api/v1/game")
    const scenarios = useFetch("http://127.0.0.1:4444/api/v1/static/scenario")

    if (games.isLoading ||scenarios.isLoading || games.data == null ||scenarios.data === null){
        return (<div>Loading ...</div>)
    }
    else {
        return (
            <Container>
                <Grid container spacing={3}>
                    {Object.values(games.data).map((game => (
                        <Grid item key={game.game_id} xs={12} md={6} lg={4}>
                            <GameCard game={game} scenario={scenarios.data[game.scenario_id]}/>
                        </Grid>
                    )))}
                </Grid>
            </Container>
        );
    }
}