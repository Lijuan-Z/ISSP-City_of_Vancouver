import '@mantine/core/styles.css';
import React from 'react';
import {
    MantineProvider,
    ColorSchemeScript,
    AppShell,
    AppShellHeader,
    AppShellNavbar,
    AppShellMain,
} from '@mantine/core';

import { theme } from '../theme';
import Header from '@/components/Header/header';
import { NavbarSimple } from '@/components/NavBar/navbar';
import { FilesProviders } from '@/contexts/files.context';

export const metadata = {
    title: 'PDS',
    description: 'PDS Application',
};

export default function RootLayout({ children }: { children: any }) {
    return (
        <html lang="en">
        <head>
            <ColorSchemeScript />
            <link rel="shortcut icon" href="/robot.ico" />
            <meta
              name="viewport"
              content="minimum-scale=1, initial-scale=1, width=device-width, user-scalable=no"
            />
        </head>
        <body
          style={{
                minHeight: '100vh',
            }}
        >
        <MantineProvider theme={theme}>
            <AppShell
              header={{ height: 100 }}
              navbar={{
                    width: 200,
                    breakpoint: 'sm',
                    collapsed: { mobile: !false },
                }}
              padding="md"
            >
                <AppShellHeader>
                    <Header />
                </AppShellHeader>
                <AppShellNavbar>
                    <NavbarSimple />
                </AppShellNavbar>
                <AppShellMain

                >
                    <FilesProviders>
                        {children}
                    </FilesProviders>
                </AppShellMain>
            </AppShell>
        </MantineProvider>
        </body>
        </html>
    );
}
