import { useEffect, useState, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { authenticatedFetch } from '../utils/api';
import GuildSelectionModal from '../components/GuildSelectionModal';
// Tailwind component mappings in index.css replace the old CSS file

function Discord() {
  const [searchParams] = useSearchParams();
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [testingConnection, setTestingConnection] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [startLink, setStartLink] = useState('');
  const [botName, setBotName] = useState('');
  const [showGuildModal, setShowGuildModal] = useState(false);

  // Check for validation callback
  useEffect(() => {
    const verified = searchParams.get('verified');
    const integrationId = searchParams.get('integration_id');
    const success = searchParams.get('success');
    const showGuildSelection = searchParams.get('show_guild_selection');

    if (verified && integrationId) {
      // Validation confirmed - update status to Active
      const updateStatus = async () => {
        try {
          const response = await authenticatedFetch(`/api/discord/integrations/${integrationId}/verify`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: verified })
          });

          if (response.ok) {
            setSuccessMessage('✅ Connection confirmed and activated!');
            loadIntegrations();
          }
        } catch (err) {
          console.error('[Discord] Error verifying:', err);
        } finally {
          // Clear URL parameters
          window.history.replaceState({}, document.title, window.location.pathname);
        }
      };

      updateStatus();
    }

    // After OAuth success, check if we should show guild selection
    if (success === 'true') {
      if (showGuildSelection === 'true') {
        setSuccessMessage('✅ Discord connected! Select which servers to integrate.');
        setShowGuildModal(true);
      } else {
        setSuccessMessage('✅ Authorized with Discord. Next, invite the bot to a server and select a channel to receive notifications.');
      }
      // Clear query params (keep UX tidy)
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, [searchParams]);

  const loadIntegrations = useCallback(async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true);
      }

      console.log('[Discord] Loading integrations...', showLoading ? '(with spinner)' : '(background)');

      const response = await authenticatedFetch('/api/discord/integrations');

      if (response.ok) {
        const data = await response.json();
        console.log('[Discord] Loaded', data.length, 'integrations');
        setIntegrations(data);
      } else {
        console.error('[Discord] Failed to load integrations');
      }
    } catch (err) {
      console.error('[Discord] Error loading integrations:', err);
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  }, []);

  const loadStartLink = useCallback(async () => {
    try {
      const response = await authenticatedFetch('/api/discord/oauth/url');

      if (response.ok) {
        const data = await response.json();
        setStartLink(data.oauth_url);
        setBotName('DRR Discord Bot');
      }
    } catch (err) {
      console.error('[Discord] Error loading OAuth URL:', err);
    }
  }, []);

  useEffect(() => {
    loadIntegrations();
    loadStartLink();

    // Listen for visibility change (when user returns from Discord)
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        console.log('[Discord] Tab became visible, refreshing integrations...');
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

      const response = await authenticatedFetch(`/api/discord/integrations/${integrationId}/test`, {
        method: 'POST'
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
    if (!confirm('Are you sure you want to disconnect this Discord integration?')) {
      return;
    }

    try {
      const response = await authenticatedFetch(`/api/discord/integrations/${integrationId}`, {
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

  const handleGuildModalClose = () => {
    setShowGuildModal(false);
  };

  const handleGuildModalSubmit = (result) => {
    console.log('[Discord] Guild modal submitted, result:', result);
    setShowGuildModal(false);
    setSuccessMessage(`✅ Added ${result.added_count} channel integrations!`);
    console.log('[Discord] Reloading integrations to show newly added channels...');
    loadIntegrations(); // Reload to show new integrations
  };

  const handleReconnectDiscord = () => {
    // Redirect to OAuth URL to refresh authorization
    if (startLink) {
      window.location.href = startLink;
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
    <div className="discord-page">
      <div className="page-header">
        <h1>Discord Integration</h1>
        <p className="subtitle">Connect your Discord account to receive domain and SSL certificate expiration notifications</p>
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
        <h2>How to Set Up Discord Integration</h2>

        <div className="instructions-card">
          <h3 style={{ marginBottom: '1rem', color: '#5865F2' }}>📱 Direct Message Setup</h3>

          <div className="instruction-step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Click "Connect Discord"</h3>
              <p>This will redirect you to Discord to authorize the DRR bot.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Authorize the Application</h3>
              <p>You'll be redirected to Discord. Click "Authorize" to allow DRR to send you direct messages.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Confirm Connection</h3>
              <p>After authorization, you'll be redirected back and your connection will appear below as a Direct Message card.</p>
            </div>
          </div>
        </div>

        <div className="instructions-card" style={{ marginTop: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem', color: '#5865F2' }}>👥 Server Channel Setup (Optional)</h3>

          <div className="instruction-step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Add Bot to Your Server</h3>
              <p>Use the bot invite link to add DRR to a Discord server <strong>you own</strong>. Only servers you created will be available for integration.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Select Channels</h3>
              <p>Choose which channels should receive domain expiration notifications. The bot can see both public and private channels in servers you own.</p>
            </div>
          </div>

          <div className="instruction-step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Receive Server Notifications</h3>
              <p>All server members with access to the channel will see domain and SSL expiration notifications.</p>
            </div>
          </div>
        </div>

        <div className="instructions-card" style={{ marginTop: '1.5rem', backgroundColor: '#fef3c7', borderColor: '#fbbf24' }}>
          <h3 style={{ marginBottom: '1rem', color: '#d97706' }}>🗑️ Disconnecting</h3>

          <div className="instruction-step">
            <div className="step-content" style={{ marginLeft: '0' }}>
              <h4 style={{ marginBottom: '0.5rem' }}>For Direct Messages:</h4>
              <p style={{ marginBottom: '1rem' }}>
                Click "Disconnect" to stop receiving notifications. The bot will no longer send you DMs.
              </p>

              <h4 style={{ marginBottom: '0.5rem' }}>For Server Channels:</h4>
              <p>
                Click "Disconnect" to stop notifications to that specific channel. You can remove the bot from your server entirely in Discord's Server Settings → Integrations.
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
            <span className="discord-icon">💬</span>
            Connect Discord
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
            <h3>No Connected Integrations</h3>
            <p>Connect your Discord account to start receiving notifications.</p>
          </div>
        ) : (
          <div className="integrations-grid">
            {integrations.map((integration) => {
              // Determine if this is a DM or guild/channel integration
              const isDM = !integration.guild_id; // no guild => DM

              // Display name logic: show channel name and guild for server channels
              let displayName;
              if (isDM) {
                displayName = integration.global_name || integration.username || 'Direct Message';
              } else {
                const channelDisplay = integration.channel_name
                  ? `#${integration.channel_name}`
                  : `Channel ${integration.channel_id}`;
                const guildDisplay = integration.guild_name || `Guild ${integration.guild_id}`;
                displayName = `${channelDisplay} (${guildDisplay})`;
              }

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
                      <span className="meta-value">{isDM ? 'Direct Message' : 'Server Channel'}</span>
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

      {/* Guild Selection Modal */}
      <GuildSelectionModal
        show={showGuildModal}
        onClose={handleGuildModalClose}
        onSubmit={handleGuildModalSubmit}
        onReconnect={handleReconnectDiscord}
      />
    </div>
  );
}

export default Discord;
