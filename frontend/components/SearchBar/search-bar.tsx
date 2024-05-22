'use client';

import React, { useState, KeyboardEvent, SetStateAction, Dispatch, useContext, forwardRef } from 'react';
import { saveAs } from 'file-saver';
import {
    ActionIcon,
    Box,
    Button, Center,
    Flex,
    LoadingOverlay,
    TagsInput,
    TextInputProps, Tooltip,
    Notification,
    useMantineTheme, Dialog,
} from '@mantine/core';
import { IconSearch } from '@tabler/icons-react';
import { rem } from 'polished';
import FilterMenu, { FilterTagsType } from '@/components/FilterMenu/filter-menu';
import { searchKeywords } from '@/utils/backend/backend.utils';
import { FilesContext } from '@/contexts/files.context';

type InputPropsType = {
    keywords: string[]
    setKeywords: Dispatch<SetStateAction<string[]>>
} & TextInputProps;

export const InputWithButton = forwardRef<TextInputProps, InputPropsType>(({
                                                                               setKeywords,
                                                                               keywords,
                                                                           }, ref) => {
    const theme = useMantineTheme();
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [errorLocal, setError] = useState<String | null>(null);

    async function onSearch(event: KeyboardEvent<HTMLInputElement>) {
        if (event.key !== 'Enter') return;
        const queryValue = event.currentTarget.value;
        const values = queryValue.split(',');
        console.log(values);
        console.log(queryValue);
        try {
            setError(null);
            const response = await fetch(`/search?q=${queryValue}`);
            if (!response.ok) {
                throw new Error('Failed to submit the data. Please try again.');
            }
            const data = await response.blob();
            const fileName = `${queryValue}.xlsx`;
            saveAs(data, fileName);
        } catch (err: unknown) {
            const erro = err as Error;
            setError(erro.message);
        } finally {
            setIsLoading(false);
        }
    }

    return <TagsInput
      ref={ref}
      placeholder="Search keyword(s)..."
      data={[]}
      value={keywords}
      onChange={setKeywords}
      clearable
      style={{
            minWidth: '400px',
            maxWidth: '400px',
        }}
      leftSection={
            <ActionIcon size={32} radius="xl" color={theme.primaryColor} variant="white">
                <IconSearch
                  style={{
                        width: rem(18),
                        height: rem(18),
                    }}
                  stroke={1.5} />
            </ActionIcon>
        } />;
});

const SearchBar1 = () => {
    const [keywords, setKeywords] = useState<string[]>([]);
    const [filterTags, setFilterTags] = useState<string[]>(['All']);
    const [searchError, setSearchError] = useState('');
    const { getFilterTagsType } = useContext(FilesContext);
    const searchKeyWords = () => {
        console.log(keywords, filterTags);
        try {
            searchKeywords(keywords, getFilterTagsType(filterTags))
                .catch(error => setSearchError(error.message));
        } catch (e) {
            console.log(e);
        }
    };

    return (
        <>
            <Box>
                <Flex
                  direction="column"
                  gap={6}
                  justify="center"
                >
                    <Tooltip label={"Press Enter or ',' to add a new keyword"}>
                        <InputWithButton
                          keywords={keywords}
                          setKeywords={setKeywords}
                        />
                    </Tooltip>
                    <FilterMenu
                      filterTags={filterTags}
                      setFilterTags={setFilterTags}
                        // keepFiltersConsistent={keepFilterTagsConsistent}
                    />
                    <Center pos="relative">
                        <LoadingOverlay
                          visible={false}
                          zIndex={1000}
                          overlayProps={{
                                radius: 'sm',
                                blur: 2,
                            }} />
                        <Tooltip
                          label={keywords.length === 0 ? 'Need at least one Keyword and Tag' : 'Search Keyword(s)'}>
                            <Button
                              variant="filled"
                              radius="xs"
                              disabled={keywords.length === 0 || filterTags.length === 0}
                              onClick={searchKeyWords}
                              style={{
                                    width: '100px',
                                }}>Search

                            </Button>
                        </Tooltip>

                    </Center>
                </Flex>
            </Box>
            <Dialog
              opened={searchError}
              withCloseButton
              onClose={() => setSearchError('')}
              size="lg"
              radius="md"
              withBorder>
                <Notification title="Search Error" color="red" onClose={() => setSearchError('')}>
                    {searchError}
                </Notification>
            </Dialog>
        </>

    );
};
export default SearchBar1;
