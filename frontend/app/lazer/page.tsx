'use client';

import React from 'react';
import { Box, Center } from '@mantine/core';

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
