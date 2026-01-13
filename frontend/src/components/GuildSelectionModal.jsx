import { useState, useEffect } from 'react';
import { authenticatedFetch } from '../utils/api';
import './GuildSelectionModal.css';

function GuildSelectionModal({ show, onClose, onSubmit, onReconnect }) {
  const [guilds, setGuilds] = useState([]);
  const [expandedGuildIds, setExpandedGuildIds] = useState(new Set());
  const [selectedChannels, setSelectedChannels] = useState(new Map()); // Map<channelId, {guildId, guildName, channelId, channelName}>
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [infoMessage, setInfoMessage] = useState(null);
  const [needsReconnect, setNeedsReconnect] = useState(false);

  useEffect(() => {
    if (show) {
      loadAvailableGuilds();
      setExpandedGuildIds(new Set());
      setSelectedChannels(new Map());
    }
  }, [show]);

  const loadAvailableGuilds = async () => {
    try {
      setLoading(true);
      setError(null);
      setInfoMessage(null);
      setNeedsReconnect(false);

      const response = await authenticatedFetch('/api/discord/available-guilds');

      if (response.ok) {
        const data = await response.json();
        setGuilds(data.guilds || []);

        // Handle special error/message responses
        if (data.error === 'no_token' || data.error === 'token_expired' ||
            data.error === 'no_owned_guilds' || data.error === 'no_integration') {
          setNeedsReconnect(true);
          setInfoMessage(data.message);
        } else if (data.message && data.guilds?.length === 0) {
          setInfoMessage(data.message);
        }
      } else {
        setError('Failed to load available servers');
      }
    } catch (err) {
      console.error('Error loading guilds:', err);
      setError('Failed to load available servers');
    } finally {
      setLoading(false);
    }
  };

  const toggleGuildExpanded = (guildId) => {
    const newExpanded = new Set(expandedGuildIds);
    if (newExpanded.has(guildId)) {
      newExpanded.delete(guildId);
    } else {
      newExpanded.add(guildId);
    }
    setExpandedGuildIds(newExpanded);
  };

  const toggleChannel = (guild, channel) => {
    const channelKey = `${guild.id}:${channel.id}`;
    const newSelection = new Map(selectedChannels);

    if (newSelection.has(channelKey)) {
      newSelection.delete(channelKey);
    } else {
      newSelection.set(channelKey, {
        guild_id: guild.id,
        guild_name: guild.name,
        channel_id: channel.id,
        channel_name: channel.name
      });
    }
    setSelectedChannels(newSelection);
  };

  const toggleAllChannelsInGuild = (guild) => {
    const newSelection = new Map(selectedChannels);
    const allSelected = guild.channels.every(ch =>
      newSelection.has(`${guild.id}:${ch.id}`)
    );

    if (allSelected) {
      // Deselect all channels in this guild
      guild.channels.forEach(ch => {
        newSelection.delete(`${guild.id}:${ch.id}`);
      });
    } else {
      // Select all channels in this guild
      guild.channels.forEach(ch => {
        newSelection.set(`${guild.id}:${ch.id}`, {
          guild_id: guild.id,
          guild_name: guild.name,
          channel_id: ch.id,
          channel_name: ch.name
        });
      });
    }
    setSelectedChannels(newSelection);
  };

  const handleSubmit = async () => {
    if (selectedChannels.size === 0) {
      onClose();
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      const channelsArray = Array.from(selectedChannels.values());
      console.log('[GuildModal] Submitting channels:', channelsArray);

      const response = await authenticatedFetch('/api/discord/add-channels', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          channels: channelsArray
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('[GuildModal] Success response:', data);
        onSubmit(data);
      } else {
        const data = await response.json();
        console.error('[GuildModal] Error response:', data);
        setError(data.detail || 'Failed to add selected channels');
      }
    } catch (err) {
      console.error('[GuildModal] Exception adding channels:', err);
      setError('Failed to add selected channels');
    } finally {
      setSubmitting(false);
    }
  };

  if (!show) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Select Discord Servers</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div className="modal-loading">
              <span className="spinner"></span>
              <p>Loading available servers...</p>
            </div>
          ) : error ? (
            <div className="modal-error">
              <p>{error}</p>
              <button className="btn btn-secondary" onClick={loadAvailableGuilds}>
                Retry
              </button>
            </div>
          ) : needsReconnect ? (
            <div className="modal-empty">
              <p>{infoMessage || 'Your Discord authorization needs to be refreshed.'}</p>
              <button
                className="btn btn-primary"
                onClick={() => {
                  onClose();
                  if (onReconnect) onReconnect();
                }}
              >
                Reconnect Discord
              </button>
            </div>
          ) : guilds.length === 0 ? (
            <div className="modal-empty">
              <p>{infoMessage || 'No available servers found.'}</p>
              <p className="hint-text">
                Only servers you own will appear here. Make sure the DRR bot is added to your servers.
              </p>
            </div>
          ) : (
            <>
              <p className="modal-description">
                Select channels from servers you own. Click a server to expand and select individual channels.
              </p>
              <div className="guilds-list">
                {guilds.map((guild) => {
                  const isExpanded = expandedGuildIds.has(guild.id);
                  const selectedCount = guild.channels.filter(ch =>
                    selectedChannels.has(`${guild.id}:${ch.id}`)
                  ).length;
                  const allSelected = guild.channels.length > 0 &&
                    selectedCount === guild.channels.length;

                  return (
                    <div key={guild.id} className="guild-item-wrapper">
                      <div className="guild-item">
                        <button
                          className="guild-expand-btn"
                          onClick={() => toggleGuildExpanded(guild.id)}
                        >
                          <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
                            ▶
                          </span>
                        </button>
                        <div
                          className="guild-info"
                          onClick={() => toggleGuildExpanded(guild.id)}
                        >
                          {guild.icon && (
                            <img
                              src={`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`}
                              alt={guild.name}
                              className="guild-icon"
                            />
                          )}
                          <div className="guild-details">
                            <div className="guild-name">{guild.name}</div>
                            <div className="guild-meta">
                              {guild.channels.length} channel{guild.channels.length !== 1 ? 's' : ''}
                              {selectedCount > 0 && ` • ${selectedCount} selected`}
                            </div>
                          </div>
                          {guild.owner && <span className="owner-badge">Owner</span>}
                        </div>
                        {guild.channels.length > 0 && (
                          <button
                            className="select-all-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleAllChannelsInGuild(guild);
                            }}
                            title={allSelected ? "Deselect all" : "Select all"}
                          >
                            <input
                              type="checkbox"
                              checked={allSelected}
                              onChange={() => {}}
                              onClick={(e) => e.stopPropagation()}
                            />
                          </button>
                        )}
                      </div>

                      {isExpanded && guild.channels.length > 0 && (
                        <div className="channels-list">
                          {guild.channels.map((channel) => {
                            const channelKey = `${guild.id}:${channel.id}`;
                            const isSelected = selectedChannels.has(channelKey);

                            return (
                              <div
                                key={channel.id}
                                className={`channel-item ${isSelected ? 'selected' : ''}`}
                                onClick={() => toggleChannel(guild, channel)}
                              >
                                <input
                                  type="checkbox"
                                  checked={isSelected}
                                  onChange={() => toggleChannel(guild, channel)}
                                  onClick={(e) => e.stopPropagation()}
                                />
                                <span className="channel-hash">#</span>
                                <span className="channel-name">{channel.name}</span>
                                {channel.type === 'announcement' && (
                                  <span className="channel-type-badge">Announcement</span>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>

        <div className="modal-footer">
          <button
            className="btn btn-secondary"
            onClick={onClose}
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={submitting || loading || guilds.length === 0 || selectedChannels.size === 0}
          >
            {submitting ? (
              <>
                <span className="spinner-sm"></span>
                Adding...
              </>
            ) : (
              `Add ${selectedChannels.size} Channel${selectedChannels.size !== 1 ? 's' : ''}`
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default GuildSelectionModal;
