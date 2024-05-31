import React, { ReactNode } from 'react';
import { Blockquote, Box, Text } from '@mantine/core';

type ReminderType = {
    message: string
    color: string
    icon: ReactNode
};
const UpdateReminder = ({ message, color, icon }: ReminderType) => (
    <Box
      style={{
            maxWidth: '500px',
        }}
    >
        <Blockquote color={color} iconSize={30} icon={icon} mt="sm" p={12}>
            <Text size="xs">
                {message}
            </Text>
        </Blockquote>
    </Box>
);

export default UpdateReminder;
