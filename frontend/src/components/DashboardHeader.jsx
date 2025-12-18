import { Link, useNavigate } from 'react-router-dom';
import './DashboardHeader.css';

function DashboardHeader({ onLogout }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    }
    navigate('/');
  };

  return (
    <header className="dashboard-header">
      <div className="dashboard-header-content">
        {/* Left: Logo */}
        <div className="dashboard-header-left">
          <Link to="/dashboard" className="dashboard-logo-link">
            <div className="dashboard-logo">
              DRR
            </div>
          </Link>
        </div>

        {/* Right: Sign Out Button */}
        <div className="dashboard-header-right">
          <button onClick={handleLogout} className="dashboard-logout-button">
            Sign Out
          </button>
        </div>
      </div>
    </header>
  );
}

export default DashboardHeader;
