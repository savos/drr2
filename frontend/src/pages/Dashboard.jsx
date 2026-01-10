import { useEffect, useState } from 'react';
// Tailwind component mappings in index.css replace the old CSS file

function Dashboard() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  return (
    <div className="dashboard-home">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Welcome back{user ? `, ${user.firstname}` : ''}!</h1>
        <p className="dashboard-subtitle">Here's an overview of your domain monitoring dashboard</p>
      </div>

      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-icon">🌐</div>
          <div className="stat-content">
            <div className="stat-value">0</div>
            <div className="stat-label">Total Domains</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <div className="stat-value">0</div>
            <div className="stat-label">Expiring Soon</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🔔</div>
          <div className="stat-content">
            <div className="stat-value">0</div>
            <div className="stat-label">Active Reminders</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-value">0</div>
            <div className="stat-label">Channels Connected</div>
          </div>
        </div>
      </div>

      <div className="dashboard-quick-actions">
        <h2 className="section-title">Quick Actions</h2>
        <div className="quick-actions-grid">
          <a href="/dashboard/add-domain" className="action-card">
            <span className="action-icon">➕</span>
            <span className="action-text">Add Domain</span>
          </a>
          <a href="/dashboard/set-reminders" className="action-card">
            <span className="action-icon">⏰</span>
            <span className="action-text">Set Reminder</span>
          </a>
          <a href="/dashboard/channels/slack" className="action-card">
            <span className="action-icon">🔗</span>
            <span className="action-text">Connect Channel</span>
          </a>
          <a href="/dashboard/domain-monitor" className="action-card">
            <span className="action-icon">👁️</span>
            <span className="action-text">View Domains</span>
          </a>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
