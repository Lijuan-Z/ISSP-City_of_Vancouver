'use client';

import React, { useState, useContext } from 'react';
import {
    Box,
    Button, Center,
    Flex,
    LoadingOverlay,
    Tooltip,
    Notification,
    Dialog,
    Checkbox,
    Group,
} from '@mantine/core';
import { IconRobot } from '@tabler/icons-react';

import { useDisclosure, useInputState } from '@mantine/hooks';
import FilterMenu from '@/components/FilterMenu/filter-menu';
import { searchKeywords } from '@/utils/backend/backend.utils';
import { FilesContext } from '@/contexts/files.context';
import Prompt from '@/components/Prompt/prompt';
import InputBar from '@/components/InputBar/input-bar';

const SearchBar1 = () => {
    const [keywords, setKeywords] = useState<string[]>([]);
    const [filterTags, setFilterTags] = useState<string[]>(['All']);
    const [openedTextBox, { toggle }] = useDisclosure(false);
    const [prompt, setPrompt] = useInputState('');
    const [searchError, setSearchError] = useState('');
    const enableSearch = openedTextBox ? prompt.length !== 0
        && keywords.length !== 0
        && filterTags.length !== 0 : keywords.length !== 0
        && filterTags.length !== 0;
    const { getFilterTagsType } = useContext(FilesContext);
    const searchKeyWords = () => {
        try {
            searchKeywords(keywords, getFilterTagsType(filterTags), openedTextBox, prompt)
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
                        <InputBar
                          keywords={keywords}
                          setKeywords={setKeywords}
                        />
                    </Tooltip>
                    <Group>
                        <FilterMenu
                          filterTags={filterTags}
                          setFilterTags={setFilterTags}
                            // keepFiltersConsistent={keepFilterTagsConsistent}
                        />
                        <Checkbox
                          labelPosition="left"
                          icon={IconRobot}
                          label="A.I"
                          onClick={toggle} />
                    </Group>
                    <Prompt text={prompt} setText={setPrompt} opened={openedTextBox} />
                    <Center pos="relative">
                        <LoadingOverlay
                          visible={false}
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
