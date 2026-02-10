import { Link, useNavigate } from 'react-router-dom';
import { ThemeToggle } from './ThemeToggle';

function Header({ user, onLogout }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    }
    navigate('/');
  };

  return (
    <header className="bg-white dark:bg-zinc-900 shadow-md dark:border-b dark:border-zinc-800 sticky top-0 z-40">
      <div className="container mx-auto px-6 py-4 flex items-center justify-between">
        {/* Left: Logo */}
        <div className="flex items-center">
          <Link to="/" className="no-underline">
            <div className="bg-gradient-to-r from-purple-600 to-indigo-600 dark:from-indigo-500 dark:to-indigo-600 text-white font-bold text-xl px-4 py-2 rounded-lg">
              DRR
            </div>
          </Link>
        </div>

        {/* Center: Navigation Links */}
        <nav className="hidden md:flex items-center gap-6">
          <Link to="/" className="text-gray-700 dark:text-zinc-300 hover:text-purple-600 dark:hover:text-indigo-400 transition-colors font-medium">Home</Link>
          <Link to="/solutions" className="text-gray-700 dark:text-zinc-300 hover:text-purple-600 dark:hover:text-indigo-400 transition-colors font-medium">Solutions</Link>
          <Link to="/products" className="text-gray-700 dark:text-zinc-300 hover:text-purple-600 dark:hover:text-indigo-400 transition-colors font-medium">Products</Link>
          <Link to="/pricing" className="text-gray-700 dark:text-zinc-300 hover:text-purple-600 dark:hover:text-indigo-400 transition-colors font-medium">Pricing</Link>
          <Link to="/partners" className="text-gray-700 dark:text-zinc-300 hover:text-purple-600 dark:hover:text-indigo-400 transition-colors font-medium">Partners</Link>
          <Link to="/company" className="text-gray-700 dark:text-zinc-300 hover:text-purple-600 dark:hover:text-indigo-400 transition-colors font-medium">Company</Link>
        </nav>

        {/* Right: Theme Toggle + Auth Links */}
        <div className="flex items-center gap-3">
          {/* Theme Toggle */}
          <ThemeToggle />
          
          {user ? (
            <button
              onClick={handleLogout}
              className="px-6 py-2 bg-red-500 hover:bg-red-600 text-white font-medium rounded-lg transition-colors"
            >
              Sign Out
            </button>
          ) : (
            <>
              <Link
                to="/login"
                className="px-6 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-zinc-700 dark:hover:bg-zinc-600 text-gray-800 dark:text-zinc-100 font-medium rounded-lg transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-6 py-2 bg-purple-600 hover:bg-purple-700 dark:bg-indigo-600 dark:hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors"
              >
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
