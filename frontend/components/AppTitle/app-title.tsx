import React from 'react';
import { Center, Stack, Text } from '@mantine/core';

const AppTitle = () => (
    <Stack
      gap={0}
    >
        <Text ta="center" fw={500} c="blue">PDS Data Optimization Proof of Concept</Text>
        <Text ta="center" fw={500} c="blue">Land Use Document Search Tool for Consequential Amendments and Digitizing
            District Schedule
        </Text>
        <Center>
            <Text
              ta="center"
              size="xs"
              style={{
                    maxWidth: '600px',
                }}>
                This application searches for keywords in documents at <a
                  href="https://vancouver.ca/home-property-development/zoning-and-land-use-policies-document-library.aspx"
                  target="_blank"
                  rel="noreferrer">
                Zoning and land use
                                                                       </a> , and <a
                                                                         href="https://vancouver.ca/your-government/vancouvers-most-referenced-bylaws.aspx"
                                                                         target="_blank"
                                                                         rel="noreferrer"
            >Vancouver's
                most referenced bylaws
                                                                                  </a>.It
                can
                also create amendments based on keyword searches and digitize land use documents for the LZR database.
                Please refer to the <a
                  href="https://vancouver.ca/your-government/vancouvers-most-referenced-bylaws.aspx"
                  target="_blank"
                  rel="noreferrer"
            >manual
                                    </a>. for more information.
            </Text>
        </Center>
    </Stack>
);

export default AppTitle;
