import { useState, useEffect } from 'react';
import { authenticatedFetch } from '../utils/api';
import { Icon } from '../utils/icons';
import { AnimatedPage } from '../components/AnimatedPage';
import { SkeletonTableRow } from '../components/Skeleton';

function AddSSL() {
  const [sslName, setSslName] = useState('');
  const [sslCerts, setSslCerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  useEffect(() => {
    loadSSLCerts();
  }, []);

  const loadSSLCerts = async () => {
    try {
      setLoading(true);
      const response = await authenticatedFetch('/api/domains/');

      if (response.ok) {
        const data = await response.json();
        // Filter only SSL type
        setSslCerts(data.filter(d => d.type === 'SSL'));
      } else {
        setError('Failed to load SSL certificates');
      }
    } catch (err) {
      console.error('Error loading SSL certificates:', err);
      setError('An error occurred while loading SSL certificates');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!sslName.trim()) {
      setError('Please enter a domain name or IP address');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      setSuccessMessage(null);

      const response = await authenticatedFetch('/api/domains/add-ssl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: sslName.trim() })
      });

      const data = await response.json();

      if (response.ok) {
        setSuccessMessage(`SSL certificate for "${data.name}" added successfully!`);
        setSslName('');
        loadSSLCerts(); // Reload the list
      } else {
        setError(data.detail || 'Failed to add SSL certificate');
      }
    } catch (err) {
      console.error('Error adding SSL certificate:', err);
      setError('An error occurred while adding the SSL certificate');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (sslId, sslName) => {
    if (!confirm(`Are you sure you want to remove SSL monitoring for "${sslName}"?`)) {
      return;
    }

    try {
      const response = await authenticatedFetch(`/api/domains/${sslId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setSuccessMessage(`SSL certificate for "${sslName}" removed successfully`);
        loadSSLCerts();
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to remove SSL certificate');
      }
    } catch (err) {
      console.error('Error deleting SSL certificate:', err);
      setError('An error occurred while removing the SSL certificate');
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

  return (
    <AnimatedPage>
      <div className="max-w-7xl mx-auto p-4 sm:p-8">
        <div className="page-header">
          <h1>Add SSL Certificate</h1>
          <p className="subtitle">
            Monitor SSL certificate expiration dates and stay secure
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

        {/* Add SSL Form */}
        <div className="setup-section">
          <h2>Add New SSL Certificate</h2>
          <form onSubmit={handleSubmit} className="max-w-2xl">
            <div className="form-group">
              <label htmlFor="sslName">Domain or IP Address</label>
              <input
                type="text"
                id="sslName"
                value={sslName}
                onChange={(e) => setSslName(e.target.value)}
                placeholder="example.com or 192.168.1.1"
                disabled={submitting}
                className="w-full"
              />
              <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-2">
                Enter a domain name (subdomain), or IP address. We'll automatically retrieve SSL certificate information on port 443.
              </p>
            </div>

            <div className="form-actions">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={submitting || !sslName.trim()}
              >
                {submitting ? (
                  <>
                    <span className="spinner-sm"></span>
                    Adding SSL Certificate...
                  </>
                ) : (
                  <>
                    <Icon name="plus" size="sm" className="text-white" />
                    Add SSL Certificate
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* SSL Certificates List */}
        <div className="setup-section">
          <h2>Monitored SSL Certificates</h2>

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
              <h3>No SSL Certificates Added</h3>
              <p>Add your first SSL certificate to start monitoring expiration dates.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b-2 border-zinc-200 dark:border-zinc-700 text-left">
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Domain/IP</th>
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Issuer</th>
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Valid From</th>
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Expiration Date</th>
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Days Until Expiry</th>
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Added</th>
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sslCerts.map((cert) => {
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
                        <td className="p-3">
                          <button
                            onClick={() => handleDelete(cert.id, cert.name)}
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

export default AddSSL;
