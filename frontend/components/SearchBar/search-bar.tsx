'use client';

import React, { useState, useContext, useEffect } from 'react';
import {
    Button, Center,
    Flex,
    LoadingOverlay,
    Tooltip,
    Notification,
    Dialog,
    Checkbox,
    Group, Divider, Text, Stack,
} from '@mantine/core';
import { IconRobot } from '@tabler/icons-react';

import { useDisclosure, useInputState } from '@mantine/hooks';
import FilterMenu from '@/components/FilterMenu/filter-menu';
import { getConsequentialSearchProgress, searchKeywords } from '@/utils/backend/backend.utils';
import { FilesContext } from '@/contexts/files.context';
import Prompt from '@/components/Prompt/prompt';
import InputBar from '@/components/InputBar/input-bar';
import UpdateReminder from '@/components/UpdateReminder/update-reminder';

const SearchBar1 = () => {
    const [keywords, setKeywords] = useState<string[]>([]);
    const [filterTags, setFilterTags] = useState<string[]>(['All']);
    const [openedTextBox, { toggle }] = useDisclosure(false);
    const [sectionChecked, { toggle: toggleSection }] = useDisclosure(false);
    const [prompt, setPrompt] = useInputState('');
    const [searchError, setSearchError] = useState('');
    const [backendSearching, setBackendSearching] = useState({
        ai: '',
        file_ready: true,
    });
    const showErrorPrompt = !!searchError;
    const enableSearch = openedTextBox ? prompt.length !== 0
        && keywords.length !== 0
        && filterTags.length !== 0 : keywords.length !== 0
        && filterTags.length !== 0;
    const { getFilterTagsType } = useContext(FilesContext);
    const searchKeyWords = async () => {
        setBackendSearching({
            ai: '',
            file_ready: false,
        });
        try {
            await searchKeywords(keywords, getFilterTagsType(filterTags), openedTextBox, prompt, sectionChecked);
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

                <UpdateReminder />

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
                    <Divider my="md" />
                    <Checkbox
                      labelPosition="left"
                      icon={IconRobot as any}
                      label="Generate Consequential Amendments"
                      onClick={toggle}
                      checked={openedTextBox}
                    />
                    <Checkbox
                      labelPosition="left"
                      icon={IconRobot as any}
                      label="Generate Sections"
                      onClick={toggleSection}
                      checked={sectionChecked}
                    />
                    <Prompt text={prompt} setText={setPrompt} opened={openedTextBox} />
                    <Center pos="relative">
                        <LoadingOverlay
                          visible={!backendSearching.file_ready}
                          zIndex={1000}
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
