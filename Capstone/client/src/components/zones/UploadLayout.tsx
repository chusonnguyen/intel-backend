import React from 'react'
import { useParams } from 'react-router-dom'

const UploadLayout = () => {
    let {id} = useParams()
  return (
    <div>
        <span>Create Zone for project {id}</span>

        <form action="submit">
            <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300" htmlFor="file_input">Upload image</label>
            <input className="block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" aria-describedby="file_input_help" id="file_input" type="file" />
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-300" id="file_input_help">JPEG, PNG</p>
            
            <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300" htmlFor="file_input">Upload raw tool list</label>
            <input className="block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" aria-describedby="file_input_help" id="file_input" type="file" />
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-300" id="file_input_help">XLSX or CSV</p>

            <div className='w-full flex justify-between items-center'>
                <button type='submit' className='bg-intel-blue text-white text-sm p-5 hover:bg-blue-400'>Create</button>
            </div>
        </form>
    </div>
  )
}

export default UploadLayout