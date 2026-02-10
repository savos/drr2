import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import PublicLayout from './components/PublicLayout';
import DashboardLayout from './components/DashboardLayout';
import Home from './pages/Home';
import UnderDevelopment from './pages/UnderDevelopment';
import Login from './pages/Login';
import Auth from './pages/Auth';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import VerifyEmail from './pages/VerifyEmail';
import Dashboard from './pages/Dashboard';
import AddUser from './pages/AddUser';
import { authenticatedFetch } from './utils/api';
import PrivacyPolicy from './pages/PrivacyPolicy';
import TermsOfService from './pages/TermsOfService';
import CookiePolicy from './pages/CookiePolicy';
import AcceptableUsePolicy from './pages/AcceptableUsePolicy';
import SecurityPolicy from './pages/SecurityPolicy';
import Pricing from './pages/Pricing';

// Import dashboard pages
import {
  PlanPage,
  StatusPage,
  DeleteAccountPage,
  UserMonitorPage,
  AddDomainPage,
  AddSSLPage,
  StatusMonitorPage,
  EmailChannelPage,
  PushNotificationsPage,
  SlackChannelPage,
  TeamsChannelPage,
  DiscordChannelPage,
  TelegramChannelPage,
  GoogleChatChannelPage,
  ZoomChannelPage,
  WebexChannelPage,
  MattermostChannelPage,
  PagerDutyPage,
  BetterStackPage,
  GrafanaOnCallPage,
  ZapierPage,
  MakePage,
  N8nPage,
  PowerAutomatePage,
  PipedreamPage,
  SetRemindersPage,
  RemindersHistoryPage,
  SolutionsPage,
  ProductsPage,
  PartnersPage,
  CompanyPage,
} from './pages/DashboardPages';

// Tailwind styles are loaded via src/index.css and @layer components

// Protected Route Component
function ProtectedRoute({ children, user, authChecked }) {
  if (!authChecked) {
    return null;
  }
  return user ? children : <Navigate to="/login" replace />;
}

// Superuser Route Component
function SuperuserRoute({ children, user, authChecked }) {
  if (!authChecked) {
    return null;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (user.is_superuser) {
    return children;
  }
  return <Navigate to="/dashboard" replace />;
}

function App() {
  const [user, setUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    const loadUser = async () => {
      try {
        // Use plain fetch for initial auth check to avoid redirect loop on 401
        const response = await fetch('/api/auth/me', { credentials: 'include' });
        if (response.ok) {
          const data = await response.json();
          setUser(data);
          localStorage.setItem('user', JSON.stringify(data));
        } else {
          localStorage.removeItem('user');
          setUser(null);
        }
      } catch (err) {
        localStorage.removeItem('user');
        setUser(null);
      } finally {
        setAuthChecked(true);
      }
    };

    loadUser();
  }, []);

  const handleLogout = async () => {
    try {
      await authenticatedFetch('/api/auth/logout', { method: 'POST' });
    } catch (err) {
      // Ignore logout errors and still clear client state.
    } finally {
      localStorage.removeItem('user');
      setUser(null);
    }
  };

  const handleAuthSuccess = (nextUser) => {
    if (nextUser) {
      setUser(nextUser);
      localStorage.setItem('user', JSON.stringify(nextUser));
    }
  };

  return (
    <ThemeProvider>
      <Router>
        <div className="app-container">
          <Routes>
          {/* Under Development - no header */}
          <Route path="/" element={<UnderDevelopment />} />

          {/* Public Routes with Header */}
          <Route element={<PublicLayout user={user} onLogout={handleLogout} />}>
            <Route path="/home" element={<Home />} />
            <Route path="/login" element={<Login onAuthSuccess={handleAuthSuccess} />} />
            <Route path="/register" element={<Auth onAuthSuccess={handleAuthSuccess} />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/verify-email" element={<VerifyEmail onAuthSuccess={handleAuthSuccess} />} />
            <Route path="/solutions" element={<SolutionsPage />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/partners" element={<PartnersPage />} />
            <Route path="/company" element={<CompanyPage />} />

            {/* Legal Pages */}
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            <Route path="/terms-of-service" element={<TermsOfService />} />
            <Route path="/cookie-policy" element={<CookiePolicy />} />
            <Route path="/acceptable-use" element={<AcceptableUsePolicy />} />
            <Route path="/security" element={<SecurityPolicy />} />
          </Route>

          {/* Protected Dashboard Routes with DashboardHeader */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute user={user} authChecked={authChecked}>
                <DashboardLayout onLogout={handleLogout} />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />

            {/* Account Routes */}
            <Route path="plan" element={<PlanPage />} />
            <Route path="add-user" element={
              <SuperuserRoute user={user} authChecked={authChecked}>
                <AddUser />
              </SuperuserRoute>
            } />
            <Route path="user-monitor" element={<UserMonitorPage />} />
            <Route path="status" element={<StatusPage />} />
            <Route path="delete-account" element={
              <SuperuserRoute user={user} authChecked={authChecked}>
                <DeleteAccountPage />
              </SuperuserRoute>
            } />

            {/* Domain/SSL Routes */}
            <Route path="add-domain" element={
              <SuperuserRoute user={user} authChecked={authChecked}>
                <AddDomainPage />
              </SuperuserRoute>
            } />
            <Route path="add-ssl" element={
              <SuperuserRoute user={user} authChecked={authChecked}>
                <AddSSLPage />
              </SuperuserRoute>
            } />
            <Route path="status-monitor" element={<StatusMonitorPage />} />

            {/* Channel Routes */}
            <Route path="channels/email" element={<EmailChannelPage />} />
            <Route path="channels/push" element={<PushNotificationsPage />} />
            <Route path="channels/slack" element={<SlackChannelPage />} />
            <Route path="channels/teams" element={<TeamsChannelPage />} />
            <Route path="channels/discord" element={<DiscordChannelPage />} />
            <Route path="channels/telegram" element={<TelegramChannelPage />} />
            <Route path="channels/google-chat" element={<GoogleChatChannelPage />} />
            <Route path="channels/zoom" element={<ZoomChannelPage />} />
            <Route path="channels/webex" element={<WebexChannelPage />} />
            <Route path="channels/mattermost" element={<MattermostChannelPage />} />

            {/* Incident Management Routes */}
            <Route path="incident/pagerduty" element={<PagerDutyPage />} />
            <Route path="incident/betterstack" element={<BetterStackPage />} />
            <Route path="incident/grafana-oncall" element={<GrafanaOnCallPage />} />

            {/* Automation Routes */}
            <Route path="automation/n8n" element={<N8nPage />} />
            <Route path="automation/power-automate" element={<PowerAutomatePage />} />
            <Route path="automation/zapier" element={<ZapierPage />} />
            <Route path="automation/make" element={<MakePage />} />
            <Route path="automation/pipedream" element={<PipedreamPage />} />

            {/* Reminder Routes */}
            <Route path="set-reminders" element={<SetRemindersPage />} />
            <Route path="reminders-history" element={<RemindersHistoryPage />} />
          </Route>

          {/* Catch all - redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
    </ThemeProvider>
  );
}

export default App;
