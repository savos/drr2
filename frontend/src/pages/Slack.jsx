import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import './Slack.css';

function Slack() {
  const [searchParams] = useSearchParams();
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connectingOAuth, setConnectingOAuth] = useState(false);
  const [testingConnection, setTestingConnection] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Check for OAuth callback status
  useEffect(() => {
    const success = searchParams.get('success');
    const errorParam = searchParams.get('error');

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
            const token = localStorage.getItem('access_token');
            const resp = await fetch(`/api/slack/integrations/${verifiedIntegrationId}/verify`, {
              method: 'POST',
              headers: { 'Authorization': `Bearer ${token}` }
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
      setSuccessMessage('✅ Slack workspace connected successfully!');
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

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');

      const response = await fetch('/api/slack/integrations', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setIntegrations(data);
      } else {
        console.error('Failed to load integrations');
      }
    } catch (err) {
      console.error('Error loading integrations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectSlack = async () => {
    try {
      setConnectingOAuth(true);
      setError(null);
      const token = localStorage.getItem('access_token');

      const response = await fetch('/api/slack/oauth/url', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

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
      const token = localStorage.getItem('access_token');

      // Generate a short client-side verification token (<=16 chars)
      const rand = Math.random().toString(36).slice(2, 10);
      const verifyToken = rand + Math.random().toString(36).slice(2, 6);
      const trimmed = verifyToken.slice(0, 16);
      localStorage.setItem(`slack_verify_token::${integrationId}`, trimmed);

      const response = await fetch(`/api/slack/integrations/${integrationId}/test?verify_token=${encodeURIComponent(trimmed)}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
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

  const handleDeleteIntegration = async (integrationId) => {
    if (!confirm('Are you sure you want to disconnect this Slack workspace?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');

      const response = await fetch(`/api/slack/integrations/${integrationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
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
              <h3>Test Your Connection</h3>
              <p>After connecting, use the "Test Connection" button to verify everything is working. You should receive a test message in your Slack DMs.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">4</div>
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
            {integrations.map((integration) => (
              <div key={integration.id} className="integration-card">
                <div className="integration-header">
                  <div className="integration-info">
                    <h3>{integration.workspace_name || 'Slack Workspace'}</h3>
                    <p className="workspace-id">ID: {integration.workspace_id}</p>
                  </div>
                  {getStatusBadge(integration.status)}
                </div>

                <div className="integration-meta">
                  <div className="meta-item">
                    <span className="meta-label">Connected:</span>
                    <span className="meta-value">
                      {new Date(integration.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {integration.slack_user_id && (
                    <div className="meta-item">
                      <span className="meta-label">User ID:</span>
                      <span className="meta-value">{integration.slack_user_id}</span>
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

                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDeleteIntegration(integration.id)}
                  >
                    🗑️ Disconnect
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Slack;
