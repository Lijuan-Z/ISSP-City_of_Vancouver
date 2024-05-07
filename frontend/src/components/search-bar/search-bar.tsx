"use client"
import React, {useState, KeyboardEvent} from 'react';
import {FaSearch} from "react-icons/fa";
import {saveAs} from 'file-saver';

const SearchBar = () => {

    const [isLoading, setIsLoading] = useState<boolean>(false)
    const [error, setError] = useState<string | null>(null)

    async function onSearch(event: KeyboardEvent<HTMLInputElement>) {
        if (event.key !== 'Enter') return
        const queryValue = event.currentTarget.value
        console.log(queryValue)
        try {
            const response = await fetch(`http://127.0.0.1:8000/search?q=${queryValue}`)
            if (!response.ok) {
                throw new Error('Failed to submit the data. Please try again.')
            }
            const data = await response.blob()
            const fileName = `${queryValue}.xlsx`
            saveAs(data,fileName)
        } catch (err: unknown) {
            const error = err as Error
            console.log(error.message)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="w-full focus-within:border-orange-500 border-2">
            <div className="flex flex-row justify-items-center border border-vancouver-blue bg-white w-full">
                <input
                    type="search"
                    placeholder="Enter keyboard to search"
                    className="w-full py-2 pl-3 pr-3 appearance-none selection:appearance-none focus:outline-none"
                    onKeyDown={(e) => onSearch(e)}
                />
                <div className="flex items-center bg-white pr-2">
                    <FaSearch color={"#0484CB"}/>
                </div>
            </div>
        </div>
    );
};

export default SearchBar;