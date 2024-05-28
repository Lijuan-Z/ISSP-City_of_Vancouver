import React, { useContext, useEffect, useState } from 'react';
import { Button, Center, Dialog, LoadingOverlay, Notification, Stack, Text, Tooltip } from '@mantine/core';
import UpdateReminder from '@/components/UpdateReminder/update-reminder';
import FilterMenu from '@/components/FilterMenu/filter-menu';
import { FilesContext } from '@/contexts/files.context';
import {
    getLazerSearchProgress,
    getSearchTagsForLazer,
} from '@/utils/backend/backend.utils';

const LazerSearchBar = () => {
    const [filterTags, setFilterTags] = useState<string[]>([]);
    const [searchError, setSearchError] = useState('');
    const { getFilterTagsType } = useContext(FilesContext);
    const [backendSearching, setBackendSearching] = useState({
        data: '',
        file_ready: true,
    });
    const showError = !!searchError;
    const getLazerOutput = async () => {
        setBackendSearching({
            data: '',
            file_ready: false,
        });
        try {
            await getSearchTagsForLazer(getFilterTagsType(filterTags));
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
        getLazerSearchProgress().then(
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
    });

    return (
        <>
            <Stack>
                <UpdateReminder />

                <FilterMenu
                  filterMenuDescription="Select document(s) and/or document type(s) from the list:"
                  filterTags={filterTags}
                  setFilterTags={setFilterTags}
                />

                <Center pos="relative">
                    <LoadingOverlay
                      visible={!backendSearching.file_ready}
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
                <Text c="dimmed">{backendSearching.data}</Text>

            </Stack>
            <Dialog
              opened={showError}
              withCloseButton
              onClose={() => setSearchError('')}
              size="lg"
              radius="md"
              withBorder
            >
                <Notification title="Search Error" color="red" onClose={() => setSearchError('')}>
                    {searchError}
                </Notification>
            </Dialog>
        </>
    );
};

export default LazerSearchBar;
