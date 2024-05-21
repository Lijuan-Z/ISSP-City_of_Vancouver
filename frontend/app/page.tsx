import { Box, Center } from '@mantine/core';
import { Welcome } from '../components/Welcome/Welcome';
import { ColorSchemeToggle } from '../components/ColorSchemeToggle/ColorSchemeToggle';
import SearchBar1 from '@/components/SearchBar/search-bar';
import { FilesProviders } from '@/contexts/files.context';

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
