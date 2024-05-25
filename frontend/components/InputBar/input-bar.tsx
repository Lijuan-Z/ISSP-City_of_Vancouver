import React, { Dispatch, forwardRef, SetStateAction } from 'react';
import { ActionIcon, TagsInput, TextInputProps, useMantineTheme } from '@mantine/core';
import { IconSearch } from '@tabler/icons-react';
import { rem } from 'polished';

type InputPropsType = {
    keywords: string[]
    setKeywords: Dispatch<SetStateAction<string[]>>
} & TextInputProps;

const InputBar = forwardRef<TextInputProps, InputPropsType>(({
                                                                               setKeywords,
                                                                               keywords,
                                                                           }, ref) => {
    const theme = useMantineTheme();
    return <TagsInput
      ref={ref}
      placeholder="Search keyword(s)..."
      data={[]}
      value={keywords}
      onChange={setKeywords}
      clearable
      style={{
            minWidth: '400px',
            maxWidth: '400px',
        }}
      leftSection={
            <ActionIcon size={32} radius="xl" color={theme.primaryColor} variant="white">
                <IconSearch
                  style={{
                        width: rem(18),
                        height: rem(18),
                    }}
                  stroke={1.5} />
            </ActionIcon>
        } />;
});

export default InputBar;
