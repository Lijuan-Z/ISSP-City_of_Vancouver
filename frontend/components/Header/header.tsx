'use client';

import React from 'react';
import Image from 'next/image';
import { Box, Button, Flex } from '@mantine/core';
// import LogoImage from '@/public/city_vancouver_logo.png';
import { ImageLoaderProps } from 'next/dist/shared/lib/image-config';
import { IconExternalLink } from '@tabler/icons-react';
import Settings1 from '@/components/Settings/settings';
import AppTitle from '@/components/AppTitle/app-title';

const Header = () => {
    const imageLoader = ({
                             src,
                             width,
                             quality,
                         }: ImageLoaderProps) => `http://localhost:8000/${src}?w=${width}&q=${quality || 75}`;

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
                  src="static/city_vancouver_logo.png"
                  alt="logo"
                  width={200}
                  height={100}
                />
                <AppTitle />
                <Flex
                  align="center"
                  gap={10}
                >
                    {
                        //TODO: Add link to the manual
                    }
                    <a
                      href="static/user_manual.pdf"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                        <Button
                          variant="filled"
                          aria-label="manual"
                          leftSection={
                                <IconExternalLink
                                  color="white"
                                  size={30}
                                  cursor="pointer"
                                />

                            }
                        >
                            Manual
                        </Button>

                    </a>
                    <Settings1 />
                </Flex>
            </Flex>

        </Box>
    );
};

export default Header;
