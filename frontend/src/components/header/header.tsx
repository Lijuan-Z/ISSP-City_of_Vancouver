import React, {HTMLProps} from 'react';
import Image from "next/image";

const Header = ({children, ...rest}: HTMLProps<HTMLDivElement>) => {
    return (
        <div
            className="w-full flex flex-row justify-start"
            {...rest}
        >
            <Image
                src={"/city_vancouver_logo.png"}
                alt={"logo"}
                width={200}
                height={100}
            />
        </div>
    );
};

export default Header;