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
    Group, Divider, Text, Blockquote, Stack,
} from '@mantine/core';
import { IconInfoCircle, IconRobot } from '@tabler/icons-react';

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
    const showErrorPrompt = !!searchError;
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
            <Stack>

                <Box
                  style={{
                        maxWidth: '500px',
                    }}
                >
                    <Blockquote color="blue" iconSize={30} icon={<IconInfoCircle />} mt="sm" p={12}>
                        <Text size="xs">
                            Please update the files by clicking
                            the 'Update Files' button on the top right and clicking 'update'.
                        </Text>
                    </Blockquote>
                </Box>

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
                      onClick={toggle} />
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
                                }}>
                                Search
                            </Button>
                        </Tooltip>

                    </Center>
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
