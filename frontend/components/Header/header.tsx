'use client';

import React from 'react';
import Image from 'next/image';
import { Box, Flex } from '@mantine/core';
// import LogoImage from '@/public/city_vancouver_logo.png';
import { ImageLoaderProps } from 'next/dist/shared/lib/image-config';
import Settings1 from '@/components/Settings/settings';

const Header = () => {
    const imageLoader = ({ src, width, quality } : ImageLoaderProps) => `http://localhost:3000/${src}?w=${width}&q=${quality || 75}`;

    return (
        <Box
          style={{
                position: 'relative',
            }}
        >
            {/*<Flex*/}
            {/*  justify="flex-end"*/}

            {/*>*/}
            {/*    <Text c="dimmed" size="sm">Dimmed text</Text>*/}
            {/*</Flex>*/}

            <Flex
              mih={50}
              gap="md"
              justify="space-between"
              align="center"
              direction="row"
              wrap="wrap"
              px={20}
            >
                <Image
                  loader={imageLoader}
                  src="./city_vancouver_logo.png"
                  alt="logo"
                  width={200}
                  height={100}
                />
                <Flex
                  align="center"
                >
                    <Settings1 />
                </Flex>
            </Flex>

        </Box>
    );
};

export default Header;
