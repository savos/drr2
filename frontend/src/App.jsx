import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import PublicLayout from './components/PublicLayout';
import DashboardLayout from './components/DashboardLayout';
import Home from './pages/Home';
import Login from './pages/Login';
import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';
import AddUser from './pages/AddUser';

// Import dashboard pages
import {
  PlanPage,
  StatusPage,
  DeleteAccountPage,
  UserMonitorPage,
  AddDomainPage,
  AddSSLPage,
  DomainMonitorPage,
  SSLMonitorPage,
  EmailChannelPage,
  PushNotificationsPage,
  SlackChannelPage,
  TeamsChannelPage,
  DiscordChannelPage,
  TelegramChannelPage,
  ZapierPage,
  MakePage,
  N8nPage,
  SetRemindersPage,
  RemindersHistoryPage,
  AboutPage,
  ProductsPage,
  PartnersPage,
  CompanyPage,
} from './pages/DashboardPages';

import './App.css';

// Protected Route Component
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('access_token');
  return token ? children : <Navigate to="/login" replace />;
}

// Superuser Route Component
function SuperuserRoute({ children }) {
  const token = localStorage.getItem('access_token');
  const userStr = localStorage.getItem('user');

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  try {
    const user = JSON.parse(userStr);
    if (user && user.is_superuser) {
      return children;
    }
  } catch (e) {
    console.error('Failed to parse user data:', e);
  }

  // If not superuser, redirect to dashboard
  return <Navigate to="/dashboard" replace />;
}

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check if user is logged in
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <Router>
      <div className="app-container">
        <Routes>
          {/* Public Routes with Header */}
          <Route element={<PublicLayout user={user} onLogout={handleLogout} />}>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Auth />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/partners" element={<PartnersPage />} />
            <Route path="/company" element={<CompanyPage />} />
          </Route>

          {/* Protected Dashboard Routes with DashboardHeader */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardLayout onLogout={handleLogout} />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />

            {/* Account Routes */}
            <Route path="plan" element={<PlanPage />} />
            <Route path="add-user" element={
              <SuperuserRoute>
                <AddUser />
              </SuperuserRoute>
            } />
            <Route path="user-monitor" element={<UserMonitorPage />} />
            <Route path="status" element={<StatusPage />} />
            <Route path="delete-account" element={
              <SuperuserRoute>
                <DeleteAccountPage />
              </SuperuserRoute>
            } />

            {/* Domain/SSL Routes */}
            <Route path="add-domain" element={
              <SuperuserRoute>
                <AddDomainPage />
              </SuperuserRoute>
            } />
            <Route path="add-ssl" element={
              <SuperuserRoute>
                <AddSSLPage />
              </SuperuserRoute>
            } />
            <Route path="domain-monitor" element={<DomainMonitorPage />} />
            <Route path="ssl-monitor" element={<SSLMonitorPage />} />

            {/* Channel Routes */}
            <Route path="channels/email" element={<EmailChannelPage />} />
            <Route path="channels/push" element={<PushNotificationsPage />} />
            <Route path="channels/slack" element={<SlackChannelPage />} />
            <Route path="channels/teams" element={<TeamsChannelPage />} />
            <Route path="channels/discord" element={<DiscordChannelPage />} />
            <Route path="channels/telegram" element={<TelegramChannelPage />} />

            {/* Automation Routes */}
            <Route path="automation/zapier" element={<ZapierPage />} />
            <Route path="automation/make" element={<MakePage />} />
            <Route path="automation/n8n" element={<N8nPage />} />

            {/* Reminder Routes */}
            <Route path="set-reminders" element={<SetRemindersPage />} />
            <Route path="reminders-history" element={<RemindersHistoryPage />} />
          </Route>

          {/* Catch all - redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
