import LegalPage from '../components/LegalPage';

function AcceptableUsePolicy() {
  return (
    <LegalPage
      title="Acceptable Use Policy"
      effectiveDate="January 1, 2025"
      subtitle="Permitted and prohibited uses of the DRR platform."
      currentPath="/acceptable-use"
    >
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          1. Introduction
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          This Acceptable Use Policy applies to all use of DRR and is part of the Terms of Service. Violations
          may result in suspension or termination, at the sole discretion of{' '}
          <span className="text-red-600">[COMPANY LEGAL NAME]</span>.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          2. Permitted Uses
        </h2>
        <ul className="list-disc list-inside space-y-2 text-zinc-600 dark:text-zinc-400 ml-4">
          <li>Monitoring domains and SSL certificates you own or are authorised to manage.</li>
          <li>Receiving automated notifications to connected platforms you control.</li>
          <li>Managing your workspace, users, and integrations within your company.</li>
          <li>Using the service in compliance with applicable laws and regulations.</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          3. Prohibited Uses
        </h2>

        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-2 mt-5">
          3.1 Security and Access
        </h3>
        <ul className="list-disc list-inside space-y-2 text-zinc-600 dark:text-zinc-400 ml-4 mb-4">
          <li>Attempting to gain unauthorised access to accounts, systems, or data.</li>
          <li>Bypassing or defeating authentication or access controls.</li>
          <li>Probing or scanning without prior written authorisation from{' '}
            <span className="text-red-600">[COMPANY LEGAL NAME]</span>.
          </li>
          <li>Using stolen credentials or compromised tokens.</li>
        </ul>

        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-2 mt-5">
          3.2 Misuse and Abuse
        </h3>
        <ul className="list-disc list-inside space-y-2 text-zinc-600 dark:text-zinc-400 ml-4 mb-4">
          <li>Monitoring domains or certificates you are not authorised to monitor.</li>
          <li>Automating usage in a way that degrades service or evades limits.</li>
          <li>Creating multiple accounts to circumvent restrictions or enforcement.</li>
          <li>Using DRR to facilitate unlawful surveillance or harassment.</li>
        </ul>

        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-2 mt-5">
          3.3 Illegal or Harmful Activity
        </h3>
        <ul className="list-disc list-inside space-y-2 text-zinc-600 dark:text-zinc-400 ml-4 mb-4">
          <li>Using DRR in violation of any applicable law or regulation.</li>
          <li>Distributing malware or engaging in phishing, fraud, or identity theft.</li>
          <li>Interfering with the availability or integrity of DRR or third-party services.</li>
        </ul>

        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-2 mt-5">
          3.4 Intellectual Property
        </h3>
        <ul className="list-disc list-inside space-y-2 text-zinc-600 dark:text-zinc-400 ml-4">
          <li>Infringing the intellectual property rights of{' '}
            <span className="text-red-600">[COMPANY LEGAL NAME]</span> or any third party.
          </li>
          <li>Reverse-engineering, decompiling, or disassembling the service.</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          4. Reporting
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
          Report suspected abuse or vulnerabilities to{' '}
          <span className="text-red-600">[SECURITY CONTACT EMAIL]</span>.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
          5. Contact
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

export default AcceptableUsePolicy;
