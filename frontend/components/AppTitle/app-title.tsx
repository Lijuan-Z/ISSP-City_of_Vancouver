import React from 'react';
import { Center, Stack, Text } from '@mantine/core';

const AppTitle = () => (
    <Stack
      gap={0}
    >
        <Text ta="center" fw={500} c="blue">PDS Data Optimization Proof of Concept</Text>
        <Text ta="center" fw={500} c="blue">Land Use Document Search Tool for Consequential Amendments and Digitizing
            District Schedules
        </Text>
        <Center>
            <Text
              ta="center"
              size="xs"
              style={{
                    maxWidth: '600px',
                }}>
                This application can search for keywords in documents in the <a
                  href="https://vancouver.ca/home-property-development/zoning-and-land-use-policies-document-library.aspx"
                  target="_blank"
                  rel="noreferrer">
                Zoning and land use document library
                                                                             </a> , and <a
                                                                               href="https://vancouver.ca/your-government/vancouvers-most-referenced-bylaws.aspx"
                                                                               target="_blank"
                                                                               rel="noreferrer"
            >
                Vancouver&apos;s most referenced by-laws
                                                                                        </a> pages.
                Please refer to the <a
                  href="https://covoffice.sharepoint.com/:w:/r/sites/PDSBrainTrust/PDSAccess/Shared%20Documents/user_manual.docx?d=w1a6bd151474c49bb8c85a906f6133e45&csf=1&web=1&e=gnJpG2"
                  target="_blank"
                  rel="noreferrer"
            >manual
                                    </a> for more information.
            </Text>
        </Center>
    </Stack>
);

export default AppTitle;
