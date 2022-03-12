import {Box, Typography, List, ListItem} from "@mui/material";
import {getActionColor} from "../../../helper/color";

export default function RisingpowerCard({type, data}){
    const data_arr = Object.values(data["data"])
    const last_1_percentage = (100 * (1 - (data_arr[data_arr.length - 2]/data_arr[data_arr.length - 1]))).toFixed(1)
    const last_5_percentage = (100 * (1 - (data_arr[data_arr.length - 6]/data_arr[data_arr.length - 1]))).toFixed(1)
    const last_10_percentage =(100 * (1 - (data_arr[data_arr.length - 11]/data_arr[data_arr.length - 1]))).toFixed(1)
    return (
        <Box sx={{
            border: 2,
            borderColor: "secondary.main",
            borderRadius: 10,
            width:"100%",
        }}>
            <div>
                <List sx={{
                    ml:1.5,
                }}>
                    <Typography fontSize={"large"}>
                        {type}
                    </Typography>
                    <ListItem>
                        <Typography>
                            Last Day: <span style={{color: getActionColor(data["last_1"])}}>{data["last_1"]>=0 ? "+" : ""}{data["last_1"]} </span> / <span style={{color: getActionColor(last_1_percentage)}}>{last_1_percentage>=0 ? "+" : ""}{last_1_percentage}%</span>
                        </Typography>
                    </ListItem>
                    <ListItem>
                        <Typography>
                            Last 5 Days: <span style={{color: getActionColor(data["last_5"])}}>{data["last_5"]>=0 ? "+" : ""}{data["last_5"]} </span> / <span style={{color: getActionColor(last_5_percentage)}}>{last_5_percentage>=0 ? "+" : ""}{last_5_percentage}%</span>
                        </Typography>
                    </ListItem>
                    <ListItem>
                        <Typography>
                            Last 10 Days: <span style={{color: getActionColor(data["last_10"])}}>{data["last_10"]>=0 ? "+" : ""}{data["last_10"]} </span> / <span style={{color: getActionColor(last_10_percentage)}}>{last_10_percentage>=0 ? "+" : ""}{last_10_percentage}%</span>
                        </Typography>
                    </ListItem>
                </List>
            </div>
        </Box>
    )
}