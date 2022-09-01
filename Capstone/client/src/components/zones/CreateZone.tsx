import axios from 'axios'
import React, { useState } from 'react'
import { NavLink, useNavigate, useParams } from 'react-router-dom'

const CreateZone = () => {
    let {id} = useParams()

    let navigate = useNavigate()

    const [zoneName, setZoneName] = useState("")
    const [zoneType, setZoneType] = useState("")
    const [zoneWidth, setZoneWidth] = useState("")
    const [zoneLength, setZoneLength] = useState("")
    const token = localStorage.getItem("token")
    const [error,setError] = useState("")
  
    const onChangeInputZoneName = (e: { target: { value: any } }) => {
        setZoneName(e.target.value)
    }
  
    const onChangeInputZoneType = (e: { target: { value: any } }) => {
        setZoneType(e.target.value)
    }
    const onChangeInputZoneWidth = (e: { target: { value: any } }) => {
        setZoneWidth(e.target.value)
    }
  
    const onChangeInputZoneLength = (e: { target: { value: any } }) => {
        setZoneLength(e.target.value)
    }

    let data = {
        project_id : id,
        zone_name: zoneName,
        zone_type: zoneType,
        width: zoneWidth,
        length: zoneLength,
    }

    const headers = { 
        'Content-Type': 'application/json',
        'x-access-token': `${token}`
    }

    const handleSubmit = async (e: any) => {
        e.preventDefault()
        if(zoneName != "" && zoneType != "" && zoneWidth != "" && zoneLength != "") {
            await axios.post('http://127.0.0.1:5000/zones', data, {
            headers:headers
            })
            .then((response) => {
            console.log(response.data);
            console.log(response.status)
            if(response.status == 200) {
                navigate(`/project/${id}`)
            }
            if(response.status == 401) {
                localStorage.clear()
                navigate('/login')
            }
            }, (error) => {
                console.log(error);
                setError("fail to create Zone")
            });
        } else {
            setError("Empty space")
        } 
    }


  return (
    <div>
        <span>Create Zone for project {id}</span>

        <form action="submit" onSubmit={handleSubmit}>
            <span>{error}</span>
            <div className='flex flex-col gap-4'>
                <label htmlFor="projectName" className='text-xs'>Zone name</label>
                <input onChange={onChangeInputZoneName} type="text" className='bg-email-bg rounded-sm focus:bg-white focus:border focus:border-email-bg focus:outline-none px-3 py-2 text-xs'placeholder='Zone name'/>
            </div>
            <div className='flex flex-col gap-4'>
                <label htmlFor="zoneType" className='text-xs'>Zone type</label>
                <input onChange={onChangeInputZoneType} type="text" className='bg-email-bg rounded-sm focus:bg-white focus:border focus:border-email-bg focus:outline-none px-3 py-2 text-xs'placeholder='Zone type'/>
            </div>
            <div className='flex flex-col gap-4'>
                <label htmlFor="zoneLength" className='text-xs'>Zone Length</label>
                <input onChange={onChangeInputZoneLength} type="number" className='bg-email-bg rounded-sm focus:bg-white focus:border focus:border-email-bg focus:outline-none px-3 py-2 text-xs'placeholder='Zone Length'/>
            </div>
            <div className='flex flex-col gap-4'>
                <label htmlFor="zoneWidth" className='text-xs'>Zone Width</label>
                <input onChange={onChangeInputZoneWidth} type="number" className='bg-email-bg rounded-sm focus:bg-white focus:border focus:border-email-bg focus:outline-none px-3 py-2 text-xs'placeholder='Zone Width'/>
            </div>

            <div className='w-full flex justify-between items-center'>
                <button type='submit' className='bg-intel-blue text-white text-sm p-5 hover:bg-blue-400'>Upload Layout</button>
            </div>
        </form>
    </div>
  )
}

export default CreateZone