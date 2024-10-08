import React, { Dispatch, forwardRef, SetStateAction } from 'react';
import { ActionIcon, TagsInput, TextInputProps, useMantineTheme } from '@mantine/core';
import { IconSearch } from '@tabler/icons-react';
import { rem } from 'polished';

type InputPropsType = {
    keywords: string[]
    setKeywords: Dispatch<SetStateAction<string[]>>
    inputBarDescription: string
} & TextInputProps;

const InputBar = forwardRef<TextInputProps, InputPropsType>(({
                                                                 setKeywords,
                                                                 keywords,
                                                                 inputBarDescription,
                                                             }, ref) => {
    const theme = useMantineTheme();
    return <TagsInput
      withAsterisk
      ref={ref as any}
      placeholder="Search keyword(s)..."
      data={[]}
      value={keywords}
      onChange={setKeywords}
      clearable
      style={{
            minWidth: '600px',
            maxWidth: '600px',
        }}
      description={inputBarDescription}
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
