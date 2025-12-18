import { Outlet } from 'react-router-dom';
import DashboardHeader from './DashboardHeader';
import Sidebar from './Sidebar';
import './DashboardLayout.css';

function DashboardLayout({ onLogout }) {
  return (
    <>
      <DashboardHeader onLogout={onLogout} />
      <div className="dashboard-container">
        <Sidebar />
        <main className="dashboard-main">
          <Outlet />
        </main>
      </div>
    </>
  );
}

export default DashboardLayout;
