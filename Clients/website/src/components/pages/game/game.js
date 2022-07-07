import {Navigate, useParams} from "react-router-dom";

export default function Game(){
    const {game_id} = useParams();
    return (
        <Navigate to={`/game/${game_id}/dashboard`} replace/>
    )
}