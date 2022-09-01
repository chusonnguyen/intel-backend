import React, { useEffect, useState }  from 'react'
import { Link, NavLink, useNavigate} from 'react-router-dom'
import axios from 'axios'

const Signup = () => {
  let navigate = useNavigate()
  const [username, setUsername] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [error, setError] = useState("")

  useEffect(() => {
    const fetchToken = async () => {
        const token=localStorage.getItem('token')
        await axios.get(`http://127.0.0.1:5000/verify-token`, {
          headers: {
            'x-access-token': `${token}`
          }
        })
        .then(
          (response) => {
            console.log(response.status)
            if(response.status == 200) {
              navigate('/')
            }
            if(response.status == 401) {
              localStorage.clear()
            }
          },
          (error) => {
            console.log(error)
            localStorage.clear()
          }
        )
      }
    fetchToken()
},[])

  const onChangeUsername = (e: { target: { value: any } }) => {
      setUsername(e.target.value)
      console.log(username)
  }

  const onChangeEmail = (e: { target: { value: any } }) => {
      setEmail(e.target.value)
      console.log(email)
  }

  const onChangePassword = (e: { target: { value: any } }) => {
    setPassword(e.target.value)
    console.log(password)
  }

  const onChangeConfirmPassword = (e: { target: { value: any } }) => {
    setConfirmPassword(e.target.value)
    console.log(confirmPassword)
  }

  const headers = { 
    'Content-Type': 'application/json',
  }

  let data = {
    username: username,
    email: email,
    password:password
  }

  const handleSubmit = async (e: any) => {
    e.preventDefault()
    if(password != "" && confirmPassword != "" && username != "" && email != "") {
      if(password == confirmPassword) {
        await axios.post('http://127.0.0.1:5000/register', data, {
          headers:headers
        })
          .then((response) => {
            console.log(response);
            navigate('/login')
          }, 
          (error) => {
            console.log(error);
            setError("Fail to create account")
          });
        
      }
      else {
        setError("Invalid password")
        return console.log("invalid password")
      } 
    } else {
      setError("Invalid form")
      return console.log("invalid form")
    }
  }

  

  return (
    <div>
      <form action="submit" onSubmit={handleSubmit}>
        <span className='text-xs'>{error}</span>
          <div className='flex flex-col gap-4'>
              <label htmlFor="name" className='text-xs'>Username</label>
              <input onChange={onChangeUsername} type="text" className='bg-email-bg rounded-sm focus:bg-white focus:border focus:border-email-bg focus:outline-none px-3 py-2 text-xs'placeholder='Username'/>
          </div>
          <div className='flex flex-col gap-4'>
              <label htmlFor="email" className='text-xs'>Email</label>
              <input onChange={onChangeEmail} type="email" className='bg-email-bg rounded-sm focus:bg-white focus:border focus:border-email-bg focus:outline-none px-3 py-2 text-xs'placeholder='Email address'/>
          </div>
          <div className='flex flex-col gap-4'>
              <label htmlFor="password" className='text-xs'>Password</label>
              <input onChange={onChangePassword} type="password" className='bg-email-bg rounded-sm focus:bg-white focus:border focus:border-email-bg focus:outline-none px-3 py-2 text-xs'placeholder='Password'/>
          </div>
          <div className='flex flex-col gap-4'>
              <label htmlFor="password" className='text-xs'>Reconfirm Password</label>
              <input onChange={onChangeConfirmPassword} type="password" className='bg-email-bg rounded-sm focus:bg-white focus:border focus:border-email-bg focus:outline-none px-3 py-2 text-xs'placeholder='Reconfirm Password'/>
          </div>
          <div className='w-full flex justify-between items-center'>
              <button type='submit' className='bg-intel-blue text-white text-sm p-5 hover:bg-blue-400'>Sign up</button>
              <NavLink to={'/login'}>Log in</NavLink>
          </div>
        </form>
    </div>
  )
}

export default Signup