import { Collapse, Textarea, Text } from '@mantine/core';
import React, { ChangeEvent } from 'react';

type PromptPropsType = {
    opened: boolean
    text: string
    setText: (value: string | ChangeEvent<any> | null | undefined) => void
};
const Prompt = ({ opened, text, setText }: PromptPropsType) => (

    <Collapse in={opened}>
        <Text c="dimmed" size="xs">
            Please type your AI prompt to identify texts in need of change and to
            propose a consequential amendment and
        </Text>
        <Text c="dimmed" size="xs">
            specify your rationale
        </Text>

        <Text c="dimmed" size="xs">
            For example:
        </Text>
        <Text c="dimmed" size="xs">
            1: Replace &apos;RS-1&apos; with &apos;R1-1&apos;
        </Text>
        <Text c="dimmed" size="xs">
            2: Remove references to specific numbers of parking spaces, and
            replace them with &apos;See Parking Bylaw&apos;.
        </Text>
        <Text c="dimmed" size="xs">
            The &apos;Rationale&apos; column in the output table
            can read &apos;Remove&apos; outdated minimum parking space requirements
        </Text>
        <Text c="dimmed" size="xs">
            and ensure alignment with &apos;Parking By-law&apos;
        </Text>

        <Textarea
          style={{
                maxWidth: '600px',
            }}
          withAsterisk
          placeholder="Add your AI prompt here..."
          autosize
          minRows={5}
          value={text}
          onChange={setText}
        />
    </Collapse>

);

export default Prompt;
