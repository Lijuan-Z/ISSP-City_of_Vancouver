'use client';

import React, { useState, useContext, useEffect } from 'react';
import {
    Button, Center,
    Flex,
    LoadingOverlay,
    Tooltip,
    Notification,
    Dialog,
    Group, Text, Stack,
} from '@mantine/core';
import { IconAlertTriangle, IconInfoCircle } from '@tabler/icons-react';

import FilterMenu from '@/components/FilterMenu/filter-menu';
import { getConsequentialSearchProgress, searchKeywords } from '@/utils/backend/backend.utils';
import { FilesContext } from '@/contexts/files.context';
import InputBar from '@/components/InputBar/input-bar';
import UpdateReminder from '@/components/UpdateReminder/update-reminder';

const SearchBar1 = () => {
    const [keywords, setKeywords] = useState<string[]>([]);
    const [filterTags, setFilterTags] = useState<string[]>(['All']);
    const [searchError, setSearchError] = useState('');
    const [backendSearching, setBackendSearching] = useState({
        ai: '',
        file_ready: true,
    });
    const showErrorPrompt = !!searchError;
    const enableSearch = keywords.length !== 0
        && filterTags.length !== 0;
    const { getFilterTagsType } = useContext(FilesContext);
    const searchKeyWords = async () => {
        setBackendSearching({
            ai: '',
            file_ready: false,
        });
        try {
            await searchKeywords(keywords,
                getFilterTagsType(filterTags),
            );
            getSearchStatus();
        } catch (error) {
            if (error instanceof Error) {
                setSearchError(error.message);
            } else {
                setSearchError('An unexpected error occurred.');
            }
        }
    };

    const getSearchStatus = () => {
        getConsequentialSearchProgress().then(
            data => {
                const fileReady = data.data;

                setBackendSearching(fileReady);
            }
        ).catch(
            error => {
                setBackendSearching(prev => ({
                    ...prev,
                    file_ready: true,
                }));
                setSearchError(error.message);
            }
        );
    };

    useEffect(() => {
        getSearchStatus();
    }, []);

    useEffect(() => {
        if (!backendSearching.file_ready) {
            setTimeout(() => getSearchStatus(), 5000);
        }
    }, [backendSearching]);

    return (
        <>
            <Stack>

                <UpdateReminder
                  color="blue"
                  icon={<IconInfoCircle />}
                  message="Please update the files by clicking the
                &apos;Update Files&apos; button on the top right
                and clicking &apos;update&apos;."
                />

                <Flex
                  direction="column"
                  gap={6}
                  justify="center"
                >
                    <Tooltip label={"Press Enter or ',' to add a new keyword"}>
                        <InputBar
                          keywords={keywords}
                          setKeywords={setKeywords}
                          inputBarDescription={"Type in a keyword(s) below, press 'enter' or ',' to separate keywords:"}
                        />
                    </Tooltip>
                    <Group>
                        <FilterMenu
                          filterTags={filterTags}
                          setFilterTags={setFilterTags}
                          filterMenuDescription="Select document(s) and/or document type(s) from the list:"
                            // keepFiltersConsistent={keepFilterTagsConsistent}
                        />
                    </Group>
                    <Center pos="relative">
                        <LoadingOverlay
                          visible={!backendSearching.file_ready}
                          zIndex={199}
                          overlayProps={{
                                radius: 'sm',
                                blur: 2,
                            }} />
                        <Tooltip
                          label={!enableSearch ? 'Need at least one Keyword and Tag' : 'Search Keyword(s)'}>
                            <Button
                              variant="filled"
                              radius="xs"
                              disabled={!enableSearch}
                              onClick={searchKeyWords}
                              style={{
                                    width: '100px',
                                }}>
                                Search
                            </Button>
                        </Tooltip>

                    </Center>
                    <Text c="dimmed">{backendSearching.ai}</Text>

                </Flex>
                <UpdateReminder
                  color="red"
                  icon={<IconAlertTriangle />}
                  message="Do not close the black
                  screen application window
                  until you decide to exit the application." />
            </Stack>
            <Dialog
              opened={showErrorPrompt}
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
