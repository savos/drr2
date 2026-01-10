import React from "react";
// Tailwind component mappings in index.css replace the old CSS file

export default function UnderDevelopment() {
  return (
    <div className="under-development">
      <div className="under-development-content">
        <div className="under-development-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 19V5M5 12l7-7 7 7"/>
          </svg>
        </div>
        <p className="under-development-domain">
          www.domainrenewalreminder.com
        </p>
        <h1 className="under-development-title">
          Under Development
        </h1>
        <p className="under-development-subtitle">
          We're working hard to bring you something amazing.
        </p>
        <p className="under-development-coming-soon">
          Coming Soon
        </p>
      </div>
    </div>
  );
}
