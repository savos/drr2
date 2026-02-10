import LegalPage from '../components/LegalPage';

function SecurityPolicy() {
  return (
    <LegalPage
      title="Security Policy"
      effectiveDate="January 1, 2025"
      subtitle="Security measures and responsible disclosure."
      currentPath="/security"
    >
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          1. Overview
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          DRR implements technical and organizational measures to protect data. No system is perfectly secure,
          and we cannot guarantee absolute security.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          2. Core Controls
        </h2>
        <ul className="list-disc list-inside space-y-2 text-zinc-600 dark:text-zinc-400 ml-4">
          <li>Password hashing and access control for user accounts.</li>
          <li>Encrypted storage for integration tokens.</li>
          <li>HTTPS in production and secure API integrations.</li>
          <li>Input validation and parameterized database access.</li>
          <li>Audit logging and monitoring for security events.</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          3. Shared Responsibility
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          Users are responsible for protecting their credentials and devices. Security of third-party platforms
          (Slack, Discord, Microsoft, Telegram) is managed by those providers.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          4. Responsible Disclosure
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed mb-3">
          If you believe you have found a security vulnerability, please report it to:
        </p>
        <div className="text-sm text-zinc-600 dark:text-zinc-400">
          <span className="text-red-600">[SECURITY CONTACT EMAIL]</span>
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          5. Incident Response
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          We investigate security incidents promptly and notify affected users when required by applicable law.
        </p>
      </section>
    </LegalPage>
  );
}

export default SecurityPolicy;
