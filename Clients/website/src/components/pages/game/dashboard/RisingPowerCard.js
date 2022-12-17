import {Box, Typography, List, ListItem} from "@mui/material";
import {getActionColor} from "../../../../helper/color";

export default function RisingPowerCard({type, data}){
    let days = [1, 5, 10]
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
                    {days.map((day) => {
                        let percentage = (100 * ((data[0]/data[day])-1)).toFixed(1)
                        let diff = data[0] - data[day]

                        return (
                            <ListItem key={day}>
                                <Typography>
                                    Last {day===1 ? "Day" : day + " Days"}: <span style={{color: getActionColor(diff)}}>{diff>=0 ? "+" : ""}{diff} </span> / <span style={{color: getActionColor(percentage)}}>{percentage>=0 ? "+" : ""}{percentage}%</span>
                                </Typography>
                            </ListItem>
                        )
                    })}
                </List>
            </div>
        </Box>
    )
}