import type {Metadata} from "next";
import {Inter} from "next/font/google";
import "./globals.css";
import Image from "next/image";
import {FaSearch} from "react-icons/fa";
import SearchBar from "@/components/search-bar/search-bar";
import Header from "@/components/header/header";


const inter = Inter({subsets: ["latin"]});

export const metadata: Metadata = {
    title: "PDS App",
    description: "Document Search",
};

export default function RootLayout({
                                       children,
                                   }: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
        <body className={`${inter.className} min-h-screen`}>
        <div className="flex flex-col items-center p-4 h-screen ">
            <div
                className="fixed top-0 w-full"
            >
                <Header/>
            </div>
            {children}
        </div>
        </body>
        </html>
    );
}
