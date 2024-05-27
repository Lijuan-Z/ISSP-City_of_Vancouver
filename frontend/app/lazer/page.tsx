'use client';

import React, { useContext, useState } from 'react';
import { Button, Center, Dialog, Flex, LoadingOverlay, Notification, Tooltip } from '@mantine/core';
import FilterMenu from '@/components/FilterMenu/filter-menu';
import { FilesContext } from '@/contexts/files.context';
import { getSearchTagsForLazer } from '@/utils/backend/backend.utils';

const Lazer = () => {
    const [filterTags, setFilterTags] = useState<string[]>([]);
    const [searchError, setSearchError] = useState('');
    const { getFilterTagsType } = useContext(FilesContext);
    const showError = !!searchError;
    const getLazerOutput = () => {
        getSearchTagsForLazer(getFilterTagsType(filterTags))
            .catch(error => setSearchError(error.message));
    };
    return (
        <>
            <Flex
              direction="column"
              gap={6}
              justify="center"
            >
                <Center>
                    <FilterMenu
                      filterMenuDescription="Select document(s) and/or document type(s) from the list:"
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
                          onClick={getLazerOutput}
                          style={{
                                width: '100px',
                            }}>Search

                        </Button>
                    </Tooltip>

                </Center>

            </Flex>
            <Dialog
              opened={showError}
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
