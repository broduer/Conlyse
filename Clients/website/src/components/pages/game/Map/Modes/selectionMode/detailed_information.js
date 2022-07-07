import {Card, CardContent, CardHeader, IconButton, Typography} from "@mui/material";
import React, {useEffect, useState} from "react";
import {Close} from "@mui/icons-material";
import {getResourceName} from "../../../../../../helper/gameTypes";

export default function DetailedInformation({current_province, setCurrentProvince}){

    const handleClose = () => setCurrentProvince([])



    if (current_province.length === 0) return null;
    console.time("total")
    let current_province_total = Object.values(current_province).reduce((acc, obj) =>
    {
        delete obj["bd"]
        delete obj["bt"]
        delete obj["pn"]
        Object.entries(obj).forEach(([k, v]) =>
        {
            acc[k] = (acc[k] || 0) + v;
        });

        return acc;
    }, {});
    console.timeEnd("total")
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
                title={"Selection"}
                action={
                    <IconButton aria-label="close" onClick={handleClose}>
                        <Close/>
                    </IconButton>
                }
            />
            <CardContent>
                <Typography>
                    Province count: {current_province.length}
                </Typography>
                <Typography>
                    Victory Points: {current_province_total["vp"]}
                </Typography>
                <Typography>
                    Resource Production:
                </Typography>
                {Object.entries(current_province_total).map(([key, cpt]) => {
                    let name = getResourceName(key)
                    if (name) return (
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