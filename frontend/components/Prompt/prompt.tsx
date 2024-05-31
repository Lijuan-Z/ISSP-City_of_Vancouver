import { Collapse, Textarea } from '@mantine/core';
import React, { ChangeEvent } from 'react';

type PromptPropsType = {
    opened: boolean
    text: string
    setText: (value: string | ChangeEvent<any> | null | undefined) => void
};
const Prompt = ({ opened, text, setText }: PromptPropsType) => (

    <Collapse in={opened}>
        <Textarea
          style={{
                maxWidth: '600px',
            }}
          withAsterisk
          description="Please type your AI prompt to identify texts in need of change and to propose a consequential amendment and specify your rationale."
          placeholder={"For example:\n1: Replace 'RS-1' with 'R1-1'\n2: Remove references to specific numbers of parking spaces, and replace them with `See Parking Bylaw`"}
          autosize
          minRows={4}
          value={text}
          onChange={setText}
        />
    </Collapse>

);

export default Prompt;
