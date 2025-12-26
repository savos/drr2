import { useState, useEffect } from 'react';
import { authenticatedFetch } from '../utils/api';
import './TeamsSelectionModal.css';

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

      const response = await authenticatedFetch('/api/teams/available-teams');

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
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Select Microsoft Teams</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div className="modal-loading">
              <span className="spinner"></span>
              <p>Loading available teams...</p>
            </div>
          ) : error ? (
            <div className="modal-error">
              <p>{error}</p>
              <button className="btn btn-secondary" onClick={loadAvailableTeams}>
                Retry
              </button>
            </div>
          ) : teams.length === 0 ? (
            <div className="modal-empty">
              <p>No available teams found.</p>
              <p className="hint-text">
                Make sure you're a member of at least one Microsoft Team.
              </p>
            </div>
          ) : (
            <>
              <p className="modal-description">
                Click on a team to expand and select individual channels to integrate.
              </p>
              <div className="teams-list">
                {teams.map((team) => {
                  const isExpanded = expandedTeamIds.has(team.id);
                  const selectedCount = team.channels.filter(ch =>
                    selectedChannels.has(`${team.id}:${ch.id}`)
                  ).length;
                  const allSelected = team.channels.length > 0 &&
                    selectedCount === team.channels.length;

                  return (
                    <div key={team.id} className="team-item-wrapper">
                      <div className="team-item">
                        <button
                          className="team-expand-btn"
                          onClick={() => toggleTeamExpanded(team.id)}
                        >
                          <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
                            ▶
                          </span>
                        </button>
                        <div
                          className="team-info"
                          onClick={() => toggleTeamExpanded(team.id)}
                        >
                          <div className="team-details">
                            <div className="team-name">{team.name}</div>
                            <div className="team-meta">
                              {team.channels.length} channel{team.channels.length !== 1 ? 's' : ''}
                              {selectedCount > 0 && ` • ${selectedCount} selected`}
                            </div>
                            {team.description && (
                              <div className="team-description">{team.description}</div>
                            )}
                          </div>
                        </div>
                        {team.channels.length > 0 && (
                          <button
                            className="select-all-btn"
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
                            />
                          </button>
                        )}
                      </div>

                      {isExpanded && team.channels.length > 0 && (
                        <div className="channels-list">
                          {team.channels.map((channel) => {
                            const channelKey = `${team.id}:${channel.id}`;
                            const isSelected = selectedChannels.has(channelKey);

                            return (
                              <div
                                key={channel.id}
                                className={`channel-item ${isSelected ? 'selected' : ''}`}
                                onClick={() => toggleChannel(team, channel)}
                              >
                                <input
                                  type="checkbox"
                                  checked={isSelected}
                                  onChange={() => toggleChannel(team, channel)}
                                  onClick={(e) => e.stopPropagation()}
                                />
                                <span className="channel-name">{channel.name}</span>
                                {channel.type === 'private' && (
                                  <span className="channel-type-badge">Private</span>
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
            disabled={submitting || loading || teams.length === 0 || selectedChannels.size === 0}
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

export default TeamsSelectionModal;
