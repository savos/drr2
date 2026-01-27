import { useState, useEffect } from 'react';
import { authenticatedFetch } from '../utils/api';

function TeamsSelectionModal({ show, onClose, onSubmit }) {
  const [teams, setTeams] = useState([]);
  const [expandedTeamIds, setExpandedTeamIds] = useState(new Set());
  const [selectedChannels, setSelectedChannels] = useState(new Map()); // Map<channelId, {teamId, teamName, channelId, channelName}>
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (show) {
      loadAvailableTeams();
      setExpandedTeamIds(new Set());
      setSelectedChannels(new Map());
    }
  }, [show]);

  const loadAvailableTeams = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await authenticatedFetch('/api/teams/owned-teams');

      if (response.ok) {
        const data = await response.json();
        setTeams(data.teams || []);
      } else {
        setError('Failed to load available teams');
      }
    } catch (err) {
      console.error('Error loading teams:', err);
      setError('Failed to load available teams');
    } finally {
      setLoading(false);
    }
  };

  const toggleTeamExpanded = (teamId) => {
    const newExpanded = new Set(expandedTeamIds);
    if (newExpanded.has(teamId)) {
      newExpanded.delete(teamId);
    } else {
      newExpanded.add(teamId);
    }
    setExpandedTeamIds(newExpanded);
  };

  const toggleChannel = (team, channel) => {
    const channelKey = `${team.id}:${channel.id}`;
    const newSelection = new Map(selectedChannels);

    if (newSelection.has(channelKey)) {
      newSelection.delete(channelKey);
    } else {
      newSelection.set(channelKey, {
        team_id: team.id,
        team_name: team.name,
        channel_id: channel.id,
        channel_name: channel.name
      });
    }
    setSelectedChannels(newSelection);
  };

  const toggleAllChannelsInTeam = (team) => {
    const newSelection = new Map(selectedChannels);
    const allSelected = team.channels.every(ch =>
      newSelection.has(`${team.id}:${ch.id}`)
    );

    if (allSelected) {
      // Deselect all channels in this team
      team.channels.forEach(ch => {
        newSelection.delete(`${team.id}:${ch.id}`);
      });
    } else {
      // Select all channels in this team
      team.channels.forEach(ch => {
        newSelection.set(`${team.id}:${ch.id}`, {
          team_id: team.id,
          team_name: team.name,
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
      console.log('[TeamsModal] Submitting channels:', channelsArray);

      // Install app to selected teams (best effort)
      const teamIds = Array.from(new Set(channelsArray.map(c => c.team_id)));
      try {
        const installResp = await authenticatedFetch('/api/teams/install', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ include_personal: false, team_ids: teamIds }),
        });
        if (installResp.ok) {
          const installData = await installResp.json();
          console.log('[TeamsModal] Install results:', installData);
        }
      } catch (e) {
        console.warn('[TeamsModal] Install attempt failed, will continue to save channels');
      }

      const response = await authenticatedFetch('/api/teams/add-channels', {
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
        console.log('[TeamsModal] Success response:', data);
        onSubmit(data);
      } else {
        const data = await response.json();
        console.error('[TeamsModal] Error response:', data);
        setError(data.detail || 'Failed to add selected channels');
      }
    } catch (err) {
      console.error('[TeamsModal] Exception adding channels:', err);
      setError('Failed to add selected channels');
    } finally {
      setSubmitting(false);
    }
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Select Microsoft Teams</h2>
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
              <p className="text-gray-600">Loading available teams...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12">
              <p className="text-red-600 mb-4">{error}</p>
              <button
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg transition-colors"
                onClick={loadAvailableTeams}
              >
                Retry
              </button>
            </div>
          ) : teams.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <p className="text-gray-700 mb-2">No available teams found.</p>
              <p className="text-sm text-gray-500">
                Make sure you're a member of at least one Microsoft Team.
              </p>
            </div>
          ) : (
            <>
              <p className="text-sm text-gray-600 mb-4">
                Click on a team to expand and select individual channels to integrate.
              </p>
              <div className="space-y-2">
                {teams.map((team) => {
                  const isExpanded = expandedTeamIds.has(team.id);
                  const selectedCount = team.channels.filter(ch =>
                    selectedChannels.has(`${team.id}:${ch.id}`)
                  ).length;
                  const allSelected = team.channels.length > 0 &&
                    selectedCount === team.channels.length;

                  return (
                    <div key={team.id} className="border border-gray-200 rounded-lg">
                      <div className="flex items-center gap-3 p-4 hover:bg-gray-50 transition-colors">
                        <button
                          className="text-gray-500 hover:text-gray-700 transition-transform"
                          onClick={() => toggleTeamExpanded(team.id)}
                        >
                          <span className={`inline-block transition-transform ${isExpanded ? 'rotate-90' : ''}`}>
                            ▶
                          </span>
                        </button>
                        <div
                          className="flex-1 cursor-pointer"
                          onClick={() => toggleTeamExpanded(team.id)}
                        >
                          <div className="font-medium text-gray-900">{team.name}</div>
                          <div className="text-sm text-gray-500">
                            {team.channels.length} channel{team.channels.length !== 1 ? 's' : ''}
                            {selectedCount > 0 && ` • ${selectedCount} selected`}
                          </div>
                          {team.description && (
                            <div className="text-sm text-gray-600 mt-1">{team.description}</div>
                          )}
                        </div>
                        {team.channels.length > 0 && (
                          <button
                            className="p-2"
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleAllChannelsInTeam(team);
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

                      {isExpanded && team.channels.length > 0 && (
                        <div className="border-t border-gray-200 bg-gray-50">
                          {team.channels.map((channel) => {
                            const channelKey = `${team.id}:${channel.id}`;
                            const isSelected = selectedChannels.has(channelKey);

                            return (
                              <div
                                key={channel.id}
                                className={`flex items-center gap-3 p-3 hover:bg-gray-100 cursor-pointer transition-colors ${
                                  isSelected ? 'bg-purple-50 hover:bg-purple-100' : ''
                                }`}
                                onClick={() => toggleChannel(team, channel)}
                              >
                                <input
                                  type="checkbox"
                                  checked={isSelected}
                                  onChange={() => toggleChannel(team, channel)}
                                  onClick={(e) => e.stopPropagation()}
                                  className="w-4 h-4 text-purple-600 rounded ml-8"
                                />
                                <span className="flex-1 text-sm text-gray-900">{channel.name}</span>
                                {channel.type === 'private' && (
                                  <span className="px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded">
                                    Private
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
            disabled={submitting || loading || teams.length === 0 || selectedChannels.size === 0}
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

export default TeamsSelectionModal;
