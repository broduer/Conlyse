import {Box} from "@mui/material";
import Carousel from "react-material-ui-carousel";
import Risingpower from "./risingpower";

export default function Risingpowers({rising_powers_countrys}){
    return (
        <Box sx={{
            bgcolor: "divider",
            border: 3,
            borderColor: "primary.main",
            borderRadius: 10,
        }}>
            <Carousel interval={10000}>
                {Object.values(rising_powers_countrys).slice(0,3).map((rising_power_country => (
                    <Risingpower key={rising_power_country.country_id} country={{rising_power_country}} number={rising_powers_countrys.indexOf(rising_power_country)+1}/>
                )))}
            </Carousel>
        </Box>
    )
}