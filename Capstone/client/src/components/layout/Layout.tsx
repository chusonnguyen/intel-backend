import React from 'react'
import { useParams } from 'react-router-dom'

const Layout = () => {
  let {id} = useParams()
  return (
    <div className='flex flex-col w-full gap-6'>
      <span className='font-bold text-2xl'>Layout of zone {id}</span>
      <div className='flex gap-4'>
        <span>Total space:</span><span>value</span>
      </div>
      <div className='flex gap-4'>
        <span>Usable space:</span><span>value</span>
      </div>
      <div className='flex gap-4'>
        <span>Honeycomb space:</span><span>value</span>
      </div>
      <img src="" alt="layout image" />
      <span className='font-bold text-2xl'>Statistic file</span>
      <div className='w-2/3 flex justify-between items-center border rounded-lg p-4'>
        <div className='flex flex-col'>
          <span className='font-bold'>No.</span>
          <span>Value</span>
        </div>
        <div className='flex flex-col'>
          <span className='font-bold'>Create Label</span>
          <span>Value</span>
        </div>
        <div className='flex flex-col'>
          <span className='font-bold'>X</span>
          <span>Value</span>
        </div>
        <div className='flex flex-col'>
          <span className='font-bold'>Y</span>
          <span>Value</span>
        </div>
        <div className='flex flex-col'>
          <span className='font-bold'>Width</span>
          <span>Value</span>
        </div>
        <div className='flex flex-col'>
          <span className='font-bold'>Length</span>
          <span>Value</span>
        </div>
      </div>

    </div>
  )
}

export default Layout