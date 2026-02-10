import LegalPage from '../components/LegalPage';

function PrivacyPolicy() {
  return (
    <LegalPage
      title="Privacy Policy"
      effectiveDate="January 1, 2025"
      subtitle="How DRR collects, uses, and protects personal data."
      currentPath="/privacy-policy"
    >
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          1. Controller and Contact
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed mb-3">
          The data controller is <span className="text-red-600">[COMPANY LEGAL NAME]</span>.
        </p>
        <div className="text-sm text-zinc-600 dark:text-zinc-400 space-y-1">
          <p><span className="text-red-600">[PHYSICAL ADDRESS]</span></p>
          <p><span className="text-red-600">[PRIVACY CONTACT EMAIL]</span></p>
          <p><span className="text-red-600">[DPO CONTACT EMAIL - IF APPOINTED]</span></p>
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          2. Data We Collect
        </h2>
        <ul className="list-disc list-inside space-y-2 text-zinc-600 dark:text-zinc-400 ml-4">
          <li>Account data: name, email, company, role/position, and authentication details.</li>
          <li>Service data: domains, SSL metadata, notification settings, and integration identifiers.</li>
          <li>Integration data: OAuth tokens and identifiers for connected platforms.</li>
          <li>Usage data: logs and diagnostics necessary for security and reliability.</li>
          <li>Analytics data: usage metrics from <span className="text-red-600">[ANALYTICS PROVIDER]</span>.</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          3. How We Use Data
        </h2>
        <ul className="list-disc list-inside space-y-2 text-zinc-600 dark:text-zinc-400 ml-4">
          <li>Provide, maintain, and secure the DRR service.</li>
          <li>Authenticate users and enforce access controls.</li>
          <li>Send notifications and service communications.</li>
          <li>Improve reliability and performance through analytics.</li>
          <li>Comply with legal obligations and enforce our terms.</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          4. Legal Bases (EU/UK)
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          We process personal data on the bases of contract performance, legitimate interests
          (service security and improvement), and consent where required (e.g., analytics cookies).
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          5. Sharing and Processors
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed mb-3">
          We share data with vendors and processors to operate the service, including hosting and email delivery.
        </p>
        <ul className="list-disc list-inside space-y-2 text-zinc-600 dark:text-zinc-400 ml-4">
          <li>Hosting provider: <span className="text-red-600">[HOSTING PROVIDER - CURRENTLY OVH]</span>.</li>
          <li>Email provider: <span className="text-red-600">[EMAIL PROVIDER - CURRENTLY MAILTRAP]</span>.</li>
          <li>Analytics provider: <span className="text-red-600">[ANALYTICS PROVIDER]</span>.</li>
          <li>Integration providers: Slack, Discord, Microsoft, Telegram (for notification delivery).</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          6. International Transfers
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          Data may be transferred internationally depending on vendor locations. Where required,
          we rely on appropriate safeguards such as Standard Contractual Clauses or equivalent mechanisms.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          7. Retention
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          We retain personal data only as long as necessary for the purposes described above or as required
          by law. You can request deletion as described below.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          8. Your Rights
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed mb-3">
          Depending on your location, you may have rights to access, correct, delete, or restrict processing
          of your personal data. EU/UK users have additional rights under GDPR/UK GDPR, and California users
          have rights under CCPA/CPRA. Australian users have rights under the Privacy Act 1988.
        </p>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          Contact us using the details above to exercise your rights.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          9. Cookies and Analytics
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          DRR uses essential cookies for authentication and may use analytics cookies where permitted by law.
          See the Cookie Policy for details.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          10. Children
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          DRR is intended for business use. Users must be at least{' '}
          <span className="text-red-600">[MINIMUM AGE]</span> years old.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          11. Changes
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          We may update this policy from time to time. Material changes will be communicated in the application
          or by email.
        </p>
      </section>
    </LegalPage>
  );
}

export default PrivacyPolicy;
