import { useEffect, useState, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { authenticatedFetch } from '../utils/api';
import TeamsSelectionModal from '../components/TeamsSelectionModal';
// Tailwind component mappings in index.css replace the old CSS file

function Teams() {
  const [searchParams] = useSearchParams();
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [testingConnection, setTestingConnection] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [startLink, setStartLink] = useState('');
  const [showTeamModal, setShowTeamModal] = useState(false);
  const [teamsStatus, setTeamsStatus] = useState({ personal_installed: false, personal_deeplink: '' });

  // Check for OAuth callback
  useEffect(() => {
    const success = searchParams.get('success');
    const showTeamSelection = searchParams.get('show_team_selection');

    if (success === 'true') {
      if (showTeamSelection === 'true') {
        setSuccessMessage('✅ Teams connected! Select which teams to integrate.');
        setShowTeamModal(true);
      } else {
        setSuccessMessage('✅ Authorized with Microsoft Teams. Next, select teams and channels to receive notifications.');
      }
      // Clear query params
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, [searchParams]);

  const loadIntegrations = useCallback(async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true);
      }

      console.log('[Teams] Loading integrations...', showLoading ? '(with spinner)' : '(background)');

      const response = await authenticatedFetch('/api/teams/integrations');

      if (response.ok) {
        const data = await response.json();
        console.log('[Teams] Loaded', data.length, 'integrations');
        setIntegrations(data);
      } else {
        console.error('[Teams] Failed to load integrations');
      }
    } catch (err) {
      console.error('[Teams] Error loading integrations:', err);
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  }, []);

  const loadStartLink = useCallback(async () => {
    try {
      const response = await authenticatedFetch('/api/teams/oauth/url');

      if (response.ok) {
        const data = await response.json();
        setStartLink(data.oauth_url);
      }
    } catch (err) {
      console.error('[Teams] Error loading OAuth URL:', err);
    }
  }, []);

  useEffect(() => {
    loadIntegrations();
    loadStartLink();
    // Load Teams app install status (personal scope)
    (async () => {
      try {
        const resp = await authenticatedFetch('/api/teams/status');
        if (resp.ok) {
          const data = await resp.json();
          setTeamsStatus(data);
        }
      } catch (e) {
        // ignore
      }
    })();

    // Listen for visibility change (when user returns from Teams)
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        console.log('[Teams] Tab became visible, refreshing integrations...');
        loadIntegrations(false); // Background refresh when tab becomes visible
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [loadIntegrations, loadStartLink]);

  const handleDeleteIntegration = async (integrationId) => {
    if (!confirm('Are you sure you want to disconnect this Teams integration?')) {
      return;
    }

    try {
      const response = await authenticatedFetch(`/api/teams/integrations/${integrationId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setSuccessMessage('Chat disconnected successfully.');
        loadIntegrations();
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to disconnect chat. Please try again.');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    }
  };

  const handleSendTest = async (integration) => {
    try {
      setTestingConnection(integration.id);
      if (!integration.team_id) {
        // DM test (bot flow pending)
        const resp = await authenticatedFetch('/api/teams/send-test-dm', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) });
        if (resp.ok) {
          setSuccessMessage('Test DM sent successfully.');
        } else {
          const data = await resp.json();
          setError(data.detail || 'Unable to send test DM yet. Ensure DRR app is installed in Teams.');
        }
      } else {
        // Channel test
        const resp = await authenticatedFetch('/api/teams/send-test-channel', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ team_id: integration.team_id, channel_id: integration.channel_id }),
        });
        if (resp.ok) {
          setSuccessMessage('Test message sent to channel.');
        } else {
          const data = await resp.json();
          setError(data.detail || 'Failed to send test message to channel.');
        }
      }
    } catch (e) {
      setError('Failed to send test message.');
    } finally {
      setTestingConnection(null);
    }
  };

  const handleTeamModalClose = () => {
    setShowTeamModal(false);
  };

  const handleTeamModalSubmit = (result) => {
    console.log('[Teams] Team modal submitted, result:', result);
    setShowTeamModal(false);
    setSuccessMessage(`✅ Added ${result.added_count} channel integrations!`);
    console.log('[Teams] Reloading integrations to show newly added channels...');
    loadIntegrations(); // Reload to show new integrations
  };

  const getStatusBadge = (status) => {
    const statusClasses = {
      'DISABLED': 'status-disabled',
      'ENABLED': 'status-enabled',
      'ACTIVE': 'status-active',
    };

    // Display status in title case for better UX
    const displayStatus = {
      'DISABLED': 'Disabled',
      'ENABLED': 'Enabled',
      'ACTIVE': 'Active',
    };

    return (
      <span className={`status-badge ${statusClasses[status] || ''}`}>
        {displayStatus[status] || status}
      </span>
    );
  };

  return (
    <div className="teams-page">
      <div className="page-header">
        <h1>Microsoft Teams Integration</h1>
        <p className="subtitle">Connect your Microsoft Teams account to receive domain and SSL certificate expiration notifications</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠️</span>
          <span>{error}</span>
          <button className="alert-close" onClick={() => setError(null)}>×</button>
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success">
          <span className="alert-icon">✅</span>
          <span>{successMessage}</span>
          <button className="alert-close" onClick={() => setSuccessMessage(null)}>×</button>
        </div>
      )}

      {/* Account Requirement Warning */}
      <div className="account-warning-card">
        <div className="warning-header">
          <span className="warning-icon">⚠️</span>
          <h3>Microsoft 365 Work/School Account Required</h3>
        </div>
        <p>
          Teams integration <strong>only works with organizational Microsoft 365 accounts</strong>
          (work or school accounts provided by your organization).
        </p>
        <p style={{ marginTop: '0.5rem', color: '#6b7280' }}>
          Personal Microsoft accounts (Outlook.com, Hotmail, Gmail-linked) are <strong>not supported</strong>
          due to Microsoft Graph API limitations.
        </p>
        <details style={{ marginTop: '1rem' }}>
          <summary style={{ cursor: 'pointer', color: '#2563eb', fontWeight: '500' }}>
            Don't have a work account? See alternatives →
          </summary>
          <div style={{ marginTop: '0.75rem', paddingLeft: '1rem', borderLeft: '3px solid #e5e7eb' }}>
            <p><strong>Alternative notification channels that support personal accounts:</strong></p>
            <ul style={{ marginTop: '0.5rem', marginLeft: '1rem' }}>
              <li><a href="/dashboard/channels/telegram">Telegram</a> - Works with any account</li>
              <li><a href="/dashboard/channels/discord">Discord</a> - Works with any account</li>
              <li><a href="/dashboard/channels/slack">Slack</a> - Works with any workspace</li>
              <li><a href="/dashboard/channels/email">Email</a> - Works with any email address</li>
            </ul>
            <p style={{ marginTop: '0.75rem' }}>
              <strong>For testing:</strong> You can get a free Microsoft 365 developer account at{' '}
              <a href="https://developer.microsoft.com/en-us/microsoft-365/dev-program" target="_blank" rel="noopener noreferrer">
                Microsoft 365 Developer Program
              </a>
            </p>
          </div>
        </details>
      </div>

      <div className="setup-section">
        <h2>How to Set Up Microsoft Teams Integration</h2>

        <div className="instructions-card">
          <h3 style={{ marginBottom: '1rem', color: '#6264A7' }}>💬 Direct Message Setup</h3>

          <div className="instruction-step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Click "Connect Teams"</h3>
              <p>This will redirect you to Microsoft to authorize the DRR app.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Authorize the Application</h3>
              <p>You'll be redirected to Microsoft. Sign in and click "Accept" to allow DRR to access your Teams.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Confirm Connection</h3>
              <p>After authorization, you'll be redirected back and your connection will appear below.</p>
            </div>
          </div>
        </div>

        <div className="instructions-card" style={{ marginTop: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem', color: '#6264A7' }}>👥 Team Channel Setup (Optional)</h3>

          <div className="instruction-step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Select Your Teams</h3>
              <p>After connecting, a modal will appear showing all your Teams. Select the teams you want to integrate.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Select Channels</h3>
              <p>Choose which channels in each team should receive domain expiration notifications.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Receive Team Notifications</h3>
              <p>All team members with access to the channel will see domain and SSL expiration notifications.</p>
            </div>
          </div>
        </div>

        <div className="instructions-card" style={{ marginTop: '1.5rem', backgroundColor: '#fef3c7', borderColor: '#fbbf24' }}>
          <h3 style={{ marginBottom: '1rem', color: '#d97706' }}>🗑️ Disconnecting</h3>

          <div className="instruction-step">
            <div className="step-content" style={{ marginLeft: '0' }}>
              <h4 style={{ marginBottom: '0.5rem' }}>For Direct Messages:</h4>
              <p style={{ marginBottom: '1rem' }}>
                Click "Disconnect" to stop receiving notifications. The app will no longer send you messages.
              </p>

              <h4 style={{ marginBottom: '0.5rem' }}>For Team Channels:</h4>
              <p>
                Click "Disconnect" to stop notifications to that specific channel. You can revoke app permissions in Microsoft Teams settings.
              </p>
            </div>
          </div>
        </div>

        <div className="connect-section">
          <a
            href={startLink}
            className="btn btn-primary btn-large"
            target="_blank"
            rel="noopener noreferrer"
          >
            <span className="teams-icon">📧</span>
            Connect Microsoft Teams
          </a>
          {!teamsStatus.personal_installed && teamsStatus.personal_deeplink && (
            <a
              href={teamsStatus.personal_deeplink}
              className="btn btn-secondary btn-large"
              target="_blank"
              rel="noopener noreferrer"
              style={{ marginLeft: '1rem' }}
            >
              ➕ Add DRR to Teams (DMs)
            </a>
          )}
          {teamsStatus.personal_installed && (
            <span style={{ marginLeft: '1rem', color: '#059669', fontWeight: 500 }}>
              ✅ DRR app installed for DMs
            </span>
          )}
        </div>
      </div>

      <div className="integrations-section">
        <h2>Connected Chats</h2>

        {loading ? (
          <div className="loading-state">
            <span className="spinner"></span>
            <p>Loading integrations...</p>
          </div>
        ) : integrations.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📧</div>
            <h3>No Connected Integrations</h3>
            <p>Connect your Microsoft Teams account to start receiving notifications.</p>
          </div>
        ) : (
          <div className="integrations-grid">
            {integrations.map((integration) => {
              // Determine if this is a DM or team/channel integration
              const isDM = !integration.team_id; // no team => DM

              // Display name logic: show channel name and team for team channels
              let displayName;
              if (isDM) {
                displayName = integration.username || integration.email || 'Direct Message';
              } else {
                const channelDisplay = integration.channel_name
                  ? `${integration.channel_name}`
                  : `Channel ${integration.channel_id}`;
                const teamDisplay = integration.team_name || `Team ${integration.team_id}`;
                displayName = `${channelDisplay} (${teamDisplay})`;
              }

              return (
                <div key={integration.id} className="integration-card">
                  <div className="integration-header">
                    <div className="integration-info">
                      <h3>{displayName}</h3>
                      {integration.email && (
                        <p className="user-email">{integration.email}</p>
                      )}
                    </div>
                    {getStatusBadge(integration.status)}
                  </div>

                  <div className="integration-meta">
                    <div className="meta-item">
                      <span className="meta-label">Type:</span>
                      <span className="meta-value">{isDM ? 'Direct Message' : 'Team Channel'}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Connected:</span>
                      <span className="meta-value">
                        {new Date(integration.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {!isDM && integration.channel_id && (
                      <div className="meta-item">
                        <span className="meta-label">Channel ID:</span>
                        <span className="meta-value">{integration.channel_id}</span>
                      </div>
                    )}
                  </div>

                  <div className="integration-actions">
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => handleSendTest(integration)}
                      disabled={testingConnection === integration.id}
                    >
                      {testingConnection === integration.id ? 'Sending…' : 'Send test'}
                    </button>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDeleteIntegration(integration.id)}
                    >
                      🗑️ Disconnect
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Team Selection Modal */}
      <TeamsSelectionModal
        show={showTeamModal}
        onClose={handleTeamModalClose}
        onSubmit={handleTeamModalSubmit}
      />
    </div>
  );
}

export default Teams;
