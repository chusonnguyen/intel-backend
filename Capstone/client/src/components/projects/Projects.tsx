import React, { useEffect, useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import axios from 'axios'

const Projects = () => {
  const [projectData, setProjectData] = useState([])
  let navigate = useNavigate()
  const token=localStorage.getItem('token')

  const fetchToken = async () => {
    if(!token) {
      navigate('/login')
    }
    await axios.get(`http://127.0.0.1:5000/verify-token`, {
      headers: {
        'x-access-token': `${token}`
      }
    })
    .then(
      (response) => {
        console.log(response.status)
        if(response.status == 200) {
          
        }
        if(response.status == 401) {
          navigate('/login')
          localStorage.clear()
        }
      },
      (error) => {
        console.log(error)
        navigate('/login')
        localStorage.clear()
      }
    )
  }

  const fetchProjects = async () => {
    await axios.get(`http://127.0.0.1:5000/projects`, {
      headers: {
        'x-access-token': `${token}`
      }
    })
    .then((res: any) => {
      if(res.status == 200) {
        const project = res.data
        setProjectData(project)
      }
      if(res.status == 401) {
        navigate('/login')
        localStorage.clear()
      }
      
    })
  }

  useEffect(() => {
    fetchToken()
    fetchProjects()
  }, [])

  return (
    <div className='flex flex-col w-full gap-6'>
      <div className='w-full flex justify-between items-center py-6'>
        <span className='font-bold text-2xl'>Projects</span>
        <NavLink to={'create-project'} className='bg-intel-blue text-white rounded-lg px-4 py-3'>+ New Project</NavLink>
      </div>
      
      <div className='grid grid-cols-3 w-full gap-6'>
        {projectData.map((project, index) => {
          return (
            <NavLink key={index} to={`/project/${project.project_id}`} className='border rounded-lg p-4 flex flex-col'>
                <img src="" alt="thumbnail" />
                <span className='font-bold truncate'>{project.project_name}</span>
                <span>{project.project_type}</span>
                <div className='w-full flex justify-between items-center'>
                  <span>Created By <span>{project.created_by}</span></span>
                  <span>{project.project_id}</span>
                </div>  
            </NavLink>
          )
        })}
          
      </div>
    </div>
  )
}

export default Projects