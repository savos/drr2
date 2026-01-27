import { Link, useNavigate } from 'react-router-dom';

function Header({ user, onLogout }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    }
    navigate('/');
  };

  return (
    <header className="bg-white shadow-md">
      <div className="container mx-auto px-6 py-4 flex items-center justify-between">
        {/* Left: Logo */}
        <div className="flex items-center">
          <Link to="/" className="no-underline">
            <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold text-xl px-4 py-2 rounded-lg">
              DRR
            </div>
          </Link>
        </div>

        {/* Center: Navigation Links */}
        <nav className="hidden md:flex items-center gap-6">
          <Link to="/" className="text-gray-700 hover:text-purple-600 transition-colors font-medium">Home</Link>
          <Link to="/about" className="text-gray-700 hover:text-purple-600 transition-colors font-medium">About</Link>
          <Link to="/products" className="text-gray-700 hover:text-purple-600 transition-colors font-medium">Products</Link>
          <Link to="/partners" className="text-gray-700 hover:text-purple-600 transition-colors font-medium">Partners</Link>
          <Link to="/company" className="text-gray-700 hover:text-purple-600 transition-colors font-medium">Company</Link>
        </nav>

        {/* Right: Auth Links */}
        <div className="flex items-center gap-3">
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
                className="px-6 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-lg transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors"
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
