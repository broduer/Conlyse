import {Box} from "@mui/material";
import {DataGrid} from "@mui/x-data-grid";
import * as React from "react";

export default function HighvalueCities({cities, countrys}){
    for (let city in cities){
        city = cities[city]
        city["id"] = city["province_id"]
        city["country"] = countrys[city["owner_id"]]["country_name"]
        let building = city["buildings"][0]
        city["building"] = building["name"] + " - " + building["level"]
    }
    const rows = Object.values(cities)
    const colums = [
        { field: 'id', headerName: 'ID', hide:true, hideable: true},
        { field: 'province_name', headerName: 'City', flex: 1},
        { field: 'country', headerName: 'Country', flex: 0.6},
        { field: 'total', headerName: 'Resources', flex: 0.5},
        { field: 'building', headerName: 'Building', flex: 1.2},
    ]
    return (
        <div style={{ display: "flex", height: "100%"}}>
            <div style={{
                flexGrow: 1,
            }}>
                <DataGrid
                    rows={rows}
                    columns={colums}
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