import {DataGrid} from "@mui/x-data-grid";
import * as React from "react";

export default function HighValueCities({cities}){

    const [sortModel, setSortModel] = React.useState([
        {
            field: 'total',
            sort: 'desc',
        },
    ]);

    const rows = Object.values(cities)
    const colums = [
        { field: 'id', headerName: 'ID', hide:true, hideable: true},
        { field: 'province', headerName: 'City', flex: 1},
        { field: 'country', headerName: 'Country', flex: 0.6},
        { field: 'total', headerName: 'Resources', flex: 0.5},
        { field: 'building', headerName: 'Building', flex: 1.2},
    ]

    return (
        <DataGrid
            rows={rows}
            columns={colums}
            hideFooter
            sortModel={sortModel}
            onSortModelChange={(model) => setSortModel(model)}
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