'use client';

import { createContext, ReactNode, useEffect, useState } from 'react';
import fileInformation from '@/public/files2.json';
import { getFilesInformation } from '@/utils/backend/backend.utils';
import { FilterTagsType } from '@/components/FilterMenu/filter-menu';

type FileType = { url: string, section: string, 'webpage-title': string, 'file-name': string };

type FilesContextType = {
    files: FileType[],
    getFilterTagsType: (tags: string[]) => FilterTagsType
};

export const FilesContext = createContext<FilesContextType>({
    files: [],
    getFilterTagsType: () => ({
        categories: [],
            files: [],
    }),
});

export const FilesProviders = ({ children }: { children: ReactNode }) => {
    const [files, setFiles] = useState<FileType[]>([]);
    const dict = files.reduce((acc, item) => {
        acc[item['webpage-title']] = item;
        return acc;
    }, {} as { [key: string]: FileType });

    const getFilterTagsType = (tags: string[]) => {
        const filterTags = tags.reduce((filteredTags, item) => {
                if (item in dict) {
                    filteredTags.files.push(dict[item]['file-name']);
                } else {
                    filteredTags.categories.push(item);
                }
                return filteredTags;
        }, {
            categories: [],
            files: [],
        } as FilterTagsType);
        return filterTags;
    };
    const value = { files, getFilterTagsType };
    useEffect(() => {
        try {
            getFilesInformation().then(
                data => setFiles(data.data)
            );
        } catch (e) {
            console.log(e);
            setFiles([]);
        }
    }, []);
    return <FilesContext.Provider value={value}>
        {children}
           </FilesContext.Provider>;
};
