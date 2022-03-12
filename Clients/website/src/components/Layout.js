import React from "react";
import {Route,Routes} from "react-router-dom";
import Startpage from "../pages/Startpage";



export default function Layout(){
    return (
        <Routes>
            <Route path={"/"} element={<Startpage/>}/>
        </Routes>
    )
}