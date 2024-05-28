import React from 'react';
import { Blockquote, Box, Text } from '@mantine/core';
import { IconInfoCircle } from '@tabler/icons-react';

const UpdateReminder = () => (
    <Box
      style={{
            maxWidth: '500px',
        }}
    >
        <Blockquote color="blue" iconSize={30} icon={<IconInfoCircle />} mt="sm" p={12}>
            <Text size="xs">
                Please update the files by clicking the
                &apos;Update Files&apos; button on the top right
                and clicking &apos;update&apos;.
            </Text>
        </Blockquote>
    </Box>
);

export default UpdateReminder;
