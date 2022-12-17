import Countrys from "./pages/game/countrys";
import React, {useState} from "react";
import Toolbar from "@mui/material/Toolbar";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import Drawer from "@mui/material/Drawer";
import Divider from "@mui/material/Divider";
import {List, ListItem, ListItemText} from "@mui/material";
import Box from "@mui/material/Box";
import {useTheme} from "@mui/material/styles";
import {useNavigate} from "react-router-dom";

import MenuIcon from "@mui/icons-material/Menu";
import HomeIcon from '@mui/icons-material/Home';
import FlagIcon from '@mui/icons-material/Flag';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AppBar from "@mui/material/AppBar";
import {LocationCity, Public} from "@mui/icons-material";

const drawerWidth=240



export default function CustomDrawer({children, game_id}) {
    const navigate = useNavigate()
    const theme = useTheme();
    const [open, setOpen] = useState();
    const toggleDrawer = (open) => (event) => {
        if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
            return;
        }

        setOpen(open)
    };

    const list = () => (
        <Box
            sx={{ width: 250 }}
            role="presentation"
            onClick={toggleDrawer(false)}
            onKeyDown={toggleDrawer(false)}
        >
            <List>
                <ListItem button key={"Dashboard"} onClick={() => navigate(`/game/${game_id}/dashboard`)}>
                    <DashboardIcon/>
                    <ListItemText>Dashboard</ListItemText>
                </ListItem>
                <ListItem button key={"Countrys"} onClick={() => navigate(`/game/${game_id}/countrys`)}>
                    <FlagIcon/>
                    <ListItemText>Countrys</ListItemText>
                </ListItem>
                <ListItem button key={"Provinces"} onClick={() => navigate(`/game/${game_id}/provinces`)}>
                    <LocationCity/>
                    <ListItemText>Provinces</ListItemText>
                </ListItem>
                <ListItem button key={"Map"} onClick={() => navigate(`/game/${game_id}/map`)}>
                    <Public/>
                    <ListItemText>Map</ListItemText>
                </ListItem>
                <Divider/>
                <ListItem sx={{flex: "end"}} button key={"BackHome"} onClick={() => navigate(`/`)}>
                    <HomeIcon/>
                    <ListItemText>Back to Game Selection</ListItemText>
                </ListItem>
            </List>
        </Box>
    );


    return(
        <div>
            <Drawer
                anchor={"left"}
                open={open}
                onClose={toggleDrawer(false)}
            >
                {list()}
            </Drawer>
            <AppBar position={"sticky"}>
                <Toolbar>
                    <IconButton
                        size="large"
                        edge="start"
                        color="inherit"
                        aria-label="menu"
                        sx={{ mr: 2 }}
                        onClick={toggleDrawer(!open)}
                    >
                        <MenuIcon />
                    </IconButton>
                    <img width={100} src={"/logo.png"} alt={"Conlyse"}/>
                </Toolbar>
            </AppBar>
            <div>
                {children}
            </div>
        </div>
    )
}