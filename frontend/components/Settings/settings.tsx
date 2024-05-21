'use client';

import React, { ChangeEvent, useRef, useState } from 'react';
import { IoSettingsSharp } from 'react-icons/io5';
import { FaSearch } from 'react-icons/fa';
import { useDisclosure } from '@mantine/hooks';
import { ActionIcon, Button, Modal } from '@mantine/core';
import { IconInfoCircle } from '@tabler/icons-react';
import SearchBar from '@/components/SearchBar/search-bar';
import Information from "@/components/Information/information";

type SettingsType = {
    scrapeURL: string
    folderPath: string
};
const Settings = () => {
    const [showModal, toggleModal] = useState(false);
    const [settingsValues, setSettingsValues] = useState<SettingsType>({
        folderPath: '',
        scrapeURL: 'https://vancouver.ca/home-property-development/zoning-and-land-use-policies-document-library.aspx',
    });
    const {
        folderPath,
        scrapeURL,
    } = settingsValues;
    console.log(showModal);
    const directoryInputRef = useRef(null);

    const handleSelectFolder = () => {
        directoryInputRef?.current?.click();
    };

    const handleFolderChange = (e: ChangeEvent<HTMLInputElement>) => {
        const selectedFolder = e.target.files?.[0];
        console.log(selectedFolder); // Use the selected folder path in your app
    };

    const directoryPicker = async () => {
        const dirHandle = await window.showDirectoryPicker();
        console.log(dirHandle);
    };
    return (
        <div
          className="mr-9 relative hover:cursor-pointer"
        >
            <IoSettingsSharp
              color="#0484CB"
              size={30}
              onClick={() => toggleModal(prev => !prev)}

            />
            {
                showModal &&
                (
                    <div
                      className="fixed inset-0 flex items-center justify-center z-50"
                      onClick={() => toggleModal(false)}>
                        <div
                          className="bg-white p-6 shadow-md w-1/3 opacity-90 "
                          onClick={(e) => {
                                e.stopPropagation();
                            }}>
                            <h1 className="font-semibold mb-4">Settings</h1>
                            <p>URL</p>
                            <div className="w-full focus-within:border-orange-500 border-2">
                                <div
                                  className="flex flex-row justify-items-center border border-vancouver-blue bg-white w-full">
                                    <input
                                      type="search"
                                      placeholder="URL"
                                      className="w-full py-2 pl-3 pr-3 appearance-none selection:appearance-none focus:outline-none"
                                      value={scrapeURL}
                                      onChange={(e) => setSettingsValues(prevState => (
                                            {
                                                ...prevState,
                                                scrapeURL: e.target.value,

                                            }
                                        ))}
                                    />
                                </div>
                            </div>
                            <p>Folder Path</p>
                            <div className="w-full focus-within:border-orange-500 border-2">
                                <div
                                  className="flex flex-row justify-items-center border border-vancouver-blue bg-white w-full">
                                    <input
                                      type="search"
                                      placeholder="path"
                                      className="w-full py-2 pl-3 pr-3 appearance-none selection:appearance-none focus:outline-none"
                                    />
                                    <input
                                      ref={directoryInputRef}
                                      type="file"
                                      style={{ display: 'none' }}
                                      onChange={(e) => handleFolderChange(e)}
                                    />
                                    <button
                                      type="button"
                                      className="bg-vancouver-blue text-white py-2 min-w-28"
                                      onClick={directoryPicker}
                                    >
                                        Select
                                    </button>
                                </div>
                            </div>
                            <div className="flex justify-end mt-2">
                                <button
                                  type="button"
                                  className="text-blue-500 border border-red-500 hover:text-blue-700 mr-4 py-2 min-w-28"
                                  onClick={() => toggleModal(false)}
                                >
                                    Cancel
                                </button>
                                <button
                                  type="button"
                                  className="bg-vancouver-green text-white py-2 min-w-28"
                                  onClick={() => {
                                        toggleModal(false);
                                    }}
                                >
                                    Save
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }
        </div>
    );
};

const Settings1 = () => {
    const [opened, {
        open,
        close,
    }] = useDisclosure(false);

    return (
        <div>

            <Modal opened={opened} onClose={close} centered>
               <Information />
            </Modal>
            <ActionIcon variant="transparent" aria-label="Settings">
                <IconInfoCircle
                  color="#0484CB"
                  size={30}
                  onClick={open}
                  cursor="pointer"
                />
            </ActionIcon>

        </div>);
};

export default Settings1;
