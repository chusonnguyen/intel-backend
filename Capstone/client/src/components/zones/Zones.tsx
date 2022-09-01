import React, { useEffect, useState } from 'react'
import { Navigate, NavLink, useNavigate, useParams } from 'react-router-dom'
import axios from 'axios'

const Zones = () => {
  let navigate = useNavigate()
  let {id} = useParams()
  const [zoneData, setZoneData] = useState([])
  const token = localStorage.getItem("token")

  const fetchZones = async () => {
    await axios.get(`http://127.0.0.1:5000/zones`, {
      headers: {
        'x-access-token': `${token}`
      }
    })
    .then((res: any) => {
      console.log(res.status)
      if(res.status == 200) {
        const zone = res.data
        setZoneData(zone)
      }
      if(res.status == 401) {
        localStorage.clear()
        navigate('/login')
      }
      
    },
      (error) => {
        console.log(error)
      }
    )
  }
  

  useEffect(() => {
    fetchZones()
  }, [])


  return (  
    <div className='flex flex-col w-full'>
      <div className='w-full flex justify-between items-center py-6'>
        <span className='font-bold text-2xl'>Zones of Project {id}</span>
        <NavLink to={'/project/1/create-zone'} className='bg-intel-blue text-white rounded-lg px-4 py-3'>+ New Zone</NavLink>
      </div>

      <div className='grid grid-cols-3 w-full gap-6'>
          {zoneData.map((zone, index) => {
          return (
            <NavLink key={index} to={`/project/${id}/zone/${zone.zone_id}`} className='border rounded-lg p-4 flex flex-col'>
              <img src="" alt="thumbnail" />
              <span className='font-bold'>{zone.zone_name}</span>
              <span>{zone.zone_type}</span>
              <div className='w-full flex justify-between items-center'>
                <span>Created By <span>{zone.created_by}</span></span>
                <span>{zone.zone_id}</span>
              </div>  
          </NavLink>
          )
        })}
      </div>
    </div>
  )
}

export default Zones