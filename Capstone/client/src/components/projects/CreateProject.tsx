import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import axios from 'axios'

const CreateProject = () => {
    let navigate = useNavigate()
    const [projectName, setProjectName] = useState("")
    const [projectType, setProjectType] = useState("")
    const [projectAddress, setProjectAddress] = useState("")
    const [error, setError] = useState("")
    const token = localStorage.getItem("token")
  
    const onChangeInputProjectName = (e: { target: { value: any } }) => {
        setProjectName(e.target.value)
    }
  
    const onChangeInputProjectType = (e: { target: { value: any } }) => {
        setProjectType(e.target.value)
    }

    const onChangeInputProjectAddress = (e: { target: { value: any } }) => {
        setProjectAddress(e.target.value)
    }

    let data = {
        project_name: projectName,
        project_type: projectType,
        address: projectAddress
    }

    const headers = { 
        'Content-Type': 'application/json',
        'x-access-token': `${token}`
    }

    const handleSubmit = (e: any) => {
        e.preventDefault()
        if(projectName != "" || projectType != "" || projectAddress != "") {
            setError("Empty Space")
        }
        if(projectName != "" && projectType != "" && projectAddress != "") {
            axios.post('http://127.0.0.1:5000/projects', data, {
        headers:headers
        })
        .then((response) => {
        console.log(response.status);
        console.log(response.data)
        if(response.status == 200) {
            navigate('/projects')
        }
        }, (error) => {
        console.log(error);
        setError("Fail to create")
        });
        }
        
    }

  return (
    <div>
        <span>Create Project</span>
        
        <form action="submit" onSubmit={handleSubmit}>
            <span>{error}</span>
            <div className='flex flex-col gap-4'>
                <label htmlFor="projectName" className='text-xs'>Project name</label>
                <input onChange={onChangeInputProjectName} type="text" className='bg-email-bg rounded-sm focus:bg-white focus:border focus:border-email-bg focus:outline-none px-3 py-2 text-xs'placeholder='Project name'/>
            </div>
            <div className='flex flex-col gap-4'>
                <label htmlFor="password" className='text-xs'>Project type</label>
                <input onChange={onChangeInputProjectType} type="text" className='bg-email-bg rounded-sm focus:bg-white focus:border focus:border-email-bg focus:outline-none px-3 py-2 text-xs'placeholder='Project type'/>
            </div>
            <div className='flex flex-col gap-4'>
                <label htmlFor="password" className='text-xs'>Project address</label>
                <input onChange={onChangeInputProjectAddress} type="text" className='bg-email-bg rounded-sm focus:bg-white focus:border focus:border-email-bg focus:outline-none px-3 py-2 text-xs'placeholder='Project address'/>
            </div>
            
            <div className='w-full flex justify-between items-center'>
                <button type='submit' className='bg-intel-blue text-white text-sm p-5 hover:bg-blue-400'>Create</button>
            </div>
        </form>
    </div>
  )
}

export default CreateProject