import {useLocation, useNavigate, useParams} from "react-router-dom";
import CustomDrawer from "../CustomDrawer";
import {DataGrid, GridColDef, GridRowsProp, GridToolbar} from "@mui/x-data-grid";
import {useCountrys, useDashboard, useGame} from "./useLoad";
import * as React from "react";
import {
    ArrowCircleRightOutlined,
    ArrowLeft,
    ArrowRight, ArrowRightOutlined,
    Block,
    Check,
    DoDisturb,
    TextFieldsOutlined
} from "@mui/icons-material";
import {getResourceName} from "../../helper/gameTypes";
import DayChanger from "../DayChanger";
import {getDifference} from "../../helper/time";
import {useEffect, useState} from "react";
import {Button, IconButton, Stack, TextField} from "@mui/material";
import {theme} from "../../helper/theme";
import {useFetch} from "../../helper/useFetch";
import getRows from "../../helper/countrys/RowsGetter";

export default function Countrys(){
    const {game_id} = useParams()
    const {datas, loading} = useGame(game_id)
    if (loading){
        return (
            <div>
                Loading
            </div>
        )
    }else return (
        <CountrysDiv game={datas.game.data[0]}/>
    )
}




function CountrysDiv({game}) {
    const navigate = useNavigate()
    const [day, setDay] = useState(getDifference(game["start_time"], game["current_time"], "D"))
    let {datas, loading} = useCountrys(game, day)
    const [rows, setRows] = useState()
    const [isLoaded, setLoaded] = useState(false)
    const handleDayChange = async (day) => {
        setDay(day)
        loading = true
        setRows([{"id": "Loading", "country_name": "Loading"}])
        datas = {
            "countrys": {
                "data": datas["countrys"].data
            },
            "teams": {
                "data": datas["teams"].data
            },
            "countrys_adv": {
                "data": await (await fetch(`http://127.0.0.1:4444/api/v1/country?game_id=${game["game_id"]}&economy=true&single&day=${day}`)).json()
            }
        }
        loading = false
        const rows_mod: GridRowsProp = getRows(datas)
        setRows(rows_mod)
    }
    if (loading)return (
        <div>
            Loading...
        </div>
    )

    if (!isLoaded){
        const rows_mod: GridRowsProp = getRows(datas)
        setRows(rows_mod)
        setLoaded(true)
    }



    const columns: GridColDef[] = [
        { field: "country_id", headerName: 'Country ID', hide: true, flex: 0.1},
        { field: "country_name", headerName: 'Country Name', flex: 0.2},
        { field: "player_name", headerName: 'Player Name', flex: 0.2},
        { field: "team_name", headerName: "Team Name", flex: 0.2},
        { field: "total_economy", headerName: "Total Economy", flex: 0.15},
        { field: "victory_points", headerName: "Victory Points", flex: 0.15},
        { field: "2", headerName: getResourceName(2),renderHeader: (params => {return getResourceName(params.field)}), flex: 0.08, hide:true},
        { field: "3", headerName: getResourceName(3),renderHeader: (params => {return getResourceName(params.field)}), flex: 0.08, hide:true},
        { field: "5", headerName: getResourceName(5),renderHeader: (params => {return getResourceName(params.field)}), flex: 0.08, hide:true},
        { field: "6", headerName: getResourceName(6),renderHeader: (params => {return getResourceName(params.field)}), flex: 0.08, hide:true},
        { field: "7", headerName: getResourceName(7),renderHeader: (params => {return getResourceName(params.field)}), flex: 0.08, hide:true},
        { field: "21", headerName: getResourceName(21),renderHeader: (params => {return getResourceName(params.field)}), flex: 0.08, hide:true},
        { field: 'type', headerName: 'Computer', flex: 0.015,
            renderCell: (cell) => {
                if(cell.row.computer === false) return <Block color={"error"}/>
                else return <Check color={"success"}/>
            }},
        {field: 'info_button',minWidth: 20, headerName: "Info", renderCell: (cell) => {
                return (
                    <Button onClick={() => navigate(`/game/${game["game_id"]}/country/${cell.row.country_id}`)}>
                        More Info
                    </Button>
                )
            }}
    ]
    return(
        <CustomDrawer game_id={game["game_id"]}>
            <div style={{height: "80vh", width: "100%"}}>
                <Stack direction={"row"} height={40} spacing={1} sx={{
                    right:0
                }}>
                    <IconButton sx={{
                        border: 1,
                        borderColor: theme.palette.primary.main,
                        height: 36,
                        width: 36,
                    }} variant={"outlined"}
                                onClick={() => {
                                    if(day > 0){
                                        handleDayChange(day-1)
                                    }
                                }}
                    >
                        <ArrowLeft color={"primary"}/>
                    </IconButton>
                    <TextField
                        type="text"
                        pattern="[0-9]*"
                        onKeyPress={(event) => {
                            if (!/[0-9]/.test(event.key)) {
                                event.preventDefault();
                            }
                        }}
                        onInput={event => {
                            if (event.target.value >= getDifference(game["start_time"], game["current_time"], "D")){
                                event.target.value = getDifference(game["start_time"], game["current_time"], "D")
                            }else if(event.target.value < 0){
                                event.target.value = 0
                            }
                        }}
                        onChange={(event) => {
                            if (event.target.value === ""){
                                if (parseInt(day) === 0){
                                    event.preventDefault()
                                    return
                                }
                                event.target.value = 0
                            }
                            event.target.value = parseInt(event.target.value)
                            if(event.target.value <= getDifference(game["start_time"], game["current_time"], "D")){
                                handleDayChange(event.target.value)
                            }else {
                                event.preventDefault()
                            }
                        }}
                        variant={"standard"}
                        margin={"none"}
                        size={"small"}
                        sx={{
                            width: 35,
                        }}
                        value={day}
                    />
                    <IconButton variant={"outlined"} sx={{
                        border: 1,
                        borderColor: theme.palette.primary.main,
                        height: 36,
                        width: 36,
                    }}
                                onClick={(event) => {
                                    if(day < getDifference(game["start_time"], game["current_time"], "D")){
                                        handleDayChange(Number(day) + 1)
                                    }
                                }}
                    >
                        <ArrowRightOutlined color={"primary"}/>
                    </IconButton>
                </Stack>
                <DataGrid
                    columns={columns}
                    rows={rows}
                    components={{ Toolbar: GridToolbar}}
                    style={{
                        flexGrow: 1,
                    }}
                />
            </div>
        </CustomDrawer>
    )
}