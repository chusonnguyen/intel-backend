import axios from 'axios';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';


const Dashboard = () => {
  const [dashboardProject, setDashboardProject] = useState([])
  const [yearHoneycomb, setYearHoneycomb] = useState("")
  const token=localStorage.getItem('token')
  let navigate = useNavigate()

  const fetchDashboardIni = async () => {
    await axios.get(`http://127.0.0.1:5000/dashboard/honeycomb/year=2022`, {
      headers: {
        'x-access-token': `${token}`
      }
    })
      .then((res: any) => {
        console.log(res.status)
        if(res.status == 200) {
          const dashboardProject = res.data
          setDashboardProject(dashboardProject)
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

  const fetchDashboard = async (yearHoneycomb: string) => {
    await axios.get(`http://127.0.0.1:5000/dashboard/honeycomb/year=${yearHoneycomb}`, {
      headers: {
        'x-access-token': `${token}`
      }
    })
      .then((res: any) => {
        console.log(res.status)
        if(res.status == 200) {
          const dashboardProject = res.data
          setDashboardProject(dashboardProject)
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
    console.log("DMM")
    fetchDashboardIni()
  },[])

  return (
    <div className='flex flex-col gap-8'>
      <div className='flex w-full justify-between items-center'>
        <span className='font-bold text-2xl'>Dashboard</span>
        {/* DROPDOWN PROJECT */}
        <div>
          <select name="project" id="">
            {dashboardProject.map((project,index) => {
              return (
                <option key={index} value="">Project A</option>
              )
              
            })}
            
          </select>
        </div>
      </div>

      {/* HONEYCOMB % */}
      
      <div>
        <span className='font-bold'>Honeycomb rate %</span>
        <div className='flex w-full justify-between items-center'>
        <span>Year</span>

        <select onChange={(e) => {
          fetchDashboard(e.target.value)
        }} name="" id="">
          <option value="2022">2022</option>
          <option value="2021">2021</option>
        </select>
        
        <input type="text" />
          {dashboardProject.map(p => {
            return (
                <div className='flex flex-col gap-3'>
                  <span>Month: {p.month}</span>
                  <span>{p.honeycomb}</span>
                </div>      
            )
          })}
          
        </div>
      </div>
      {/* USABLE m2 */}
      <div>
        <span className='font-bold'>Usable space m2</span>
        <div className="flex flex-col">
          <div className='flex w-full justify-between items-center'>
            <span>Zone: <span>Value <span>(m2)</span></span></span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard