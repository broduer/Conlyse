import {Box, Typography, List, ListItem} from "@mui/material";
import {getActionColor} from "../../../../helper/color";

export default function RisingpowerCard({type, data}){
    const last_1_percentage = (100 * (1 - (data["1"]/data["0"]))).toFixed(1)
    const last_5_percentage = (100 * (1 - (data["5"]/data["0"]))).toFixed(1)
    const last_10_percentage =(100 * (1 - (data["10"]/data["0"]))).toFixed(1)
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
                            Last Day: <span style={{color: getActionColor(data["l1"])}}>{data["l1"]>=0 ? "+" : ""}{data["l1"]} </span> / <span style={{color: getActionColor(last_1_percentage)}}>{last_1_percentage>=0 ? "+" : ""}{last_1_percentage}%</span>
                        </Typography>
                    </ListItem>
                    <ListItem>
                        <Typography>
                            Last 5 Days: <span style={{color: getActionColor(data["l5"])}}>{data["l5"]>=0 ? "+" : ""}{data["l5"]} </span> / <span style={{color: getActionColor(last_5_percentage)}}>{last_5_percentage>=0 ? "+" : ""}{last_5_percentage}%</span>
                        </Typography>
                    </ListItem>
                    <ListItem>
                        <Typography>
                            Last 10 Days: <span style={{color: getActionColor(data["l10"])}}>{data["l10"]>=0 ? "+" : ""}{data["l10"]} </span> / <span style={{color: getActionColor(last_10_percentage)}}>{last_10_percentage>=0 ? "+" : ""}{last_10_percentage}%</span>
                        </Typography>
                    </ListItem>
                </List>
            </div>
        </Box>
    )
}