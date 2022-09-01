import { Outlet, Route, Routes,useNavigate } from "react-router-dom"
import React, {useEffect} from 'react'
import axios from 'axios'
import Login from "./components/registration/Login"
import Signup from "./components/registration/Signup"
import Homepage from "./components/homepage/Homepage"
//import ProtectRoutes from "./components/protectRoute/ProtectRoute"
//import PublicRoutes from "./components/protectRoute/PublicRoute"


function App() {

  return (
    <div className="w-screen h-screen flex justify-center items-center">
      <Routes>
          <Route path="login" element = {<Login />} />
          <Route path="register" element = {<Signup />} />
          <Route path="*" element = {<Homepage />} />
      </Routes>

    </div>
  )
}

export default App
