import React from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend, TimeScale,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';
import {theme} from "../../../../helper/theme";
import {getResourceColour, getResourceName} from "../../../../helper/gameTypes";

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale,
);

export const options = {
    maintainAspectRatio : false,
    responsive : true,
    animation: false,
    plugins: {
        legend: {
            position: 'top',
            display: true,
            color: 'rgb(63, 181, 102)',
        },
        title: {
            display: false,
        },
    },
    scales: {
        x: {
            title: {
                display: true,
                text: "Days",
            },
            fontColor:"#411111",
            ticks: {
                color: theme.palette.secondary.main,
            },
        }
    },
    interaction: {
        intersect: false,
        mode: 'index',
    }
};



export default function EconomyGraph({country}) {
    const data = {
        labels: country["economy"]["labels"],
        datasets: []
    };
    for (let key in Object.keys(country["economy"])){
        key = Object.keys(country["economy"])[key]
        let name = getResourceName(key.toString())
        let hidden = false
        if (name){
            if (key === "21" || key === "trp") hidden = true
            data["datasets"].push({
                label: name,
                yAxisID: "economy_y",
                data: country["economy"][key],
                borderColor: `rgb(${getResourceColour(key)})`,
                backgroundColor: `rgb(${getResourceColour(key)})`,
                cubicInterpolationMode: 'monotone',
                fill:false,
                hidden: hidden,
            })
        }
    }
    return (
        <div style={{position:"relative", height: "30vh", padding:"1%"}}>
            <Line options={options} data={data} type={"line"}/>
        </div>)
}
