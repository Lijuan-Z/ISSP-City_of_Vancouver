'use client';

import { Text, rem, ActionIcon, TagsInput, TagsInputProps, Group, Flex } from '@mantine/core';
import {
    IconExternalLink, IconAdjustmentsHorizontal,
} from '@tabler/icons-react';
import React, { Dispatch, SetStateAction, useContext } from 'react';
import { theme } from '@/theme';
import { FilesContext } from '@/contexts/files.context';

export type FilterTagsType = {
    categories: string[]
    files: string[]

};
type FilterMenuProps = {
    filterTags: string[]
    setFilterTags: Dispatch<SetStateAction<string[]>>,
    // keepFiltersConsistent: (tags: string[]) => void
};

function FilterMenu({
                        filterTags,
                        setFilterTags,

                    }: FilterMenuProps) {
    console.log(filterTags);
    const { files: fileData } = useContext(FilesContext);
    const fileNames = fileData.map(item => item['webpage-title']);

    const options: Record<string, { url: string, id: number }> = fileData.reduce((acc, item) => {
        const key = item['webpage-title'];
        acc[key] = {
            url: item.url,
            id: 1,
        };
        return acc;
    }, {} as { [key: string]: { url: string, id: number } });
    const renderTagsInputOption: TagsInputProps['renderOption'] = ({ option }) => (
        <Group>
            <Flex
              justify="space-between"
            >
                <Text>{option.value}</Text>
                {
                    options[option.value].url &&
                    <ActionIcon
                      size={32}
                      radius="xl"
                      color={theme.primaryColor}
                      variant="white"
                      onClick={(e) => {
                            e.stopPropagation();
                            window.open(options[option.value].url, '_blank', 'noreferrer'
                            );
                        }}
                    >
                        <IconExternalLink
                          style={{
                                width: rem(18),
                                height: rem(18),
                            }}
                          stroke={1.5} />
                    </ActionIcon>
                }
            </Flex>
        </Group>
    );

    const categories = fileData.reduce((acc, item) => {
        if (!acc[item.section]) {
            acc[item.section] = item.section;
        }
        return acc;
    }, { All: 'All' } as { [key: string]: string });
    const categoriesKeys = Object.keys(categories);
    categoriesKeys.reduce((acc, key) => {
        acc[key] = {
            url: '',
            id: 0,
        };
        return acc;
    }, options);
    const newSet = new Set(fileNames);
    const dropdownData = [
        {
            group: 'Categories',
            items: Object.keys(categories),
        },
        {
            group: 'Files',
            items: Array.from(newSet),
        },
    ];

    return (
        <TagsInput
          leftSection={
                <ActionIcon size={32} radius="xl" color={theme.primaryColor} variant="white">
                    <IconAdjustmentsHorizontal
                      style={{
                            width: rem(18),
                            height: rem(18),
                        }}
                      stroke={1.5} />
                </ActionIcon>
            }
          style={{
                minWidth: '350px',
                maxWidth: '350px',
            }}
          placeholder="Filter tags"
          data={dropdownData}
          onClear={() => setFilterTags(['All'])}
          clearable
            // onSearchChange={}
            // onOptionSubmit={(value) => console.log(value)}
          onChange={setFilterTags}
          value={filterTags}
            // defaultValue={['All']}
          renderOption={renderTagsInputOption}
        />
    );
}

export default FilterMenu;