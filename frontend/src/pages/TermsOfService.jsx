import LegalPage from '../components/LegalPage';

function TermsOfService() {
  return (
    <LegalPage
      title="Terms of Service"
      effectiveDate="January 1, 2025"
      subtitle="Terms governing use of the DRR platform."
      currentPath="/terms-of-service"
    >
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          1. Acceptance
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          By accessing or using DRR, you agree to these Terms and the related policies (Privacy Policy,
          Cookie Policy, Acceptable Use Policy, and Security Policy). If you do not agree, do not use the service.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          2. The Service
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          DRR provides domain and SSL monitoring with notifications to connected platforms. Data from third-party
          sources may be delayed or inaccurate. DRR does not guarantee real-time accuracy.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          3. Accounts
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          You are responsible for maintaining the confidentiality of your credentials and for all activity under
          your account. You must provide accurate information and keep it up to date.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          4. Acceptable Use
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          Your use of DRR must comply with the Acceptable Use Policy and applicable laws.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          5. Billing and Trial
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed mb-3">
          DRR offers monthly or yearly plans. A free trial of one billing period (28/29/30/31 days) is provided.
          Billing starts immediately after the trial ends unless you cancel before the trial ends.
        </p>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          If you cancel, access continues until the end of the current paid period. Refund terms (if any) are
          described at <span className="text-red-600">[REFUND POLICY URL OR STATEMENT]</span>.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          6. Intellectual Property
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          DRR and its content are owned by <span className="text-red-600">[COMPANY LEGAL NAME]</span> or its
          licensors. You are granted a limited, non-exclusive, non-transferable license to use DRR for your
          internal business purposes.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          7. Third-Party Services
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          Integrations rely on third-party platforms. Their terms and policies apply to your use of those services.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          8. Disclaimers
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          DRR is provided "as is" and "as available" without warranties of any kind, to the extent permitted by law.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          9. Limitation of Liability
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          To the maximum extent permitted by law, <span className="text-red-600">[COMPANY LEGAL NAME]</span> will not
          be liable for indirect, incidental, special, or consequential damages. Total liability is limited to the
          fees paid in the 12 months before the claim.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          10. Termination
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          You may cancel at any time. We may suspend or terminate access for violations of these Terms or law.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          11. Governing Law
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          These Terms are governed by the laws of <span className="text-red-600">[GOVERNING LAW / JURISDICTION]</span>,
          without regard to conflict-of-laws rules.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          12. Contact
        </h2>
        <div className="text-sm text-zinc-600 dark:text-zinc-400 space-y-1">
          <p><span className="text-red-600">[COMPANY LEGAL NAME]</span></p>
          <p><span className="text-red-600">[PHYSICAL ADDRESS]</span></p>
          <p><span className="text-red-600">[LEGAL CONTACT EMAIL]</span></p>
        </div>
      </section>
    </LegalPage>
  );
}

export default TermsOfService;
