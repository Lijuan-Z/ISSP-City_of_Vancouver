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
