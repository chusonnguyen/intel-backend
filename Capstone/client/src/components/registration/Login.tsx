import React, {useEffect, useState} from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import axios from 'axios'



const Login = () => {   
    let navigate = useNavigate()
    // localStorage.clear()
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
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

    const onChangeEmail = (e: { target: { value: any } }) => {
        setEmail(e.target.value)
        console.log(email)
    }
  
    const onChangePassword = (e: { target: { value: any } }) => {
        setPassword(e.target.value)
        console.log(password)
    }

    const handleSubmit = async (e: any) => {
        e.preventDefault()
        if(password != "" && email != "") {
            await axios.get('http://127.0.0.1:5000/login', {
                auth: {
                    username: email,
                    password: password
                }
            })
            .then(
                (response) => {
                    console.log(response.data.token)
                    localStorage.setItem("token", response.data.token)
                    navigate('/')
                },
                (error) => {
                    console.log(error.data)
                    setError("Fail to Login")
                }
            )
        } else {
            setError("Empty space")
        }

        
    }


    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 w-full h-full">
        {/* LEFT KV */}
        <div className='w-full h-full justify-center items-center bg-intel-blue hidden sm:flex'>
            <span className='text-white text-8xl'>Intel</span>
        </div>
        {/* RIGHT REGISTRATION */}
        <div className='min-w-[280px] w-full h-full flex flex-col justify-between items-center p-12 xs:pl-36'>
            {/* LOGO */}
            <div className='w-full flex justify-end items-end'>
                <span className='text-xl font-bold'>honeycomb</span>
            </div>
            {/* LOGIN SECTION */}
            <div className='flex flex-col justify-start items-start gap-14 w-full'>
                <span className='text-3xl font-bold'>Log in</span>
                <span className='text-3xl font-bold'>test@gmail.com</span>
                <div className='w-full flex flex-col justify-center items-start gap-6'>
                    <span className='text-sm font-semibold text-text-grey'>Log in using your email</span>
                    <span className='text-sm font-semibold text-text-grey'>{error}</span>

                    <form action="submit" onSubmit={handleSubmit}>
                        <div className='flex flex-col gap-4'>
                            <label htmlFor="email" className='text-xs'>Email</label>
                            <input onChange={onChangeEmail} type="email" className='bg-email-bg rounded-sm focus:bg-white focus:border focus:border-email-bg focus:outline-none px-3 py-2 text-xs'placeholder='Email address'/>
                        </div>
                        <div className='flex flex-col gap-4'>
                            <label htmlFor="password" className='text-xs'>Password</label>
                            <input onChange={onChangePassword} type="password" className='bg-email-bg rounded-sm focus:bg-white focus:border focus:border-email-bg focus:outline-none px-3 py-2 text-xs'placeholder='Password'/>
                        </div>
                        
                        <div className='w-full flex justify-between items-center'>
                            <button type='submit' className='bg-intel-blue text-white text-sm p-5 hover:bg-blue-400'>Log in</button>
                            <NavLink to={'/register'}>Sign up</NavLink>
                        </div>
                        
                    </form>
                </div>


            </div>
            {/* FOOTER */}
            <div>
                
            </div>
        </div>
      </div>
  )
}

export default Login