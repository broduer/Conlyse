import {DataGrid} from "@mui/x-data-grid";
import * as React from 'react';
import {getResourceName} from "../../../../helper/game_types";


export default function Trades({trades}){
    const [sortModel, setSortModel] = React.useState([
        {
            field: 'time',
            sort: 'desc',
        },
    ]);

    const rows = Object.values(trades)
    const colums = [
        { field: 'id', headerName: 'ID', hide:true, hideable: true},
        { field: 'rsrt', headerName: 'Type', flex: 0.2,
            renderCell: (cell) => {
            return (
                <img src={`/resources/${cell.row["rsrt"]}.png`} alt={getResourceName(cell.row["rsrt"])} height={"100%"}/>
            )
            }},
        { field: 'am', headerName: 'Amount', flex: 0.4},
        { field: 'pc', headerName: 'Price', flex: 0.4},
        { field: 'b', headerName: 'Action', flex: 0.2},
        { field: 'cn', headerName: 'Country', flex: 0.8},
    ]


    return (

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
    )
}