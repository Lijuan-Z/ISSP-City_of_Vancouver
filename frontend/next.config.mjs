import bundleAnalyzer from '@next/bundle-analyzer';

// const withBundleAnalyzer = bundleAnalyzer({
//     enabled: process.env.ANALYZE === 'true',
// });
//
// export default withBundleAnalyzer({
//     reactStrictMode: false,
//     eslint: {
//         ignoreDuringBuilds: true,
//     },
//     experimental: {
//         optimizePackageImports: ['@mantine/core', '@mantine/hooks'],
//     },
//     async rewrites() {
//         return [
//             {
//                 source: '/:path*',
//                 destination: 'http://127.0.0.1:5000/:path*'
//             }
//         ]
//     }
// });

/** @type {import('next').NextConfig} */
const nextConfig = {
    async rewrites() {
        return [
            {
                source: '/:path*',
                destination: 'http://127.0.0.1:8000/:path*'
            }
        ]
    }

};

export default nextConfig;
