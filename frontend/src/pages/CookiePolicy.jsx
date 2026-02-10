import LegalPage from '../components/LegalPage';

function CookiePolicy() {
  return (
    <LegalPage
      title="Cookie Policy"
      effectiveDate="January 1, 2025"
      subtitle="How DRR uses cookies and similar technologies."
      currentPath="/cookie-policy"
    >
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          1. Introduction
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          This Cookie Policy explains how DRR uses cookies and similar technologies. It should be read
          together with the Privacy Policy and Terms of Service.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          2. What Are Cookies
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          Cookies are small text files placed on your device by a website. Similar technologies include
          localStorage and sessionStorage.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          3. Cookies We Use
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed mb-3">
          DRR uses the following categories of cookies:
        </p>
        <ul className="list-disc list-inside space-y-2 text-zinc-600 dark:text-zinc-400 ml-4">
          <li><strong>Essential cookies:</strong> Required to authenticate you and keep you signed in.</li>
          <li><strong>Analytics cookies:</strong> Used to understand product usage and improve the service.
            The current analytics provider is <span className="text-red-600">[ANALYTICS PROVIDER]</span>.
          </li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          4. Local Storage
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          DRR stores limited account profile data in your browser storage to improve the in-app experience.
          You can clear this data by logging out or by clearing site data in your browser.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          5. Managing Cookies
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          You can control cookies using your browser settings. In the EU and UK, analytics cookies are set
          only after consent, where required by law.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          6. Contact
        </h2>
        <div className="text-sm text-zinc-600 dark:text-zinc-400 space-y-1">
          <p><span className="text-red-600">[COMPANY LEGAL NAME]</span></p>
          <p><span className="text-red-600">[PHYSICAL ADDRESS]</span></p>
          <p><span className="text-red-600">[PRIVACY CONTACT EMAIL]</span></p>
        </div>
      </section>
    </LegalPage>
  );
}

export default CookiePolicy;
