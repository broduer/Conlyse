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
import {theme} from "../../../helper/theme";

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
    plugins: {
        legend: {
            position: 'top',
            display: true,
            color: 'rgb(63, 181, 102)',
        },
        title: {
            display: false,
            text: 'Chart.js Line Chart',
        },
    },
    layout: {
        padding: {
            left: 10,
            right: 30,
            top: 3,
            bottom: 2
        }
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
    }
};



export default function VictoryGraph({victory_data}) {
    const data = {
        labels: victory_data["labels"],
        datasets: [
            {
                label: ["Victory Points"],
                yAxisID: "victory_points_y",
                data: victory_data["victory_points"]["data"],
                borderColor: 'rgb(63, 181, 102)',
                backgroundColor: 'rgb(63, 181, 102)',
                fill:false,
            },
        ]
    };
    return <Line options={options} data={data} width={197}/>;
}
