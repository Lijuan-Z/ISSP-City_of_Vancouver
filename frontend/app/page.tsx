import { Box, Center } from '@mantine/core';
import SearchBar1 from '@/components/SearchBar/search-bar';

export default function HomePage() {
    return (
        <Box
          style={{
                height: '100%',
            }}
        >
            <Center
              h="100%"
            >
                <SearchBar1 />
            </Center>
        </Box>
    );
}
