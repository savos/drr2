import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { authenticatedFetch } from '../utils/api';
import { Icon } from '../utils/icons';
import { AnimatedPage } from '../components/AnimatedPage';
import { SkeletonTableRow } from '../components/Skeleton';

function Email() {
  const [verifiedUsers, setVerifiedUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadVerifiedUsers();
  }, []);

  const loadVerifiedUsers = async () => {
    try {
      setLoading(true);
      const response = await authenticatedFetch('/api/users/verified');

      if (response.ok) {
        const data = await response.json();
        setVerifiedUsers(data);
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to load verified users');
      }
    } catch (err) {
      setError('An error occurred while loading users');
      console.error('Error loading users:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatedPage>
      <div className="max-w-6xl mx-auto p-4 sm:p-8">
        <div className="page-header">
          <h1>Email Notifications</h1>
          <p className="subtitle">
            Manage email addresses that will receive domain and SSL certificate expiration reminders
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

        <div className="setup-section">
          <h2>Emails for reminders (verified)</h2>

          {loading ? (
            <div className="bg-white dark:bg-zinc-800 rounded-lg border border-zinc-200 dark:border-zinc-700">
              <SkeletonTableRow columns={4} />
              <SkeletonTableRow columns={4} />
              <SkeletonTableRow columns={4} />
              <SkeletonTableRow columns={4} />
            </div>
          ) : verifiedUsers.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">
                <Icon name="envelope" variant="outline" size="xl" className="text-zinc-400 dark:text-zinc-600" />
              </div>
              <h3>No Verified Email Addresses</h3>
              <p>No verified users found in your company. Add users and verify their email addresses to start receiving notifications.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b-2 border-zinc-200 dark:border-zinc-700 text-left">
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Name</th>
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Position</th>
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Email</th>
                    <th className="p-3 font-semibold text-zinc-700 dark:text-zinc-300">Role</th>
                  </tr>
                </thead>
                <tbody>
                  {verifiedUsers.map((user) => (
                    <tr
                      key={user.id}
                      className="border-b border-zinc-200 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors"
                    >
                      <td className="p-3 text-zinc-900 dark:text-zinc-100">
                        {user.firstname} {user.lastname}
                      </td>
                      <td className="p-3 text-zinc-600 dark:text-zinc-400">
                        {user.position || '-'}
                      </td>
                      <td className="p-3 text-zinc-600 dark:text-zinc-400">
                        <div className="flex items-center gap-2">
                          <Icon name="check" variant="solid" size="sm" className="text-emerald-500" />
                          {user.email}
                        </div>
                      </td>
                      <td className="p-3">
                        <span className={`status-badge ${user.is_superuser ? 'status-active' : 'status-disabled'}`}>
                          {user.is_superuser ? 'Superuser' : 'User'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Info Section */}
          <div className="mt-8 p-6 bg-indigo-50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800 rounded-lg">
            <div className="flex items-start gap-3">
              <Icon name="bell" variant="solid" size="md" className="text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
              <div>
                <h3 className="text-base font-semibold text-indigo-900 dark:text-indigo-200 mb-2">
                  How Email Notifications Work
                </h3>
                <p className="text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed mb-3">
                  All verified email addresses listed above can automatically receive domain and SSL certificate
                  expiration reminders. Notifications are sent based on the reminder schedules you configure.
                </p>
                <div className="flex flex-wrap gap-3 mt-4">
                  <Link to="/dashboard/add-user" className="btn btn-secondary btn-sm">
                    <Icon name="users" size="sm" className="text-indigo-600 dark:text-indigo-400" />
                    Add User
                  </Link>
                  <Link to="/dashboard/set-reminders" className="btn btn-secondary btn-sm">
                    <Icon name="clock" size="sm" className="text-indigo-600 dark:text-indigo-400" />
                    Set Reminders
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* Additional Info */}
          <div className="mt-6 p-4 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg">
            <div className="flex items-start gap-3">
              <Icon name="warning" variant="solid" size="sm" className="text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
              <p className="text-sm text-zinc-700 dark:text-zinc-300">
                <strong>Note:</strong> Only users with verified email addresses will receive notifications.
                Users must verify their email by clicking the link sent to their inbox after registration.
              </p>
            </div>
          </div>
        </div>
      </div>
    </AnimatedPage>
  );
}

export default Email;
