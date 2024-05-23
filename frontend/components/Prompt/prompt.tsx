import { Accordion, Box, Button, Collapse, Group, Text, Textarea } from '@mantine/core';
import React from 'react';
import { useDisclosure } from '@mantine/hooks';

const groceries = [
    {
        emoji: '🍎',
        value: 'Apples',
        description:
            'Crisp and refreshing fruit. Apples are known for their versatility and nutritional benefits. They come in a variety of flavors and are great for snacking, baking, or adding to salads.',
    },
];

type PromptPropsType = {
    opened: boolean
};
const Prompt = ({ opened }: PromptPropsType) => (

    <Collapse in={opened}>
        <Textarea
          placeholder="A.I. Prompt"
          autosize
          minRows={2}
        />
    </Collapse>

);

export default Prompt;
