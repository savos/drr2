import { useState, useEffect } from 'react';
import { authenticatedFetch } from '../utils/api';
import './GuildSelectionModal.css';

function SlackChannelSelectionModal({ show, onClose, onSubmit, workspaceId }) {
  const [channels, setChannels] = useState([]);
  const [selectedChannels, setSelectedChannels] = useState(new Map());
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [infoMessage, setInfoMessage] = useState(null);

  useEffect(() => {
    if (show) {
      loadAvailableChannels();
      setSelectedChannels(new Map());
    }
  }, [show, workspaceId]);

  const loadAvailableChannels = async () => {
    try {
      setLoading(true);
      setError(null);
      setInfoMessage(null);

      const query = workspaceId ? `?workspace_id=${encodeURIComponent(workspaceId)}` : '';
      const response = await authenticatedFetch(`/api/slack/available-channels${query}`);

      if (response.ok) {
        const data = await response.json();
        setChannels(data.channels || []);
        if (data.message && data.channels?.length === 0) {
          setInfoMessage(data.message);
        }
      } else {
        setError('Failed to load available channels');
      }
    } catch (err) {
      console.error('Error loading Slack channels:', err);
      setError('Failed to load available channels');
    } finally {
      setLoading(false);
    }
  };

  const toggleChannel = (channel) => {
    const newSelection = new Map(selectedChannels);
    if (newSelection.has(channel.id)) {
      newSelection.delete(channel.id);
    } else {
      newSelection.set(channel.id, {
        channel_id: channel.id,
        channel_name: channel.name,
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
      const response = await authenticatedFetch('/api/slack/add-channels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workspace_id: workspaceId,
          channels: channelsArray,
        })
      });

      if (response.ok) {
        const data = await response.json();
        onSubmit(data);
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to add selected channels');
      }
    } catch (err) {
      console.error('Error adding Slack channels:', err);
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
          <h2>Select Slack Channels</h2>
          <button className="modal-close" onClick={onClose}>X</button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div className="modal-loading">
              <span className="spinner"></span>
              <p>Loading available channels...</p>
            </div>
          ) : error ? (
            <div className="modal-error">
              <p>{error}</p>
              <button className="btn btn-secondary" onClick={loadAvailableChannels}>
                Retry
              </button>
            </div>
          ) : channels.length === 0 ? (
            <div className="modal-empty">
              <p>{infoMessage || 'No available channels found.'}</p>
              <p className="hint-text">
                Only channels you created and the bot can access will appear.
              </p>
            </div>
          ) : (
            <>
              <p className="modal-description">
                Select channels you created for notifications.
              </p>
              <div className="channels-list">
                {channels.map((channel) => {
                  const isSelected = selectedChannels.has(channel.id);
                  return (
                    <div
                      key={channel.id}
                      className={`channel-item ${isSelected ? 'selected' : ''}`}
                      onClick={() => toggleChannel(channel)}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleChannel(channel)}
                        onClick={(e) => e.stopPropagation()}
                      />
                      <span className="channel-hash">#</span>
                      <span className="channel-name">{channel.name}</span>
                      {channel.is_private && (
                        <span className="channel-type-badge">Private</span>
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
            disabled={submitting || loading || channels.length === 0 || selectedChannels.size === 0}
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

export default SlackChannelSelectionModal;
