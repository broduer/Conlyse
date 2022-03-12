import React from 'react';
import {Navigate, useLocation, useParams} from "react-router-dom";
import {useFetch} from "../helper/useFetch";

export default function Game(){


    const {game_id} = useParams()
    const location = useLocation()
    const datas = {
        "provinces": useFetch(`http://127.0.0.1:5000/api/v1/province?game_id=${game_id}&current_time=${location.state.game["current_time"]}`),
        "trades": useFetch(`http://127.0.0.1:5000/api/v1/trade?game_id=${game_id}`),
        "countrys": useFetch(`http://127.0.0.1:5000/api/v1/country?game_id=${game_id}`),
        "teams": useFetch(`http://127.0.0.1:5000/api/v1/team?game_id=${game_id}`),
        "game": location.state.game
    }
    let loading = false;
    for (let data in datas) {
        if ("game" === data) continue
        data = datas[data]
        if (data.isLoading || data.data === null){
            loading = true
        }
    }
    if(loading){
        return (
            <div>
                Loading...
            </div>
        )
    }else {
        for (let data in datas){
            if ("game" === data) continue
            datas[data] = datas[data].data
        }
        return (
            <Navigate to={`/game/${game_id}/dashboard`} state={{data: datas}} replace/>
        )
    }
}
