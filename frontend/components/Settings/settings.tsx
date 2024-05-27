'use client';

import React from 'react';
import { useDisclosure } from '@mantine/hooks';
import { ActionIcon, Button, Modal } from '@mantine/core';
import { IconInfoCircle } from '@tabler/icons-react';
import Information from '@/components/Information/information';

const Settings1 = () => {
    const [opened, {
        open,
        close,
    }] = useDisclosure(false);

    return (
        <div>

            <Modal opened={opened} onClose={close} centered>
                <Information />
            </Modal>
            <Button
              variant="filled"
              aria-label="Settings"
              onClick={open}
              leftSection={
                    <IconInfoCircle
                      color="white"
                      size={30}
                      cursor="pointer"
                    />

                }
            >
                Update Files
            </Button>

        </div>);
};

export default Settings1;
