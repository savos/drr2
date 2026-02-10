import { Link, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { AnimatedPage } from '../components/AnimatedPage';
import Footer from '../components/Footer';

const LEGAL_PAGES = [
  { path: '/privacy-policy', label: 'Privacy Policy' },
  { path: '/terms-of-service', label: 'Terms of Service' },
  { path: '/cookie-policy', label: 'Cookie Policy' },
  { path: '/acceptable-use', label: 'Acceptable Use Policy' },
  { path: '/security', label: 'Security Policy' },
];

function LegalPage({ title, effectiveDate, subtitle, currentPath, children }) {
  const others = LEGAL_PAGES.filter((p) => p.path !== currentPath);
  const location = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  return (
    <AnimatedPage>
      <div className="bg-white dark:bg-zinc-950 border-b border-zinc-200 dark:border-zinc-800">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <p className="text-xs uppercase tracking-widest text-zinc-500 dark:text-zinc-400">Legal</p>
          <h1 className="text-3xl sm:text-4xl font-semibold text-zinc-900 dark:text-zinc-100 mt-2">{title}</h1>
          {subtitle && (
            <p className="text-base text-zinc-600 dark:text-zinc-400 mt-3">{subtitle}</p>
          )}
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-4">Effective {effectiveDate}</p>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {children}
      </div>

      <Footer />
    </AnimatedPage>
  );
}

export default LegalPage;
