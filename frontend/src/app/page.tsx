import Image from "next/image";
import SearchBar from "@/components/search-bar/search-bar";
import Header from "@/components/header/header";

export default function Home() {
    return (
        <div className="flex w-full max-w-md h-full items-center justify-items-center">
            <SearchBar/>
        </div>

    );
}
