import {DataGrid} from "@mui/x-data-grid";
import {theme} from "../../../helper/theme";
import {getResourceColor} from "../../../helper/color";
import * as React from 'react';


export default function Trades({trades, countrys, game, speed}){

    for (let trade in trades){
        trade = trades[trade]
        trade["id"] = trade["trade_id"]
        trade["price"] = trade["amount"] * trade["limit"]
        trade["time"] = new Date((game["start_time"] + ((trade["current_time"] - game["start_time"]) / speed)) * 1000)
        trade["type"] = trade["resource_type"]
        trade["country"] = countrys[trade["owner_id"]].country_name
        if (trade["buy"]) trade["action"] = "Buy"
        else trade["action"] = "Sell"
    }
    const rows = Object.values(trades)
    const colums = [
        { field: 'id', headerName: 'ID', hide:true, hideable: true},
        { field: 'type', headerName: 'Type', flex: 0.2,
            renderCell: (cell) => {
            return (
                <img src={require(`../../../images/resources/${cell.row.type}.png`)} height={"100%"}/>
            )
            }},
        { field: 'amount', headerName: 'Amount', flex: 0.4},
        { field: 'price', headerName: 'Price', flex: 0.4},
        { field: 'action', headerName: 'Action', flex: 0.2},
        { field: 'time', headerName: 'Time', type:"date", flex: 0.8},
        { field: 'country', headerName: 'Country', flex: 0.8},
    ]

    const [sortModel, setSortModel] = React.useState([
        {
            field: 'time',
            sort: 'desc',
        },
    ]);

    return (
        <div style={{ display: "flex", height: "100%"}}>
            <div style={{
                flexGrow: 1,
            }}>
                <DataGrid
                    rows={rows}
                    columns={colums}
                    sortModel={sortModel}
                    onSortModelChange={(model) => setSortModel(model)}
                    hideFooter
                    sx={{
                        border: 3,
                        borderColor: "primary.main",
                        borderRadius: 10,
                        bgcolor: "divider",
                        overflow: "hidden",
                    }}
                />
            </div>
        </div>
    )
}