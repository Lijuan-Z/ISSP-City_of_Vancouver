'use client';

import { useState } from 'react';
import { Group, Code } from '@mantine/core';
import {
    IconBellRinging,
    IconFingerprint,
    IconKey,
    IconSettings,
    Icon2fa,
    IconDatabaseImport,
    IconReceipt2,
    IconSwitchHorizontal,
    IconLogout, IconPdf, IconDatabase,
} from '@tabler/icons-react';
// import { MantineLogo } from '@mantinex/mantine-logo';
import { usePathname, useRouter } from 'next/navigation';
import classes from './NavbarSimple.module.css';

const data = [
    {
        link: '/',
        label: 'Objective One',
        icon: IconPdf,
    },
    {
        link: '/lazer',
        label: 'Objective Three',
        icon: IconDatabase,

    },
];

export function NavbarSimple() {
    const router = useRouter();
    const pathName = usePathname();
    console.log('path', pathName);
    const links = data.map((item) => (
        <a
          className={classes.link}
          data-active={item.link === pathName || undefined}
          href={item.link}
          key={item.label}
          onClick={(event) => {
                event.preventDefault();
                router.push(item.link);
            }}
        >
            <item.icon className={classes.linkIcon} stroke={1.5} />
            <span>{item.label}</span>
        </a>
    ));

    return (
        <nav className={classes.navbar}>
            <div className={classes.navbarMain}>

                {links}
            </div>

        </nav>
    );
}