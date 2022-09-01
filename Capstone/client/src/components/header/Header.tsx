import React, { useEffect, useState }  from 'react'
import { Link, NavLink, useNavigate} from 'react-router-dom'
import axios from 'axios'

const Header = () => {
  let navigate = useNavigate()
  const [username, setUsername] = useState("")
  const token=localStorage.getItem('token')

  const fetchUser = async () => {
    await axios.get('http://127.0.0.1:5000/a_user', {
      headers: {
        'x-access-token': `${token}`
      }
    })
    .then(
      (response) => {
        console.log(response.status)
        if(response.status == 200) {
          console.log(response.data.user.username)
          setUsername(response.data.user.username)
        }
        if(response.status == 401) {
          localStorage.clear()
          navigate('/login')
        }
      }, 
      (error) => {
        console.log(error)
      }
    )
  }

  const logout = async () => {
    await axios.get(`http://127.0.0.1:5000/logout`, {
      headers: {
        'x-access-token': `${token}`
      }
    })
    .then(
      (response) => {
        console.log(response.status)
        if(response.status == 200) {
          localStorage.clear()
          navigate('/login')
        }
        if(response.status == 401) {
        }
      },
      (error) => {
        console.log(error)
      }
    )
  }

  const handleClick = () => {
    logout()
  }

  useEffect(() => {
    fetchUser()
  })

  return (
    <div className='w-full flex justify-between items-center p-6'>
        <span>{username}</span>
        <button onClick={handleClick} >Log out</button>
    </div>
  )
}

export default Header