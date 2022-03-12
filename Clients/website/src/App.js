import Header from "./components/Header";
import {BrowserRouter as Router, Routes, Route} from "react-router-dom";
import Startpage from "./pages/Startpage";
import React, {Component, useEffect, useState} from "react";
import Game from "./groups/game";
import {theme} from "./helper/theme";
import {CssBaseline, ThemeProvider} from "@mui/material";
import Countrys from "./components/game/countrys";
import Country from "./components/game/country";
import Dashboard from "./components/game/dashboard";


const App = () => {


    return (
        <ThemeProvider theme={theme}>
            <CssBaseline/>
            <Router>
                <div className="App">
                    <Header/>
                    <Routes>
                        <Route path={"/game/:game_id"} element={<Game/>} exact/>
                        <Route path={"/game/:game_id/dashboard"} element={<Dashboard/>}/>
                        <Route path={"/game/:game_id/countrys"} element={<Countrys/>}/>
                        <Route path={"/game/:game_id/country/:country_id"} element={<Country/>}/>
                        <Route path={"/"} element={<Startpage/>} exact/>
                    </Routes>
                </div>
            </Router>
        </ThemeProvider>
        );
}
export default App

