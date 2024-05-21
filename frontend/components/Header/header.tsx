import React from 'react';
import Image from 'next/image';
import { Box, Button, Flex, Text } from '@mantine/core';
import Settings1 from '@/components/Settings/settings';

const Header = () => (
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
              src="/city_vancouver_logo.png"
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

export default Header;
