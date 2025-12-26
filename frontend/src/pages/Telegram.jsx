import { useEffect, useState, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import './Telegram.css';

function Telegram() {
  const [searchParams] = useSearchParams();
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [testingConnection, setTestingConnection] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [startLink, setStartLink] = useState('');
  const [botName, setBotName] = useState('');

  // Check for validation callback
  useEffect(() => {
    const verified = searchParams.get('verified');
    const integrationId = searchParams.get('integration_id');

    if (verified && integrationId) {
      // Validation confirmed - update status to Active
      const updateStatus = async () => {
        try {
          const token = localStorage.getItem('access_token');
          const response = await fetch(`/api/telegram/integrations/${integrationId}/verify`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: verified })
          });

          if (response.ok) {
            setSuccessMessage('✅ Connection confirmed and activated!');
            loadIntegrations();
          }
        } catch (err) {
          console.error('[Telegram] Error verifying:', err);
        } finally {
          // Clear URL parameters
          window.history.replaceState({}, document.title, window.location.pathname);
        }
      };

      updateStatus();
    }
  }, [searchParams]);

  const loadIntegrations = useCallback(async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true);
      }
      const token = localStorage.getItem('access_token');

      console.log('[Telegram] Loading integrations...', showLoading ? '(with spinner)' : '(background)');

      const response = await fetch('/api/telegram/integrations', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        console.log('[Telegram] Loaded', data.length, 'integrations');
        setIntegrations(data);
      } else {
        console.error('[Telegram] Failed to load integrations');
      }
    } catch (err) {
      console.error('[Telegram] Error loading integrations:', err);
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  }, []);

  const loadStartLink = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token');

      const response = await fetch('/api/telegram/start/link', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setStartLink(data.start_link);
        setBotName(data.bot_name);
      }
    } catch (err) {
      console.error('[Telegram] Error loading start link:', err);
    }
  }, []);

  useEffect(() => {
    loadIntegrations();
    loadStartLink();

    // Listen for visibility change (when user returns from Telegram)
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        console.log('[Telegram] Tab became visible, refreshing integrations...');
        loadIntegrations(false); // Background refresh when tab becomes visible
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [loadIntegrations, loadStartLink]);

  const handleTestConnection = async (integrationId) => {
    try {
      setTestingConnection(integrationId);
      setError(null);
      setSuccessMessage(null);
      const token = localStorage.getItem('access_token');

      const response = await fetch(`/api/telegram/integrations/${integrationId}/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (data.success) {
        setSuccessMessage(data.message);
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
    if (!confirm('Are you sure you want to disconnect this Telegram chat?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');

      const response = await fetch(`/api/telegram/integrations/${integrationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
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
    <div className="telegram-page">
      <div className="page-header">
        <h1>Telegram Integration</h1>
        <p className="subtitle">Connect your Telegram account to receive domain and SSL certificate expiration notifications</p>
        <div className="page-actions">
          <button className="btn btn-secondary" onClick={() => loadIntegrations()}>
            Refresh
          </button>
        </div>
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
        <h2>How to Set Up Telegram Integration</h2>

        <div className="instructions-card">
          <h3 style={{ marginBottom: '1rem', color: '#2563eb' }}>📱 Direct Message Setup</h3>

          <div className="instruction-step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Click "Connect Telegram"</h3>
              <p>This will open Telegram and start a direct chat with the DRR bot.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Send /start Command</h3>
              <p>The bot will automatically send the /start command with your account ID. Just tap "START" in Telegram.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Confirm Connection</h3>
              <p>You'll receive a confirmation message from the bot, and your connection will appear below as a Direct Message card.</p>
            </div>
          </div>
        </div>

        <div className="instructions-card" style={{ marginTop: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem', color: '#2563eb' }}>👥 Group Setup (Optional)</h3>

          <div className="instruction-step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Add Bot to Your Group</h3>
              <p>In Telegram, go to your group → Group Info → Add Members → Search for {botName || 'the DRR bot'} and add it.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Grant Admin Permissions (Recommended)</h3>
              <p>Give the bot admin permissions so it can send messages reliably. The connection will appear below as a Group card.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Receive Group Notifications</h3>
              <p>All group members will see domain and SSL expiration notifications in the group chat.</p>
            </div>
          </div>
        </div>

        <div className="instructions-card" style={{ marginTop: '1.5rem', backgroundColor: '#fef3c7', borderColor: '#fbbf24' }}>
          <h3 style={{ marginBottom: '1rem', color: '#d97706' }}>🗑️ Removing the Bot</h3>

          <div className="instruction-step">
            <div className="step-content" style={{ marginLeft: '0' }}>
              <h4 style={{ marginBottom: '0.5rem' }}>For Direct Messages:</h4>
              <p style={{ marginBottom: '1rem' }}>
                Click "Disconnect" to stop notifications. To fully remove the bot from your Telegram chat list, you must manually delete the chat in Telegram or send the <code>/stop</code> command to the bot.
              </p>

              <h4 style={{ marginBottom: '0.5rem' }}>For Groups:</h4>
              <p>
                Click "Disconnect" and the bot will automatically leave the group. Alternatively, you can manually remove the bot from the group in Telegram.
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
            <span className="telegram-icon">📱</span>
            Connect Telegram
          </a>
          {botName && (
            <p className="bot-info">
              Bot: <strong>{botName}</strong>
            </p>
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
            <div className="empty-icon">💬</div>
            <h3>No Connected Chats</h3>
            <p>Connect your Telegram account to start receiving notifications.</p>
          </div>
        ) : (
          <div className="integrations-grid">
            {integrations.map((integration) => {
              // Determine if this is a DM or group integration
              const isDM = integration.chat_type === 'private';
              const displayName = isDM
                ? 'Direct Message'
                : (integration.chat_title || `Group ${integration.channel_id}`);

              return (
                <div key={integration.id} className="integration-card">
                  <div className="integration-header">
                    <div className="integration-info">
                      <h3>{displayName}</h3>
                      {integration.first_name && (
                        <p className="user-name">
                          {integration.first_name}
                          {integration.last_name && ` ${integration.last_name}`}
                          {integration.username && ` (@${integration.username})`}
                        </p>
                      )}
                    </div>
                    {getStatusBadge(integration.status)}
                  </div>

                  <div className="integration-meta">
                    <div className="meta-item">
                      <span className="meta-label">Type:</span>
                      <span className="meta-value">{isDM ? 'Direct Message' : 'Group'}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Connected:</span>
                      <span className="meta-value">
                        {new Date(integration.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {!isDM && integration.channel_id && (
                      <div className="meta-item">
                        <span className="meta-label">Chat ID:</span>
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
    </div>
  );
}

export default Telegram;
