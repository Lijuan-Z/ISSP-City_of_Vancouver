'use client';

import React, { useContext, useState } from 'react';
import { Box, Button, Center, Dialog, Flex, LoadingOverlay, Notification, Stack, Tooltip } from '@mantine/core';
import FilterMenu from '@/components/FilterMenu/filter-menu';
import { FilesContext } from '@/contexts/files.context';
import { getSearchTagsForLazer } from '@/utils/backend/backend.utils';
import UpdateReminder from '@/components/UpdateReminder/update-reminder';
import SearchBar1 from '@/components/SearchBar/search-bar';
import LazerSearchBar from '@/components/LazerSearchBar/lazer-search-bar';

const Lazer = () => (
        <Box
          style={{
                height: '100%',
            }}
        >
            <Center
              h="100%"
            >
                <LazerSearchBar />
            </Center>
        </Box>
    );

export default Lazer;
