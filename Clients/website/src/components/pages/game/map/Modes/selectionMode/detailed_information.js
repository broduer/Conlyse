import {Card, CardContent, CardHeader, IconButton, Typography} from "@mui/material";
import React from "react";
import {Close} from "@mui/icons-material";
import {getResourceName} from "../../../../../../helper/game_types";



export default function DetailedInformation({countrys, current_province, setCurrentProvince}){

    const handleClose = () => setCurrentProvince([])



    if (current_province.length === 0) return null;
    const province_name = current_province.length === 1 ? Object.values(current_province)[0]["pn"] : null
    function get_country_name() {
            const locked_owner_id = Object.values(current_province)[0]["oid"]
            for (let province in current_province){
                if (current_province[province]["oid"]!== locked_owner_id){
                    return null
                }
            }
            return countrys[locked_owner_id]["cn"]
    }
    const country_name = get_country_name()
    const title = province_name ? `${province_name} (${country_name})` : country_name
    // console.time("total")
    let current_province_total = Object.values(current_province).reduce((acc, obj) =>
    {
        Object.entries(obj).forEach(([k, v]) =>
        {
            if (!(["bt", "bd", "pn"].includes(k))){
                acc[k] = (acc[k] || 0) + v;
            }
        });

        return acc;
    }, {});
    //console.timeEnd("total")
    return (
        <Card sx={{
            position: "absolute",
            right: 0,
            bottom: 0,
            width: "20%",
            height: "40vh",
            margin: 2,
            bgcolor: "background.paper",
            border: 3,
            borderColor: "primary.main",
            borderRadius: 10,
        }}>
            <CardHeader
                title={title}
                action={
                    <IconButton aria-label="close" onClick={handleClose}>
                        <Close/>
                    </IconButton>
                }
            />
            <CardContent>
                <Typography>
                    {current_province.length> 1 ? `Province count: ${current_province.length}`: undefined}
                </Typography>
                <Typography>
                    Victory Points: {current_province_total["vp"]}
                </Typography>
                <Typography>
                    Resource Production:
                </Typography>
                {Object.entries(current_province_total).map(([key, cpt]) => {
                    let name = getResourceName(key)
                    if (name && cpt !== 0) return (
                        <Typography key={key}>
                            {name}: {cpt}
                        </Typography>
                    )
                })
                }
            </CardContent>
        </Card>
    )
}