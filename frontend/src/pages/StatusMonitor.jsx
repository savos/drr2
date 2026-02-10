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
  const [checking, setChecking] = useState(null);
  const [checkingAll, setCheckingAll] = useState(false);
  const [domainFilter, setDomainFilter] = useState('');
  const [sslFilter, setSslFilter] = useState('');
  const [viewMode, setViewMode] = useState('both'); // 'domains', 'ssl', 'both'
  
  // Pagination state
  const [domainsPerPage, setDomainsPerPage] = useState(10);
  const [currentDomainPage, setCurrentDomainPage] = useState(1);
  const [sslPerPage, setSslPerPage] = useState(10);
  const [currentSslPage, setCurrentSslPage] = useState(1);

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

  const handleCheck = async (id, type) => {
    setChecking(id);
    setError(null);
    try {
      const response = await authenticatedFetch(`/api/domains/${id}/check`, {
        method: 'PATCH',
      });

      if (response.ok) {
        const updatedDomain = await response.json();
        
        // Update the appropriate state based on type
        if (type === 'DOMAIN') {
          setDomains(prevDomains => prevDomains.map(d => d.id === id ? updatedDomain : d));
        } else {
          setSslCerts(prevCerts => prevCerts.map(c => c.id === id ? updatedDomain : c));
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to check domain');
      }
    } catch (err) {
      console.error('Error checking domain:', err);
      setError('An error occurred while checking the domain');
    } finally {
      setChecking(null);
    }
  };

  const handleCheckAllSSL = async () => {
    if (sslCerts.length === 0) return;
    
    setCheckingAll(true);
    setError(null);
    
    try {
      // Check all SSL certificates sequentially
      for (const cert of sslCerts) {
        try {
          const response = await authenticatedFetch(`/api/domains/${cert.id}/check`, {
            method: 'PATCH',
          });

          if (response.ok) {
            const updatedCert = await response.json();
            setSslCerts(prevCerts => prevCerts.map(c => c.id === cert.id ? updatedCert : c));
          } else {
            console.error(`Failed to check certificate ${cert.name}`);
          }
        } catch (err) {
          console.error(`Error checking certificate ${cert.name}:`, err);
        }
      }
    } finally {
      setCheckingAll(false);
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

  // Pagination component
  const Pagination = ({ currentPage, totalPages, onPageChange }) => {
    if (totalPages <= 1) return null;

    const getPageNumbers = () => {
      const pages = [];
      const maxVisible = 7;
      
      if (totalPages <= maxVisible) {
        for (let i = 1; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        if (currentPage <= 4) {
          for (let i = 1; i <= 5; i++) pages.push(i);
          pages.push('...');
          pages.push(totalPages);
        } else if (currentPage >= totalPages - 3) {
          pages.push(1);
          pages.push('...');
          for (let i = totalPages - 4; i <= totalPages; i++) pages.push(i);
        } else {
          pages.push(1);
          pages.push('...');
          for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i);
          pages.push('...');
          pages.push(totalPages);
        }
      }
      return pages;
    };

    return (
      <div className="flex items-center justify-center gap-2 mt-4 pb-4">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="px-3 py-1 rounded border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-zinc-50 dark:hover:bg-zinc-700"
        >
          Previous
        </button>
        {getPageNumbers().map((page, idx) => (
          page === '...' ? (
            <span key={`ellipsis-${idx}`} className="px-2 text-zinc-500">...</span>
          ) : (
            <button
              key={page}
              onClick={() => onPageChange(page)}
              className={`px-3 py-1 rounded border ${
                currentPage === page
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-700'
              }`}
            >
              {page}
            </button>
          )
        ))}
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="px-3 py-1 rounded border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-zinc-50 dark:hover:bg-zinc-700"
        >
          Next
        </button>
      </div>
    );
  };

  // Apply filtering
  const filteredDomains = domainFilter.length >= 2 
    ? domains.filter(d => d.name.toLowerCase().includes(domainFilter.toLowerCase()))
    : domains;
  
  const filteredSslCerts = sslFilter.length >= 2
    ? sslCerts.filter(c => c.name.toLowerCase().includes(sslFilter.toLowerCase()))
    : sslCerts;

  // Apply sorting
  const sortedDomains = sortData(filteredDomains, domainSortField, domainSortDirection);
  const sortedSslCerts = sortData(filteredSslCerts, sslSortField, sslSortDirection);

  // Pagination logic for domains
  const totalDomainPages = domainsPerPage === 'all' ? 1 : Math.ceil(sortedDomains.length / domainsPerPage);
  const paginatedDomains = domainsPerPage === 'all' 
    ? sortedDomains 
    : sortedDomains.slice((currentDomainPage - 1) * domainsPerPage, currentDomainPage * domainsPerPage);

  // Pagination logic for SSL
  const totalSslPages = sslPerPage === 'all' ? 1 : Math.ceil(sortedSslCerts.length / sslPerPage);
  const paginatedSslCerts = sslPerPage === 'all'
    ? sortedSslCerts
    : sortedSslCerts.slice((currentSslPage - 1) * sslPerPage, currentSslPage * sslPerPage);

  return (
    <AnimatedPage>
      <div className="max-w-7xl mx-auto p-4 sm:p-8">
        <div className="page-header">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1>Status Monitor</h1>
              <p className="subtitle">
                Monitor all domains and SSL certificates in one place
              </p>
            </div>
            
            {/* View Mode Toggle */}
            <div className="inline-flex rounded-lg border border-zinc-300 dark:border-zinc-600 bg-zinc-100 dark:bg-zinc-800 p-1">
              <button
                onClick={() => setViewMode('both')}
                className={`px-4 py-2 rounded-md font-medium transition-all text-sm ${
                  viewMode === 'both'
                    ? 'bg-white dark:bg-zinc-700 text-indigo-600 dark:text-indigo-400 shadow-sm'
                    : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-200'
                }`}
              >
                Both
              </button>
              <button
                onClick={() => setViewMode('domains')}
                className={`px-4 py-2 rounded-md font-medium transition-all text-sm ${
                  viewMode === 'domains'
                    ? 'bg-white dark:bg-zinc-700 text-indigo-600 dark:text-indigo-400 shadow-sm'
                    : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-200'
                }`}
              >
                Domains Only
              </button>
              <button
                onClick={() => setViewMode('ssl')}
                className={`px-4 py-2 rounded-md font-medium transition-all text-sm ${
                  viewMode === 'ssl'
                    ? 'bg-white dark:bg-zinc-700 text-indigo-600 dark:text-indigo-400 shadow-sm'
                    : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-200'
                }`}
              >
                SSL Certificates Only
              </button>
            </div>
          </div>
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
        {(viewMode === 'both' || viewMode === 'domains') && (
        <div className="setup-section">
          <div className="flex items-center justify-between mb-4">
            <h2>Domains ({filteredDomains.length}{domainFilter.length >= 2 ? ` of ${domains.length}` : ''})</h2>
            {filteredDomains.length > 10 && (
              <div className="flex items-center gap-2">
                <label className="text-sm text-zinc-600 dark:text-zinc-400">Show domains per page:</label>
                <select
                  value={domainsPerPage}
                  onChange={(e) => {
                    setDomainsPerPage(e.target.value === 'all' ? 'all' : parseInt(e.target.value));
                    setCurrentDomainPage(1);
                  }}
                  className="px-3 py-1 rounded border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100"
                >
                  <option value="10">10</option>
                  <option value="20">20</option>
                  <option value="50">50</option>
                  <option value="100">100</option>
                  <option value="all">All</option>
                </select>
              </div>
            )}
          </div>

          {/* Domain Filter */}
          <div className="flex items-center gap-3 p-4 mb-4 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-200 dark:border-zinc-700">
            <label className="text-zinc-700 dark:text-zinc-300 font-medium">Filter:</label>
            <div className="relative flex-1 max-w-md">
              <input
                type="text"
                value={domainFilter}
                onChange={(e) => {
                  setDomainFilter(e.target.value);
                  setCurrentDomainPage(1);
                }}
                placeholder="Search domains..."
                className="w-full pl-10 pr-10 py-2 rounded-lg border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400 dark:text-zinc-500">
                <Icon name="magnifyingGlass" size="sm" />
              </div>
              {domainFilter.length >= 2 && (
                <button
                  onClick={() => setDomainFilter('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 dark:text-zinc-500 hover:text-zinc-600 dark:hover:text-zinc-300"
                >
                  <Icon name="xMark" size="sm" />
                </button>
              )}
            </div>
          </div>

          {loading ? (
            <div className="bg-white dark:bg-zinc-800 rounded-lg border border-zinc-200 dark:border-zinc-700">
              <SkeletonTableRow columns={7} />
              <SkeletonTableRow columns={7} />
              <SkeletonTableRow columns={7} />
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
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">
                      Check
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedDomains.map((domain) => {
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
                        <td className="p-3">
                          <button
                            onClick={() => handleCheck(domain.id, 'DOMAIN')}
                            disabled={checking === domain.id}
                            className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {checking === domain.id ? 'Checking...' : 'Check'}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
          
          {/* Domain Pagination */}
          {!loading && domains.length > 0 && (
            <Pagination
              currentPage={currentDomainPage}
              totalPages={totalDomainPages}
              onPageChange={setCurrentDomainPage}
            />
          )}
        </div>
        )}

        {/* SSL Certificates Table */}
        {(viewMode === 'both' || viewMode === 'ssl') && (
        <div className="setup-section">
          <div className="flex items-center justify-between mb-4">
            <h2>SSL Certificates ({filteredSslCerts.length}{sslFilter.length >= 2 ? ` of ${sslCerts.length}` : ''})</h2>
            {filteredSslCerts.length > 10 && (
              <div className="flex items-center gap-2">
                <label className="text-sm text-zinc-600 dark:text-zinc-400">Show certificates per page:</label>
                <select
                  value={sslPerPage}
                  onChange={(e) => {
                    setSslPerPage(e.target.value === 'all' ? 'all' : parseInt(e.target.value));
                    setCurrentSslPage(1);
                  }}
                  className="px-3 py-1 rounded border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100"
                >
                  <option value="10">10</option>
                  <option value="20">20</option>
                  <option value="50">50</option>
                  <option value="100">100</option>
                  <option value="all">All</option>
                </select>
              </div>
            )}
          </div>
          
          {/* SSL Filter and Check All */}
          <div className="flex items-center justify-between gap-4 p-4 mb-4 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-200 dark:border-zinc-700">
            {/* Filter on the left */}
            <div className="flex items-center gap-3 flex-1">
              <label className="text-zinc-700 dark:text-zinc-300 font-medium">Filter:</label>
              <div className="relative flex-1 max-w-md">
                <input
                  type="text"
                  value={sslFilter}
                  onChange={(e) => setSslFilter(e.target.value)}
                  placeholder="Search SSL certificates..."
                  className="w-full pl-10 pr-10 py-2 rounded-lg border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400 dark:text-zinc-500">
                  <Icon name="magnifyingGlass" size="sm" />
                </div>
                {sslFilter.length >= 2 && (
                  <button
                    onClick={() => setSslFilter('')}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 dark:text-zinc-500 hover:text-zinc-600 dark:hover:text-zinc-300"
                  >
                    <Icon name="xMark" size="sm" />
                  </button>
                )}
              </div>
            </div>
            
            {/* Check All on the right */}
            {sslCerts.length > 0 && (
              <div className="flex items-center gap-3">
                <span className="text-zinc-700 dark:text-zinc-300 font-medium">
                  Check all SSL certificates
                </span>
                <button
                  onClick={handleCheckAllSSL}
                  disabled={checkingAll}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium whitespace-nowrap"
                >
                  {checkingAll ? 'Checking...' : 'Check'}
                </button>
              </div>
            )}
          </div>

          {loading ? (
            <div className="bg-white dark:bg-zinc-800 rounded-lg border border-zinc-200 dark:border-zinc-700">
              <SkeletonTableRow columns={8} />
              <SkeletonTableRow columns={8} />
              <SkeletonTableRow columns={8} />
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
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">
                      Check
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedSslCerts.map((cert) => {
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
                        <td className="p-3">
                          <button
                            onClick={() => handleCheck(cert.id, 'SSL')}
                            disabled={checking === cert.id}
                            className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {checking === cert.id ? 'Checking...' : 'Check'}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
          
          {/* SSL Pagination */}
          {!loading && sslCerts.length > 0 && (
            <Pagination
              currentPage={currentSslPage}
              totalPages={totalSslPages}
              onPageChange={setCurrentSslPage}
            />
          )}
        </div>
        )}
      </div>
    </AnimatedPage>
  );
}

export default StatusMonitor;
