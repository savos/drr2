import { Link, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import './Sidebar.css';

function Sidebar() {
  const location = useLocation();
  const [isSuperuser, setIsSuperuser] = useState(false);

  useEffect(() => {
    // Get user from localStorage
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        setIsSuperuser(!!user.is_superuser);
      } catch (e) {
        console.error('Failed to parse user data:', e);
      }
    }
  }, []);

  const isActive = (path) => {
    return location.pathname === path;
  };

  const menuSections = [
    {
      title: 'Account',
      links: [
        { name: 'Plan', path: '/dashboard/plan' },
        { name: 'Add User', path: '/dashboard/add-user', superuserOnly: true },
        { name: 'User Monitor', path: '/dashboard/user-monitor' },
        { name: 'Status', path: '/dashboard/status' },
        { name: 'Delete Account', path: '/dashboard/delete-account', superuserOnly: true },
      ]
    },
    {
      title: 'DOMAINS/SSLs',
      links: [
        { name: 'Add Domain', path: '/dashboard/add-domain', superuserOnly: true },
        { name: 'Add SSL', path: '/dashboard/add-ssl', superuserOnly: true },
        { name: 'Domain Monitor', path: '/dashboard/domain-monitor' },
        { name: 'SSL Monitor', path: '/dashboard/ssl-monitor' },
      ]
    },
    {
      title: 'Channels',
      links: [
        { name: 'Email', path: '/dashboard/channels/email' },
        { name: 'Push Notifications', path: '/dashboard/channels/push' },
        { name: 'Slack', path: '/dashboard/channels/slack' },
        { name: 'MS Teams', path: '/dashboard/channels/teams' },
        { name: 'Discord', path: '/dashboard/channels/discord' },
        { name: 'Telegram', path: '/dashboard/channels/telegram' },
      ]
    },
    {
      title: 'Automation Tools',
      links: [
        { name: 'Zapier', path: '/dashboard/automation/zapier' },
        { name: 'Make', path: '/dashboard/automation/make' },
        { name: 'n8n', path: '/dashboard/automation/n8n' },
      ]
    },
    {
      title: 'Reminders',
      links: [
        { name: 'Set Reminders', path: '/dashboard/set-reminders' },
        { name: 'Reminders History', path: '/dashboard/reminders-history' },
      ]
    },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-content">
        {menuSections.map((section, index) => {
          // Filter links based on superuser status
          const visibleLinks = section.links.filter(link => {
            // If link requires superuser and user is not superuser, hide it
            if (link.superuserOnly && !isSuperuser) {
              return false;
            }
            return true;
          });

          // Only render section if it has visible links
          if (visibleLinks.length === 0) {
            return null;
          }

          return (
            <div key={index} className="sidebar-section">
              <h3 className="section-title">{section.title}</h3>
              <ul className="section-links">
                {visibleLinks.map((link, linkIndex) => (
                  <li key={linkIndex}>
                    <Link
                      to={link.path}
                      className={`sidebar-link ${isActive(link.path) ? 'active' : ''}`}
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </aside>
  );
}

export default Sidebar;
