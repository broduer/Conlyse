import {createTheme} from "@mui/material";

export const theme = createTheme({
    palette: {
        mode: 'dark',
        primary: {
            main: '#3fb566',
        },
        secondary: {
            main: '#00542c',
        },
        error: {
            main: '#ff0000',
        },
        warning: {
            main: '#f3e700',
        },
        info: {
            main: '#21f3f3',
        },
        success: {
            main: '#00ff0b',
        },
        resources: {
            supplies: '#384F13',
            fuel: '#BD4E44',
            components: '#71819B',
            electronics: '#4EC263',
            rare_materials: '#B6773C',
            money: '#091c00',
        }
    },
    typography: {
        fontFamily: 'Noto Sans',
    },
});
