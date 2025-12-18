import { Link, useNavigate } from 'react-router-dom';
import './Header.css';

function Header({ user, onLogout }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    }
    navigate('/');
  };

  return (
    <header className="main-header">
      <div className="header-content">
        {/* Left: Logo */}
        <div className="header-left">
          <Link to="/" className="logo-link">
            <div className="logo-placeholder">
              DRR
            </div>
          </Link>
        </div>

        {/* Center: Navigation Links */}
        <nav className="header-nav">
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/about" className="nav-link">About</Link>
          <Link to="/products" className="nav-link">Products</Link>
          <Link to="/partners" className="nav-link">Partners</Link>
          <Link to="/company" className="nav-link">Company</Link>
        </nav>

        {/* Right: Auth Links */}
        <div className="header-right">
          {user ? (
            <button onClick={handleLogout} className="auth-button logout">
              Sign Out
            </button>
          ) : (
            <>
              <Link to="/login" className="auth-button secondary">
                Sign In
              </Link>
              <Link to="/register" className="auth-button primary">
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
