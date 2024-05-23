import { saveAs } from 'file-saver';
import { FilterTagsType } from '@/components/FilterMenu/filter-menu';

export const searchKeywords = async (keywords: string[], filterTags: FilterTagsType) => {
    console.log(filterTags);
    const requestBody = {
        data: {
            'search-terms': keywords,
            files: filterTags.files,
            categories: filterTags.categories,
        },
    };
    console.log(requestBody);
    const response = await fetch('/search', {
        method: 'POST',
        body: JSON.stringify(requestBody),
        headers: {
            'Content-type': 'application/json',
        },
    });
    if (!response.ok) {
        throw new Error('Failed to submit the data. Please try again.');
    }
    const data = await response.blob();
    const fileName = 'ouptut.xlsx';
    saveAs(data, fileName);
};

export const getFilesInformation = async () => {
    const response = await fetch('/data');
    if (!response.ok) {
        throw new Error('Failed to submit the data. Please try again.');
    }
    const data = response.json();
    return data;
};

export const getUpdateInformation = async () => {
    const response = await fetch('/update/info');
    if (!response.ok) {
        throw new Error('Failed to submit the data. Please try again.');
    }
    const data = response.json();
    return data;
};

export const updateFilesInBackend = async () => {
    const response = await fetch('/update');
    if (!response.ok) {
        throw new Error('Failed to submit the data. Please try again.');
    }
};

export const getSearchTagsForLazer = async (filterTags: FilterTagsType) => {
    console.log(filterTags);
    const requestBody = {
        data: {
            files: filterTags.files,
            categories: filterTags.categories,
        },
    };
    console.log(requestBody);
    const response = await fetch('/search/o3', {
        method: 'POST',
        body: JSON.stringify(requestBody),
        headers: {
            'Content-type': 'application/json',
        },
    });
    if (!response.ok) {
        throw new Error('Failed to submit the data. Please try again.');
    }
    const data = await response.blob();
    const fileName = 'ouptut.xlsx';
    saveAs(data, fileName);
};

export const getSearchProgress = async () => {
    const response = await fetch('/search/info');
    if (!response.ok) {
        throw new Error('Failed to submit the data. Please try again.');
    }
    const data = response.json();
    return data;
};
