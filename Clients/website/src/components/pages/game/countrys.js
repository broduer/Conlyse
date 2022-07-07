import {Link, useParams} from "react-router-dom";
import CustomDrawer from "../../CustomDrawer";
import {DataGrid, GridToolbar} from "@mui/x-data-grid";
import * as React from "react";
import {
    ArrowLeft,
    ArrowRightOutlined,
    Block,
    Check, Info,
} from "@mui/icons-material";
import {getResourceName} from "../../../helper/gameTypes";
import {getDifference} from "../../../helper/time";
import {useState} from "react";
import {IconButton, Stack, TextField} from "@mui/material";
import {theme} from "../../../helper/theme";
import getRows from "../../../helper/countrys/RowsGetter";
import {useQueries, useQuery} from "react-query";
import {getCombined} from "../../../helper/CombinedArray";
import * as api from "../../../helper/api";
import {isEqual} from "lodash";


export default function Countrys() {
    const {game_id} = useParams()
    const {data} = useQuery(["game", game_id], () => api.getGame(game_id), {keepPreviousData : true});
    const [day, setDay] = useState(0)
    const [rows, setRows] = useState([])
    const [rows_loaded, setRows_loaded] = useState(false)
    const [loaded, setLoaded] = useState(false)
    const [columns, setColumns] = useState( [
        { field: "cid", headerName: 'Country ID', hide: true, flex: 0.1},
        { field: "cn", headerName: 'Country Name', flex: 0.2},
        { field: "pyn", headerName: 'Player Name', flex: 0.2},
        { field: "tn", headerName: "Team Name", flex: 0.2},
        { field: "vp", headerName: "Victory Points", flex: 0.15},
        { field: "ml", headerName: "Morale", flex: 0.15},
        { field: "trp", headerName: "Total Economy", flex: 0.15},
        { field: "2", headerName: getResourceName("2"),renderHeader: (params => {return getResourceName(params.field)}), flex: 0.08, hide:true},
        { field: "3", headerName: getResourceName("3"),renderHeader: (params => {return getResourceName(params.field)}), flex: 0.08, hide:true},
        { field: "5", headerName: getResourceName("5"),renderHeader: (params => {return getResourceName(params.field)}), flex: 0.08, hide:true},
        { field: "6", headerName: getResourceName("6"),renderHeader: (params => {return getResourceName(params.field)}), flex: 0.08, hide:true},
        { field: "7", headerName: getResourceName("7"),renderHeader: (params => {return getResourceName(params.field)}), flex: 0.08, hide:true},
        { field: "21", headerName: getResourceName("21"),renderHeader: (params => {return getResourceName(params.field)}), flex: 0.08, hide:true},
        { field: "t_ac", headerName: "Annexed Cities"},
        { field: "t_c", headerName: "Cities", width: 70},
        { field: "t_mlc", headerName: "Mainland Cities"},
        { field: "t_p", headerName: "Provinces", width: 70},
        { field: "t_pc", headerName: "Provinces & Cities"},
        { field: 'type', headerName: 'Computer', width: 50,
            renderCell: (cell) => {
                if(cell.row.computer === false) return <Block color={"error"}/>
                else return <Check color={"success"}/>
            }},
        { field: 'info_button',minWidth: 20, headerName: "Info", renderCell: (cell) => {
                return (
                    <Link to={`/game/${game["gid"]}/country/${cell.row["cid"]}`}>
                        <Info color={"info"}/>
                    </Link>
                )
            }}]
    )
    let defined = data ? data[game_id] : undefined;
    let game = {};

    if(!!defined){
        game = data[game_id]
        if (!loaded){
            setDay(getDifference(game["st"], game["ct"], "D"))
            setLoaded(true)
        }
    }
    let results = useQueries([
        { queryKey: ['teams', game["gid"]], queryFn: () => api.getTeams(game["gid"]), keepPreviousData : true, enabled: !!defined && loaded},
        { queryKey: ['countrys', game["gid"], "normal", "-1", "-1"], queryFn: () => api.getCountrys(game["gid"], "normal", "-1", "-1"), keepPreviousData : true, enabled: !!defined && loaded},
        { queryKey: ['countrys', game["gid"], "stats", "-1", day], queryFn: () => api.getCountrys(game["gid"], "stats", "-1", day), keepPreviousData : true, enabled: !!defined && loaded, refetchOnMount: false},
    ])

    const isSuccess = !results.some(query => !query.isSuccess)


    if(isSuccess && !rows_loaded) {
        setRows_loaded(true)
        setRows(getRows(Object.values(results[0]["data"]), getCombined([Object.values(results[1]["data"]), Object.values(results[2]["data"])], "cid")))
    }
    const handleDayChange = (day) => {
        setRows_loaded(false)
        setDay(day)
    }


    return(
        <CustomDrawer game_id={game["gid"]}>
            <div style={{margin: 20}}>
                <div style={{height: "calc(100vh - 160px)", width: "100%"}}>
                    <Stack direction={"row"} justifyContent={"space-between"} alignItems={"flex-end"}>
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
                                    if (event.target.value >= getDifference(game["st"], game["ct"], "D")){
                                        event.target.value = getDifference(game["st"], game["ct"], "D")
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
                                    if(event.target.value <= getDifference(game["st"], game["ct"], "D")){
                                        handleDayChange(parseInt(event.target.value))
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
                                            if(day < getDifference(game["st"], game["ct"], "D")){
                                                handleDayChange(Number(day) + 1)
                                            }
                                        }}
                            >
                                <ArrowRightOutlined color={"primary"}/>
                            </IconButton>
                        </Stack>
                    </Stack>

                    <DataGrid
                        columns={columns}
                        rows={rows}
                        onStateChange={
                            // Sets the State of the Columns otherwise day changes would make enabled columns visible or hidden again
                            (state) => {
                                let new_columns = columns
                                for (let column in state.columns.lookup){
                                    column = state.columns.lookup[column]
                                    new_columns.find((new_column) => column["field"] === new_column["field"])["hide"]= column["hide"]
                                }
                                if(!isEqual(columns, new_columns)) setColumns(new_columns)
                            }
                        }
                        components={{ Toolbar: GridToolbar}}
                        style={{
                            flexGrow: 1,
                        }}
                    />
                </div>
            </div>
        </CustomDrawer>
    )
}