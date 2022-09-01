import axios from 'axios'
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

const History = () => {
  const [history, setHistory] = useState([])
  let navigate = useNavigate()
  const token=localStorage.getItem('token')

  const fetchHistory = async () => {
    console.log("Vai loz luon")
    await axios.get(`http://127.0.0.1:5000/history/`, {
      headers: {
        'x-access-token': `${token}`
      }
  })
      .then(res => {
        if(res.status == 200) {
          const history = res.data
          setHistory(history)
        }
        if(res.status == 401) {
          localStorage.clear()
          navigate('/login')
        }
        
      })
  }


  useEffect(() => {
    fetchHistory()
  },[])

  return (
    <div className='flex flex-col gap-4 w-full'>
      <span className='font-bold text-2xl'>History</span>
      {history.map(h => {
        return (
          <div className='w-full flex justify-between items-center border rounded-lg p-4'>
            <div className='flex flex-col'>
              <span className='font-bold'>ID</span>
              <span>{h.id}</span>
            </div>
            <div className='flex flex-col'>
              <span className='font-bold'>Description</span>
              <span>{h.description}</span>
            </div>
            <div className='flex flex-col'>
              <span className='font-bold'>By</span>
              <span>{h.user_id}</span>
            </div>
            <div className='flex flex-col'>
              <span className='font-bold'>Time</span>
              <span>{h.Time}</span>
            </div>
          </div>
        )
      })}

    </div>
  )
}

export default History