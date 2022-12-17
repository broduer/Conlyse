import {NavLink} from "react-router-dom";

export default function CountryLink({children, game_id, country_id}){
    return (
        <NavLink
            style={{
                textDecoration: "none",
                color: "white",
            }}
            to={`/game/${game_id}/country/${country_id}`} >
            {children}
        </NavLink>
    )
}