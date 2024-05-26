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
          placeholder="A.I. Prompt"
          autosize
          minRows={2}
          value={text}
          onChange={setText}
        />
    </Collapse>

);

export default Prompt;
