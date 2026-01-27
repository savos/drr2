import { useState, useEffect } from 'react';
import { authenticatedFetch } from '../utils/api';

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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Select Slack Channels</h2>
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
              <p className="text-gray-600">Loading available channels...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12">
              <p className="text-red-600 mb-4">{error}</p>
              <button
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg transition-colors"
                onClick={loadAvailableChannels}
              >
                Retry
              </button>
            </div>
          ) : channels.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <p className="text-gray-700 mb-2">{infoMessage || 'No available channels found.'}</p>
              <p className="text-sm text-gray-500">
                Only channels you created and the bot can access will appear.
              </p>
            </div>
          ) : (
            <>
              <p className="text-sm text-gray-600 mb-4">
                Select channels you created for notifications.
              </p>
              <div className="space-y-2">
                {channels.map((channel) => {
                  const isSelected = selectedChannels.has(channel.id);
                  return (
                    <div
                      key={channel.id}
                      className={`flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors ${
                        isSelected ? 'bg-purple-50 border-purple-300 hover:bg-purple-100' : ''
                      }`}
                      onClick={() => toggleChannel(channel)}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleChannel(channel)}
                        onClick={(e) => e.stopPropagation()}
                        className="w-4 h-4 text-purple-600 rounded"
                      />
                      <span className="text-gray-500 font-medium">#</span>
                      <span className="flex-1 text-sm text-gray-900 font-medium">{channel.name}</span>
                      {channel.is_private && (
                        <span className="px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded">
                          Private
                        </span>
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
            disabled={submitting || loading || channels.length === 0 || selectedChannels.size === 0}
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

export default SlackChannelSelectionModal;
