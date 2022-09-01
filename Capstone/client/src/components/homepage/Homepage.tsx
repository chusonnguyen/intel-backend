import { Route, Routes ,useNavigate} from 'react-router-dom'
import React, {useEffect} from 'react'
import axios from 'axios'
import SideNav from '../navigation/SideNav'
import Dashboard from '../dashboard/Dashboard'
import History from '../history/History'
import Projects from '../projects/Projects'
import Header from '../header/Header'
import CreateProject from '../projects/CreateProject'
import Zones from '../zones/Zones'
import CreateZone from '../zones/CreateZone'
import Layout from '../layout/Layout'
import UploadLayout from '../zones/UploadLayout'

const Homepage = () => {
  return (
    <div className='w-full h-full flex justify-center items-center'>
      <SideNav />
      <div className='w-full h-full flex flex-col justify-center items-center'>
        <Header />
        <div className='p-6 w-full h-full'>
          <Routes>
            <Route path="*" element={<Dashboard />} />
            <Route path="history" element={<History />} />
            <Route path="projects" element={<Projects />} />
            <Route path="projects/create-project" element={<CreateProject />} />
            <Route path="project/:id" element={<Zones />} />
            <Route path="project/:id/create-zone" element={<CreateZone />} />
            <Route path="create-zone/upload-layout" element={<UploadLayout />} />
            <Route path="project/:id/zone/:id" element={<Layout />} />
          </Routes>
        </div>

      </div>

    </div>
  )
}

export default Homepage