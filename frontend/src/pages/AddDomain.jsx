import { useState, useEffect } from 'react';
import { authenticatedFetch } from '../utils/api';
import { Icon } from '../utils/icons';
import { AnimatedPage } from '../components/AnimatedPage';
import { SkeletonTableRow } from '../components/Skeleton';

function AddDomain() {
  const [domainName, setDomainName] = useState('');
  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  useEffect(() => {
    loadDomains();
  }, []);

  const loadDomains = async () => {
    try {
      setLoading(true);
      const response = await authenticatedFetch('/api/domains/');

      if (response.ok) {
        const data = await response.json();
        // Filter only DOMAIN type
        setDomains(data.filter(d => d.type === 'DOMAIN'));
      } else {
        setError('Failed to load domains');
      }
    } catch (err) {
      console.error('Error loading domains:', err);
      setError('An error occurred while loading domains');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!domainName.trim()) {
      setError('Please enter a domain name');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      setSuccessMessage(null);

      const response = await authenticatedFetch('/api/domains/add-domain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: domainName.trim() })
      });

      const data = await response.json();

      if (response.ok) {
        setSuccessMessage(`Domain "${data.name}" added successfully!`);
        setDomainName('');
        loadDomains(); // Reload the list
      } else {
        setError(data.detail || 'Failed to add domain');
      }
    } catch (err) {
      console.error('Error adding domain:', err);
      setError('An error occurred while adding the domain');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (domainId, domainName) => {
    if (!confirm(`Are you sure you want to remove "${domainName}" from monitoring?`)) {
      return;
    }

    try {
      const response = await authenticatedFetch(`/api/domains/${domainId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setSuccessMessage(`Domain "${domainName}" removed successfully`);
        loadDomains();
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to remove domain');
      }
    } catch (err) {
      console.error('Error deleting domain:', err);
      setError('An error occurred while removing the domain');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
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

  return (
    <AnimatedPage>
      <div className="max-w-7xl mx-auto p-4 sm:p-8">
        <div className="page-header">
          <h1>Add Domain</h1>
          <p className="subtitle">
            Monitor domain expiration dates and receive timely reminders
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

        {successMessage && (
          <div className="alert alert-success">
            <span className="alert-icon">
              <Icon name="check" variant="solid" size="sm" className="text-emerald-600" />
            </span>
            <span>{successMessage}</span>
            <button className="alert-close" onClick={() => setSuccessMessage(null)}>×</button>
          </div>
        )}

        {/* Add Domain Form */}
        <div className="setup-section">
          <h2>Add New Domain</h2>
          <form onSubmit={handleSubmit} className="max-w-2xl">
            <div className="form-group">
              <label htmlFor="domainName">Domain Name</label>
              <input
                type="text"
                id="domainName"
                value={domainName}
                onChange={(e) => setDomainName(e.target.value)}
                placeholder="example.com"
                disabled={submitting}
                className="w-full"
              />
              <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-2">
                Enter the domain name without "www." prefix. We'll automatically retrieve expiration information.
              </p>
            </div>

            <div className="form-actions">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={submitting || !domainName.trim()}
              >
                {submitting ? (
                  <>
                    <span className="spinner-sm"></span>
                    Adding Domain...
                  </>
                ) : (
                  <>
                    <Icon name="plus" size="sm" className="text-white" />
                    Add Domain
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Domains List */}
        <div className="setup-section">
          <h2>Monitored Domains</h2>

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
              <h3>No Domains Added</h3>
              <p>Add your first domain to start monitoring expiration dates.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b-2 border-zinc-200 dark:border-zinc-700 text-left">
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Domain</th>
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Registrar</th>
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Expiration Date</th>
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Days Until Expiry</th>
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Added</th>
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {domains.map((domain) => {
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
                        <td className="p-3">
                          <button
                            onClick={() => handleDelete(domain.id, domain.name)}
                            className="btn btn-danger btn-sm"
                          >
                            <Icon name="trash" size="sm" />
                            Remove
                          </button>
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

export default AddDomain;
