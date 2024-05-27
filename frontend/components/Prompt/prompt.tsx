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
          withAsterisk
          description="Please type your AI prompt to identify regulations in need of change and to propose a consequential amendment."
          placeholder="Example: If there is any mention of parking space size or the number of parking spots, replace it with 'See parking by-law'. Do not replace mentions of parking access or location. Do not replace if the parking by-law is already mentioned. "
          autosize
          minRows={4}
          value={text}
          onChange={setText}
        />
    </Collapse>

);

export default Prompt;
