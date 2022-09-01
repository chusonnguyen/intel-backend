import React, {useEffect} from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import axios from 'axios'

const SideNav = () => {
  return (
    <div className='basis-96'>
        <ul className='flex flex-col gap-20 p-6'>
            <li >
                <NavLink className='p-4 border' to={'dashboard'}>Dashboard</NavLink>
            </li>
            <li>
                <NavLink className='p-4 border' to={'history'}>History</NavLink>
            </li>
            <li>
                <NavLink className='p-4 border' to={'projects'}>Projects</NavLink>
            </li>
        </ul>
    </div>
  )
}

export default SideNav