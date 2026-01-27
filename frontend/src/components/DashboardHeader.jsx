import { Link, useNavigate } from 'react-router-dom';
import { Icon } from '../utils/icons';
import { ThemeToggle } from './ThemeToggle';

function DashboardHeader({ onLogout, onMenuClick }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    }
    navigate('/');
  };

  return (
    <header className="bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 shadow-sm sticky top-0 z-30">
      <div className="px-4 sm:px-6 py-4 flex items-center justify-between">
        {/* Left: Hamburger + Logo */}
        <div className="flex items-center gap-3">
          {/* Hamburger Menu - Mobile Only */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
            aria-label="Open menu"
          >
            <Icon name="menu" size="md" className="text-zinc-600 dark:text-zinc-400" />
          </button>

          {/* Logo */}
          <Link to="/dashboard" className="no-underline">
            <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 dark:from-indigo-500 dark:to-indigo-600 text-white font-bold text-xl px-4 py-2 rounded-lg shadow-depth-1 hover:shadow-depth-2 transition-shadow">
              DRR
            </div>
          </Link>
        </div>

        {/* Right: Theme Toggle + Sign Out Button */}
        <div className="flex items-center gap-3">
          {/* Theme Toggle */}
          <ThemeToggle />

          {/* Sign Out Button */}
          <button
            onClick={handleLogout}
            className="px-4 sm:px-6 py-2 bg-red-500 hover:bg-red-600 dark:bg-red-600 dark:hover:bg-red-700 text-white font-medium rounded-lg transition-colors text-sm sm:text-base"
          >
            Sign Out
          </button>
        </div>
      </div>
    </header>
  );
}

export default DashboardHeader;
