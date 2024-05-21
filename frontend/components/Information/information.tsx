import React, { useEffect, useState } from 'react';
import {
    Group,
    List,
    Paper,
    rem,
    ThemeIcon,
    Text,
    Progress,
    SimpleGrid,
    Box,
    Tooltip,
    Button,
    Center, RingProgress, Grid, Stack, LoadingOverlay, Loader,
} from '@mantine/core';
import {
    IconArrowDownRight,
    IconArrowUpRight,
    IconCircleCheck,
    IconCircleDashed,
    IconDeviceAnalytics, IconDownload, IconFile,
    IconPlayerPause, IconPlayerPlay, IconReload,
} from '@tabler/icons-react';
import classes from './information.module.css';
import { getUpdateInformation, updateFilesInBackend } from '@/utils/backend/backend.utils';

type StatusUpdate = {
    status: string;
    file_updated: number;
    last_updated: string;
    total_updated_files: number;
    percentage_updated: number;
};
const Information = () => {
    const [updateInfo, setUpdateInfo] = useState<StatusUpdate>(
        {
            file_updated: 0, last_updated: '', percentage_updated: 0, status: '', total_updated_files: 0,
        }
    );
    const [updating, setUpdating] = useState(false);
    const { file_updated, total_updated_files, percentage_updated, last_updated, status } = updateInfo;
    const UpdateIcon = updating ? IconPlayerPlay : IconPlayerPause;
    const updateFiles = () => {
        setUpdating(true);
        updateFilesInBackend()
            .catch(error => console.log(error));
    };

    const getNewUpdateInformation = () => {
        getUpdateInformation()
            .then(data => setUpdateInfo(data.data))
            .catch(error => console.log(error));
    };
    useEffect(() => {
        getNewUpdateInformation();
    }, []);

    useEffect(() => {
        switch (updateInfo.status) {
            case 'Idle':
                setUpdating(false);
                break;
            default:
                setUpdating(true);
                setTimeout(() => getNewUpdateInformation(), 1000);
        }
    }, [updateInfo]);
    console.log('infor', updateInfo);

    return (
        <Paper radius="md" p={10}>
            <Grid justify="space-between">
                <Stack>
                    <Group justify="space-between">
                        <Group align="flex-end" gap="xs">
                            <Text fz="xl" fw={700}>
                                Status:
                            </Text>
                            <Text c={updating ? 'teal' : 'blue'} className={classes.diff} fz="sm" fw={700}>
                                <span>{status}</span>
                                <UpdateIcon size="1rem" style={{ marginBottom: rem(4) }} stroke={1.5} />
                            </Text>
                        </Group>
                    </Group>
                    <Group justify="space-between">
                        <Group align="flex-end" gap="xs">
                            <Text fz="xl" fw={700}>
                                Total Files:
                            </Text>
                            <Text c="blue" className={classes.diff} fz="sm" fw={700}>
                                <span>{total_updated_files}</span>
                                <IconFile size="1rem" style={{ marginBottom: rem(4) }} stroke={1.5} />
                            </Text>
                        </Group>
                    </Group>
                    <Tooltip label="Last Updated Time">
                        <Text c="dimmed" fz="sm">
                            {last_updated}
                        </Text>
                    </Tooltip>

                </Stack>
                {
                    updating
                    &&
                    <RingProgress
                      size={80}
                      roundCaps
                      thickness={8}
                      sections={[{ value: percentage_updated, color: 'blue' }]}
                      label={
                            <Center>
                                <Text>{file_updated}</Text>
                            </Center>
                        }
                    />
                }

            </Grid>
            <Center>
                <Box pos="relative">
                    <LoadingOverlay visible={updating} zIndex={1000} overlayProps={{ radius: 'sm', blur: 2 }} className={classes.loader} />
                    <Button rightSection={<IconReload size={14} />} onClick={updateFiles}>Update</Button>

                </Box>
            </Center>
        </Paper>
    );
};

export default Information;
