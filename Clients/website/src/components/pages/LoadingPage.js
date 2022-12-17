import CustomDrawer from "../CustomDrawer";
import CircularProgressWithLabel from "../CircularProgressWithLabel";
import {CircularProgress} from "@mui/material";

export default function LoadingPage({game_id, percentage}){
    return (
        <CustomDrawer game_id={game_id}>
            {percentage != null ? <CircularProgressWithLabel value={percentage}/> : <CircularProgress/>}
        </CustomDrawer>
    )
}