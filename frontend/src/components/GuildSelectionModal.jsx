import { useState, useEffect } from 'react';
import { authenticatedFetch } from '../utils/api';

function GuildSelectionModal({ show, onClose, onSubmit, onReconnect }) {
  const [guilds, setGuilds] = useState([]);
  const [expandedGuildIds, setExpandedGuildIds] = useState(new Set());
  const [selectedChannels, setSelectedChannels] = useState(new Map()); // Map<channelId, {guildId, guildName, channelId, channelName}>
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [infoMessage, setInfoMessage] = useState(null);
  const [needsReconnect, setNeedsReconnect] = useState(false);
  const [errorCode, setErrorCode] = useState(null);
  const [inviteUrl, setInviteUrl] = useState('');

  useEffect(() => {
    if (show) {
      loadAvailableGuilds();
      loadInviteUrl();
      setExpandedGuildIds(new Set());
      setSelectedChannels(new Map());
    }
  }, [show]);

  const loadInviteUrl = async () => {
    try {
      const response = await authenticatedFetch('/api/discord/bot/invite-url');
      if (response.ok) {
        const data = await response.json();
        setInviteUrl(data.invite_url || '');
      }
    } catch (err) {
      console.error('Error loading Discord invite URL:', err);
    }
  };

  const loadAvailableGuilds = async () => {
    try {
      setLoading(true);
      setError(null);
      setInfoMessage(null);
      setNeedsReconnect(false);
      setErrorCode(null);

      const response = await authenticatedFetch('/api/discord/available-guilds');

      if (response.ok) {
        const data = await response.json();
        setGuilds(data.guilds || []);
        setErrorCode(data.error || null);

        // Handle special error/message responses
        if (data.error === 'no_token' || data.error === 'token_expired' ||
            data.error === 'no_guilds' || data.error === 'no_integration') {
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

  const showInviteAction = Boolean(inviteUrl) && (
    errorCode === 'bot_not_installed' ||
    errorCode === 'audit_log_denied' ||
    errorCode === 'no_created_channels'
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Select Discord Servers</h2>
          <button
            className="text-gray-400 hover:text-gray-600 text-3xl font-light leading-none"
            onClick={onClose}
          >
            ×
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mb-4"></div>
              <p className="text-gray-600">Loading available servers...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12">
              <p className="text-red-600 mb-4">{error}</p>
              <button
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg transition-colors"
                onClick={loadAvailableGuilds}
              >
                Retry
              </button>
            </div>
          ) : needsReconnect ? (
            <div className="flex flex-col items-center justify-center py-12 gap-3">
              <p className="text-gray-700 text-center">{infoMessage || 'Your Discord authorization needs to be refreshed.'}</p>
              {showInviteAction && (
                <a
                  className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg transition-colors"
                  href={inviteUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Add Bot to Server
                </a>
              )}
              <button
                className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors"
                onClick={() => {
                  onClose();
                  if (onReconnect) onReconnect();
                }}
              >
                Reconnect Discord
              </button>
            </div>
          ) : guilds.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 gap-3">
              <p className="text-gray-700">{infoMessage || 'No available servers found.'}</p>
              <p className="text-sm text-gray-500">
                Make sure the DRR bot is added to servers you have access to.
              </p>
              {showInviteAction && (
                <a
                  className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors"
                  href={inviteUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Add Bot to Server
                </a>
              )}
            </div>
          ) : (
            <>
              <p className="text-sm text-gray-600 mb-4">
                Select channels you created on your Discord servers. Click a server to expand and select individual channels.
              </p>
              <div className="space-y-2">
                {guilds.map((guild) => {
                  const isExpanded = expandedGuildIds.has(guild.id);
                  const selectedCount = guild.channels.filter(ch =>
                    selectedChannels.has(`${guild.id}:${ch.id}`)
                  ).length;
                  const allSelected = guild.channels.length > 0 &&
                    selectedCount === guild.channels.length;

                  return (
                    <div key={guild.id} className="border border-gray-200 rounded-lg">
                      <div className="flex items-center gap-3 p-4 hover:bg-gray-50 transition-colors">
                        <button
                          className="text-gray-500 hover:text-gray-700 transition-transform"
                          onClick={() => toggleGuildExpanded(guild.id)}
                        >
                          <span className={`inline-block transition-transform ${isExpanded ? 'rotate-90' : ''}`}>
                            ▶
                          </span>
                        </button>
                        <div
                          className="flex-1 flex items-center gap-3 cursor-pointer"
                          onClick={() => toggleGuildExpanded(guild.id)}
                        >
                          {guild.icon && (
                            <img
                              src={`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`}
                              alt={guild.name}
                              className="w-10 h-10 rounded-full"
                            />
                          )}
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-gray-900">{guild.name}</span>
                              {guild.owner && (
                                <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded">
                                  Owner
                                </span>
                              )}
                            </div>
                            <div className="text-sm text-gray-500">
                              {guild.channels.length} channel{guild.channels.length !== 1 ? 's' : ''}
                              {selectedCount > 0 && ` • ${selectedCount} selected`}
                            </div>
                          </div>
                        </div>
                        {guild.channels.length > 0 && (
                          <button
                            className="p-2"
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
                              className="w-4 h-4 text-purple-600 rounded"
                            />
                          </button>
                        )}
                      </div>

                      {isExpanded && guild.channels.length > 0 && (
                        <div className="border-t border-gray-200 bg-gray-50">
                          {guild.channels.map((channel) => {
                            const channelKey = `${guild.id}:${channel.id}`;
                            const isSelected = selectedChannels.has(channelKey);

                            return (
                              <div
                                key={channel.id}
                                className={`flex items-center gap-3 p-3 hover:bg-gray-100 cursor-pointer transition-colors ${
                                  isSelected ? 'bg-purple-50 hover:bg-purple-100' : ''
                                }`}
                                onClick={() => toggleChannel(guild, channel)}
                              >
                                <input
                                  type="checkbox"
                                  checked={isSelected}
                                  onChange={() => toggleChannel(guild, channel)}
                                  onClick={(e) => e.stopPropagation()}
                                  className="w-4 h-4 text-purple-600 rounded ml-8"
                                />
                                <span className="text-gray-500 font-medium">#</span>
                                <span className="flex-1 text-sm text-gray-900">{channel.name}</span>
                                {channel.type === 'announcement' && (
                                  <span className="px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded">
                                    Announcement
                                  </span>
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

        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
          <button
            className="px-6 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={onClose}
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            onClick={handleSubmit}
            disabled={submitting || loading || guilds.length === 0 || selectedChannels.size === 0}
          >
            {submitting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
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
