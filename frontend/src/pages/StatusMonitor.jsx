import { useState, useEffect } from 'react';
import { authenticatedFetch } from '../utils/api';
import { Icon } from '../utils/icons';
import { AnimatedPage } from '../components/AnimatedPage';
import { SkeletonTableRow } from '../components/Skeleton';

function StatusMonitor() {
  const [domains, setDomains] = useState([]);
  const [sslCerts, setSslCerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Sorting state for domains table
  const [domainSortField, setDomainSortField] = useState('renew_date');
  const [domainSortDirection, setDomainSortDirection] = useState('asc');

  // Sorting state for SSL table
  const [sslSortField, setSslSortField] = useState('renew_date');
  const [sslSortDirection, setSslSortDirection] = useState('asc');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const response = await authenticatedFetch('/api/domains/');

      if (response.ok) {
        const data = await response.json();
        // Split data into domains and SSL certificates
        setDomains(data.filter(d => d.type === 'DOMAIN'));
        setSslCerts(data.filter(d => d.type === 'SSL'));
      } else {
        setError('Failed to load monitoring data');
      }
    } catch (err) {
      console.error('Error loading monitoring data:', err);
      setError('An error occurred while loading monitoring data');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const getDaysUntilExpiry = (renewDate) => {
    const today = new Date();
    const expiry = new Date(renewDate);
    const diffTime = expiry - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getExpiryStatus = (renewDate) => {
    const days = getDaysUntilExpiry(renewDate);

    if (days < 0) {
      return { className: 'text-red-600 dark:text-red-400 font-semibold', label: 'Expired' };
    } else if (days <= 7) {
      return { className: 'text-red-600 dark:text-red-400 font-semibold', label: `${days} days` };
    } else if (days <= 30) {
      return { className: 'text-amber-600 dark:text-amber-400 font-semibold', label: `${days} days` };
    } else {
      return { className: 'text-emerald-600 dark:text-emerald-400', label: `${days} days` };
    }
  };

  // Generic sort function
  const sortData = (data, field, direction) => {
    const sorted = [...data].sort((a, b) => {
      let aVal = a[field];
      let bVal = b[field];

      // Handle date fields
      if (field === 'renew_date' || field === 'created_at' || field === 'not_before') {
        aVal = new Date(aVal);
        bVal = new Date(bVal);
      }

      // Handle days until expiry (computed field)
      if (field === 'days_until_expiry') {
        aVal = getDaysUntilExpiry(a.renew_date);
        bVal = getDaysUntilExpiry(b.renew_date);
      }

      // String comparison
      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }

      if (aVal < bVal) return direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return direction === 'asc' ? 1 : -1;
      return 0;
    });

    return sorted;
  };

  // Handle domain table sorting
  const handleDomainSort = (field) => {
    if (domainSortField === field) {
      // Toggle direction
      setDomainSortDirection(domainSortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setDomainSortField(field);
      setDomainSortDirection('asc');
    }
  };

  // Handle SSL table sorting
  const handleSslSort = (field) => {
    if (sslSortField === field) {
      // Toggle direction
      setSslSortDirection(sslSortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSslSortField(field);
      setSslSortDirection('asc');
    }
  };

  // Sort icon component
  const SortIcon = ({ field, currentField, currentDirection }) => {
    if (field !== currentField) {
      return <Icon name="chevronUpDown" size="sm" className="text-zinc-400 dark:text-zinc-600 inline ml-1" />;
    }
    return currentDirection === 'asc' ? (
      <Icon name="chevronUp" size="sm" className="text-indigo-600 dark:text-indigo-400 inline ml-1" />
    ) : (
      <Icon name="chevronDown" size="sm" className="text-indigo-600 dark:text-indigo-400 inline ml-1" />
    );
  };

  // Apply sorting
  const sortedDomains = sortData(domains, domainSortField, domainSortDirection);
  const sortedSslCerts = sortData(sslCerts, sslSortField, sslSortDirection);

  return (
    <AnimatedPage>
      <div className="max-w-7xl mx-auto p-4 sm:p-8">
        <div className="page-header">
          <h1>Status Monitor</h1>
          <p className="subtitle">
            Monitor all domains and SSL certificates in one place
          </p>
        </div>

        {error && (
          <div className="alert alert-error">
            <span className="alert-icon">
              <Icon name="warning" variant="solid" size="sm" className="text-red-600" />
            </span>
            <span>{error}</span>
            <button className="alert-close" onClick={() => setError(null)}>×</button>
          </div>
        )}

        {/* Domains Table */}
        <div className="setup-section">
          <h2>Domains ({domains.length})</h2>

          {loading ? (
            <div className="bg-white dark:bg-zinc-800 rounded-lg border border-zinc-200 dark:border-zinc-700">
              <SkeletonTableRow columns={5} />
              <SkeletonTableRow columns={5} />
              <SkeletonTableRow columns={5} />
            </div>
          ) : domains.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">
                <Icon name="globe" variant="outline" size="xl" className="text-zinc-400 dark:text-zinc-600" />
              </div>
              <h3>No Domains Monitored</h3>
              <p>Add domains to start monitoring their expiration dates.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b-2 border-zinc-200 dark:border-zinc-700 text-left">
                    <th
                      className="p-3 font-semibold text-zinc-700 dark:text-zinc-300 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
                      onClick={() => handleDomainSort('name')}
                    >
                      Domain
                      <SortIcon field="name" currentField={domainSortField} currentDirection={domainSortDirection} />
                    </th>
                    <th
                      className="p-3 font-semibold text-zinc-700 dark:text-zinc-300 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
                      onClick={() => handleDomainSort('issuer')}
                    >
                      Registrar
                      <SortIcon field="issuer" currentField={domainSortField} currentDirection={domainSortDirection} />
                    </th>
                    <th
                      className="p-3 font-semibold text-zinc-700 dark:text-zinc-300 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
                      onClick={() => handleDomainSort('renew_date')}
                    >
                      Expiration Date
                      <SortIcon field="renew_date" currentField={domainSortField} currentDirection={domainSortDirection} />
                    </th>
                    <th
                      className="p-3 font-semibold text-zinc-700 dark:text-zinc-300 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
                      onClick={() => handleDomainSort('days_until_expiry')}
                    >
                      Days Until Expiry
                      <SortIcon field="days_until_expiry" currentField={domainSortField} currentDirection={domainSortDirection} />
                    </th>
                    <th
                      className="p-3 font-semibold text-zinc-700 dark:text-zinc-300 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
                      onClick={() => handleDomainSort('created_at')}
                    >
                      Added
                      <SortIcon field="created_at" currentField={domainSortField} currentDirection={domainSortDirection} />
                    </th>
                    <th
                      className="p-3 font-semibold text-zinc-700 dark:text-zinc-300 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
                      onClick={() => handleDomainSort('updated_at')}
                    >
                      Last Check
                      <SortIcon field="updated_at" currentField={domainSortField} currentDirection={domainSortDirection} />
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {sortedDomains.map((domain) => {
                    const expiryStatus = getExpiryStatus(domain.renew_date);

                    return (
                      <tr
                        key={domain.id}
                        className="border-b border-zinc-200 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors"
                      >
                        <td className="p-3 text-zinc-900 dark:text-zinc-100 font-medium">
                          {domain.name}
                        </td>
                        <td className="p-3 text-zinc-600 dark:text-zinc-400">
                          {domain.issuer}
                        </td>
                        <td className="p-3 text-zinc-600 dark:text-zinc-400">
                          {formatDate(domain.renew_date)}
                        </td>
                        <td className={`p-3 ${expiryStatus.className}`}>
                          {expiryStatus.label}
                        </td>
                        <td className="p-3 text-zinc-600 dark:text-zinc-400">
                          {formatDate(domain.created_at)}
                        </td>
                        <td className="p-3 text-zinc-600 dark:text-zinc-400">
                          {formatDateTime(domain.updated_at)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* SSL Certificates Table */}
        <div className="setup-section">
          <h2>SSL Certificates ({sslCerts.length})</h2>

          {loading ? (
            <div className="bg-white dark:bg-zinc-800 rounded-lg border border-zinc-200 dark:border-zinc-700">
              <SkeletonTableRow columns={6} />
              <SkeletonTableRow columns={6} />
              <SkeletonTableRow columns={6} />
            </div>
          ) : sslCerts.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">
                <Icon name="link" variant="outline" size="xl" className="text-zinc-400 dark:text-zinc-600" />
              </div>
              <h3>No SSL Certificates Monitored</h3>
              <p>Add SSL certificates to start monitoring their expiration dates.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b-2 border-zinc-200 dark:border-zinc-700 text-left">
                    <th
                      className="p-3 font-semibold text-zinc-700 dark:text-zinc-300 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
                      onClick={() => handleSslSort('name')}
                    >
                      Domain
                      <SortIcon field="name" currentField={sslSortField} currentDirection={sslSortDirection} />
                    </th>
                    <th
                      className="p-3 font-semibold text-zinc-700 dark:text-zinc-300 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
                      onClick={() => handleSslSort('issuer')}
                    >
                      Issuer
                      <SortIcon field="issuer" currentField={sslSortField} currentDirection={sslSortDirection} />
                    </th>
                    <th
                      className="p-3 font-semibold text-zinc-700 dark:text-zinc-300 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
                      onClick={() => handleSslSort('not_before')}
                    >
                      Valid From
                      <SortIcon field="not_before" currentField={sslSortField} currentDirection={sslSortDirection} />
                    </th>
                    <th
                      className="p-3 font-semibold text-zinc-700 dark:text-zinc-300 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
                      onClick={() => handleSslSort('renew_date')}
                    >
                      Expiration Date
                      <SortIcon field="renew_date" currentField={sslSortField} currentDirection={sslSortDirection} />
                    </th>
                    <th
                      className="p-3 font-semibold text-zinc-700 dark:text-zinc-300 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
                      onClick={() => handleSslSort('days_until_expiry')}
                    >
                      Days Until Expiry
                      <SortIcon field="days_until_expiry" currentField={sslSortField} currentDirection={sslSortDirection} />
                    </th>
                    <th
                      className="p-3 font-semibold text-zinc-700 dark:text-zinc-300 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
                      onClick={() => handleSslSort('created_at')}
                    >
                      Added
                      <SortIcon field="created_at" currentField={sslSortField} currentDirection={sslSortDirection} />
                    </th>
                    <th
                      className="p-3 font-semibold text-zinc-700 dark:text-zinc-300 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-700/50"
                      onClick={() => handleSslSort('updated_at')}
                    >
                      Last Check
                      <SortIcon field="updated_at" currentField={sslSortField} currentDirection={sslSortDirection} />
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {sortedSslCerts.map((cert) => {
                    const expiryStatus = getExpiryStatus(cert.renew_date);

                    return (
                      <tr
                        key={cert.id}
                        className="border-b border-zinc-200 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors"
                      >
                        <td className="p-3 text-zinc-900 dark:text-zinc-100 font-medium">
                          {cert.name}
                        </td>
                        <td className="p-3 text-zinc-600 dark:text-zinc-400">
                          {cert.issuer}
                        </td>
                        <td className="p-3 text-zinc-600 dark:text-zinc-400">
                          {formatDateTime(cert.not_before)}
                        </td>
                        <td className="p-3 text-zinc-600 dark:text-zinc-400">
                          {formatDate(cert.renew_date)}
                        </td>
                        <td className={`p-3 ${expiryStatus.className}`}>
                          {expiryStatus.label}
                        </td>
                        <td className="p-3 text-zinc-600 dark:text-zinc-400">
                          {formatDate(cert.created_at)}
                        </td>
                        <td className="p-3 text-zinc-600 dark:text-zinc-400">
                          {formatDateTime(cert.updated_at)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </AnimatedPage>
  );
}

export default StatusMonitor;
