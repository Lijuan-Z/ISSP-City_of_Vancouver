'use client';

import React, { useContext, useState } from 'react';
import { Button, Center, Dialog, Flex, LoadingOverlay, Notification, Tooltip } from '@mantine/core';
import FilterMenu, { FilterTagsType } from '@/components/FilterMenu/filter-menu';
import { FilesContext, FilesProviders } from '@/contexts/files.context';

const Lazer = () => {
    const [filterTags, setFilterTags] = useState<string[]>([]);
    const [searchError, setSearchError] = useState('');
    const { getFilterTagsType } = useContext(FilesContext);
    return (
        <>
            <Flex
              direction="column"
              gap={6}
              justify="center"
            >
                <Center>
                    <FilterMenu
                      filterTags={filterTags}
                      setFilterTags={setFilterTags}
                    />
                </Center>
                <Center pos="relative">
                    <LoadingOverlay
                      visible={false}
                      zIndex={1000}
                      overlayProps={{
                            radius: 'sm',
                            blur: 2,
                        }} />
                    <Tooltip
                      label={filterTags.length === 0 ? 'Need at least one Tag' : 'Search Tag(s)'}>
                        <Button
                          variant="filled"
                          radius="xs"
                          disabled={filterTags.length === 0}
                          onClick={() => {
                              setSearchError('Testing');
                            }}
                          style={{
                                width: '100px',
                            }}>Search

                        </Button>
                    </Tooltip>

                </Center>

            </Flex>
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

export default Lazer;
