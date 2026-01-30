import { Link, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '../utils/icons';

function Sidebar({ isMobileOpen, onMobileClose }) {
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

  // Close mobile sidebar on route change
  useEffect(() => {
    if (isMobileOpen && onMobileClose) {
      onMobileClose();
    }
  }, [location.pathname]);

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
        { name: 'Status Monitor', path: '/dashboard/status-monitor' },
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
        { name: 'Google Chat', path: '/dashboard/channels/google-chat' },
        { name: 'Zoom Team Chat', path: '/dashboard/channels/zoom' },
        { name: 'Cisco Webex', path: '/dashboard/channels/webex' },
        { name: 'Mattermost', path: '/dashboard/channels/mattermost' },
      ]
    },
    {
      title: 'Incident Management',
      links: [
        { name: 'PagerDuty', path: '/dashboard/incident/pagerduty' },
        { name: 'BetterStack', path: '/dashboard/incident/betterstack' },
        { name: 'Grafana OnCall', path: '/dashboard/incident/grafana-oncall' },
      ]
    },
    {
      title: 'Automation Tools',
      links: [
        { name: 'n8n', path: '/dashboard/automation/n8n' },
        { name: 'Power Automate', path: '/dashboard/automation/power-automate' },
        { name: 'Zapier', path: '/dashboard/automation/zapier' },
        { name: 'Make', path: '/dashboard/automation/make' },
        { name: 'Pipedream', path: '/dashboard/automation/pipedream' },
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

  const SidebarContent = () => (
    <div className="py-6">
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
          <div key={index} className="mb-6">
            <h3 className="px-6 mb-2 text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
              {section.title}
            </h3>
            <ul className="space-y-1 px-3">
              {visibleLinks.map((link, linkIndex) => (
                <li key={linkIndex}>
                  <Link
                    to={link.path}
                    className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive(link.path)
                        ? 'bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300'
                        : 'text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 hover:text-zinc-900 dark:hover:text-zinc-100'
                    }`}
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
  );

  return (
    <>
      {/* Desktop Sidebar - Always visible on large screens */}
      <aside className="hidden lg:block w-64 bg-white dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800 h-full overflow-y-auto">
        <SidebarContent />
      </aside>

      {/* Mobile Sidebar - Overlay with backdrop */}
      <AnimatePresence>
        {isMobileOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="lg:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
              onClick={onMobileClose}
            />

            {/* Sidebar */}
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ duration: 0.3, type: 'spring', damping: 30, stiffness: 300 }}
              className="lg:hidden fixed left-0 top-0 bottom-0 w-64 bg-white dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800 z-50 overflow-y-auto shadow-depth-5"
            >
              {/* Close button */}
              <div className="sticky top-0 bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 px-4 py-3 flex items-center justify-between z-10">
                <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">Menu</span>
                <button
                  onClick={onMobileClose}
                  className="p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                  aria-label="Close menu"
                >
                  <Icon name="close" size="md" className="text-zinc-600 dark:text-zinc-400" />
                </button>
              </div>
              <SidebarContent />
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}

export default Sidebar;
