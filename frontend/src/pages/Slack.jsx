import { useEffect, useState, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { authenticatedFetch } from '../utils/api';
import SlackChannelSelectionModal from '../components/SlackChannelSelectionModal';
// Tailwind component mappings in index.css replace the old CSS file

function Slack() {
  const [searchParams] = useSearchParams();
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connectingOAuth, setConnectingOAuth] = useState(false);
  const [testingConnection, setTestingConnection] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [showChannelModal, setShowChannelModal] = useState(false);
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState('');

  // Check for OAuth callback status
  useEffect(() => {
    const success = searchParams.get('success');
    const errorParam = searchParams.get('error');
    const showChannelSelection = searchParams.get('show_channel_selection');
    const workspaceId = searchParams.get('workspace_id');

    // Frontend-only verification: if Slack DM link returned a `verified` token that
    // matches what we generated for a given integration_id, mark it Active via API.
    const verifiedToken = searchParams.get('verified');
    const verifiedIntegrationId = searchParams.get('integration_id');

    const completeFrontendVerification = async () => {
      try {
        if (verifiedToken && verifiedIntegrationId) {
          const stored = localStorage.getItem(`slack_verify_token::${verifiedIntegrationId}`);
          if (stored && stored === verifiedToken) {
            // Call backend to flip status to Active
            const resp = await authenticatedFetch(`/api/slack/integrations/${verifiedIntegrationId}/verify`, {
              method: 'POST'
            });
            if (resp.ok) {
              setSuccessMessage('✅ Slack DM verified and integration activated.');
              // Clear stored token and URL params
              localStorage.removeItem(`slack_verify_token::${verifiedIntegrationId}`);
              loadIntegrations();
            } else {
              const data = await resp.json().catch(() => ({}));
              setError(data?.detail || 'Failed to activate Slack integration.');
            }
          }
        }
      } finally {
        // Clear URL parameters without reloading
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    };

    if (success === 'true') {
      if (showChannelSelection === 'true') {
        setSelectedWorkspaceId(workspaceId || '');
        setShowChannelModal(true);
        setSuccessMessage('Slack workspace connected! Select channels to connect.');
      } else {
        setSuccessMessage('Slack workspace connected successfully!');
      }
      // Reload integrations
      loadIntegrations();
      // Clear query string (keep UX tidy)
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (errorParam) {
      const errorMessages = {
        'invalid_state': 'Invalid OAuth state. Please try again.',
        'oauth_failed': 'OAuth authentication failed. Please try again.',
        'missing_data': 'Missing data from Slack. Please try again.',
        'database_error': 'Error saving integration. Please try again.',
        'unexpected_error': 'An unexpected error occurred. Please try again.',
      };
      setError(errorMessages[errorParam] || 'An error occurred during OAuth.');
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (verifiedToken && verifiedIntegrationId) {
      // Run verification flow
      completeFrontendVerification();
    }
  }, [searchParams]);

  const loadIntegrations = useCallback(async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true);
      }

      console.log('[Slack] Loading integrations...', showLoading ? '(with spinner)' : '(background)');

      const response = await authenticatedFetch('/api/slack/integrations');

      if (response.ok) {
        const data = await response.json();
        console.log('[Slack] Loaded', data.length, 'integrations');
        setIntegrations(data);
      } else {
        console.error('[Slack] Failed to load integrations');
      }
    } catch (err) {
      console.error('[Slack] Error loading integrations:', err);
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    console.log('[Slack] Setting up auto-refresh (every 10 seconds)');
    loadIntegrations();

    // Set up auto-refresh every 10 seconds to detect new channels
    const intervalId = setInterval(() => {
      console.log('[Slack] Auto-refresh triggered');
      loadIntegrations(false); // Don't show loading spinner during background refresh
    }, 10000); // 10 seconds

    // Cleanup interval on unmount
    return () => {
      console.log('[Slack] Clearing auto-refresh interval');
      clearInterval(intervalId);
    };
  }, [loadIntegrations]);

  const handleConnectSlack = async () => {
    try {
      setConnectingOAuth(true);
      setError(null);

      const response = await authenticatedFetch('/api/slack/oauth/url');

      if (response.ok) {
        const data = await response.json();
        // Redirect to Slack OAuth
        window.location.href = data.oauth_url;
      } else {
        setError('Failed to generate OAuth URL. Please try again.');
        setConnectingOAuth(false);
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
      setConnectingOAuth(false);
    }
  };

  const handleTestConnection = async (integrationId) => {
    try {
      setTestingConnection(integrationId);
      setError(null);
      setSuccessMessage(null);

      // Generate a short client-side verification token (<=16 chars)
      const rand = Math.random().toString(36).slice(2, 10);
      const verifyToken = rand + Math.random().toString(36).slice(2, 6);
      const trimmed = verifyToken.slice(0, 16);
      localStorage.setItem(`slack_verify_token::${integrationId}`, trimmed);

      const response = await authenticatedFetch(`/api/slack/integrations/${integrationId}/test?verify_token=${encodeURIComponent(trimmed)}`, {
        method: 'POST'
      });

      const data = await response.json();

      if (data.success) {
        setSuccessMessage('Test message sent. Please click "✅ Confirm in DRR" in your Slack DM.');
        loadIntegrations(); // Reload to update status
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to send test message. Please try again.');
    } finally {
      setTestingConnection(null);
    }
  };

  const handleChannelModalClose = () => {
    setShowChannelModal(false);
  };

  const handleChannelModalSubmit = (result) => {
    setShowChannelModal(false);
    setSuccessMessage(`Added ${result.added_count} Slack channels.`);
    loadIntegrations();
  };

  const handleDeleteIntegration = async (integrationId) => {
    if (!confirm('Are you sure you want to disconnect this Slack workspace?')) {
      return;
    }

    try {
      const response = await authenticatedFetch(`/api/slack/integrations/${integrationId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setSuccessMessage('Workspace disconnected successfully.');
        loadIntegrations();
      } else {
        setError('Failed to disconnect workspace. Please try again.');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    }
  };

  const getStatusBadge = (status) => {
    const statusClasses = {
      'Disabled': 'status-disabled',
      'Enabled': 'status-enabled',
      'Active': 'status-active',
      'Inactive': 'status-inactive',
    };

    return (
      <span className={`status-badge ${statusClasses[status] || ''}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="slack-page">
      <div className="page-header">
        <h1>Slack Integration</h1>
        <p className="subtitle">Connect your Slack workspace to receive domain and SSL certificate expiration notifications</p>
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

      <div className="setup-section">
        <h2>How to Set Up Slack Integration</h2>
        <div className="instructions-card">
          <div className="instruction-step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Click "Connect to Slack"</h3>
              <p>You'll be redirected to Slack's authorization page where you can choose which workspace to connect.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Authorize DRR App</h3>
              <p>Grant DRR permission to send you direct messages and read your user information. Your data remains secure and private.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Select Channels</h3>
              <p>After connecting, you will be prompted to select channels you created. The bot must already be in those channels.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">4</div>
            <div className="step-content">
              <h3>Test Your Connection</h3>
              <p>After connecting, use the "Test Connection" button to verify everything is working. You should receive a test message in your Slack DMs.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">5</div>
            <div className="step-content">
              <h3>Receive Notifications</h3>
              <p>You'll automatically receive Slack notifications when your domains or SSL certificates are about to expire.</p>
            </div>
          </div>
        </div>

        <div className="connect-section">
          <button
            className="btn btn-primary btn-large"
            onClick={handleConnectSlack}
            disabled={connectingOAuth}
          >
            {connectingOAuth ? (
              <>
                <span className="spinner"></span>
                Connecting...
              </>
            ) : (
              <>
                <img src="/slack-icon.svg" alt="Slack" className="btn-icon" onError={(e) => e.target.style.display = 'none'} />
                Connect to Slack
              </>
            )}
          </button>
        </div>
      </div>

      <div className="integrations-section">
        <h2>Connected Workspaces</h2>

        {loading ? (
          <div className="loading-state">
            <span className="spinner"></span>
            <p>Loading integrations...</p>
          </div>
        ) : integrations.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔌</div>
            <h3>No Connected Workspaces</h3>
            <p>Connect your first Slack workspace to start receiving notifications.</p>
          </div>
        ) : (
          <div className="integrations-grid">
            {integrations.map((integration) => {
              // Determine if this is a DM or channel integration
              const isDM = integration.channel_id === integration.slack_user_id;
              const displayName = isDM
                ? 'Direct Message'
                : (integration.channel_name ? `#${integration.channel_name}` : `Channel ${integration.channel_id}`);

              return (
                <div key={integration.id} className="integration-card">
                  <div className="integration-header">
                    <div className="integration-info">
                      <h3>{displayName}</h3>
                      <p className="workspace-id">{integration.workspace_name || 'Slack Workspace'}</p>
                    </div>
                    {getStatusBadge(integration.status)}
                  </div>

                  <div className="integration-meta">
                    <div className="meta-item">
                      <span className="meta-label">Type:</span>
                      <span className="meta-value">{isDM ? 'Direct Message' : 'Channel'}</span>
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
                      onClick={() => handleTestConnection(integration.id)}
                      disabled={testingConnection === integration.id}
                    >
                      {testingConnection === integration.id ? (
                        <>
                          <span className="spinner-sm"></span>
                          Testing...
                        </>
                      ) : (
                        '🧪 Test Connection'
                      )}
                    </button>

                    {isDM && (
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDeleteIntegration(integration.id)}
                      >
                        🗑️ Disconnect
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <SlackChannelSelectionModal
        show={showChannelModal}
        onClose={handleChannelModalClose}
        onSubmit={handleChannelModalSubmit}
        workspaceId={selectedWorkspaceId}
      />
    </div>
  );
}

export default Slack;
