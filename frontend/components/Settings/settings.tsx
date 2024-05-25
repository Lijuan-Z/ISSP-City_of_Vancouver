'use client';

import React from 'react';
import { useDisclosure } from '@mantine/hooks';
import { ActionIcon, Modal } from '@mantine/core';
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
            <ActionIcon variant="transparent" aria-label="Settings">
                <IconInfoCircle
                  color="#0484CB"
                  size={30}
                  onClick={open}
                  cursor="pointer"
                />
            </ActionIcon>

        </div>);
};

export default Settings1;
