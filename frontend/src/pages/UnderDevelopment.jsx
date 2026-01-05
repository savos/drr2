import React from "react";

export default function UnderDevelopment() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white text-center text-gray-800 p-4 sm:p-6 md:p-8">
      <p className="text-xs sm:text-sm md:text-base uppercase tracking-[0.3em] text-gray-500 px-4">
        www.domainrenewalreminder.com
      </p>
      <h1 className="mt-4 sm:mt-6 md:mt-8 text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-semibold tracking-wide px-4">
        Under Development
      </h1>
      <p className="mt-2 sm:mt-3 md:mt-4 text-base sm:text-lg md:text-xl lg:text-2xl text-gray-600 px-4">
        Coming soon...
      </p>
    </div>
  );
}
