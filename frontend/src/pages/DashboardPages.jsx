import StubPage from './StubPage';

// Account Pages
export function PlanPage() {
  return <StubPage title="Plan" description="Manage your subscription plan and billing information." />;
}

export function StatusPage() {
  return <StubPage title="Status" description="View your account status and usage statistics." />;
}

export function DeleteAccountPage() {
  return <StubPage title="Delete Account" description="Permanently delete your account and all associated data." />;
}

export function UserMonitorPage() {
  return <StubPage title="User Monitor" description="View and manage all users in your company." />;
}

// Domain Pages
export function AddDomainPage() {
  return <StubPage title="Add Domain" description="Add a new domain to monitor for expiration dates." />;
}

export function AddSSLPage() {
  return <StubPage title="Add SSL" description="Add a new SSL certificate to monitor for expiration dates." />;
}

export function DomainMonitorPage() {
  return <StubPage title="Domain Monitor" description="View and manage all your monitored domains." />;
}

export function SSLMonitorPage() {
  return <StubPage title="SSL Monitor" description="View and manage all your monitored SSL certificates." />;
}

// Channel Pages
export function EmailChannelPage() {
  return <StubPage title="Email Notifications" description="Configure email notification settings for domain reminders." />;
}

export function PushNotificationsPage() {
  return <StubPage title="Push Notifications" description="Enable browser push notifications for instant alerts." />;
}

export function SlackChannelPage() {
  return <StubPage title="Slack Integration" description="Connect your Slack workspace to receive domain reminders." />;
}

export function TeamsChannelPage() {
  return <StubPage title="Microsoft Teams" description="Integrate with MS Teams for team-wide notifications." />;
}

export function DiscordChannelPage() {
  return <StubPage title="Discord Integration" description="Connect Discord to get alerts in your server." />;
}

export function TelegramChannelPage() {
  return <StubPage title="Telegram Bot" description="Set up Telegram bot for instant domain alerts." />;
}

// Automation Pages
export function ZapierPage() {
  return <StubPage title="Zapier Integration" description="Connect with 5000+ apps using Zapier automation." />;
}

export function MakePage() {
  return <StubPage title="Make Integration" description="Create powerful workflows with Make (formerly Integromat)." />;
}

export function N8nPage() {
  return <StubPage title="n8n Integration" description="Self-hosted workflow automation with n8n." />;
}

// Reminder Pages
export function SetRemindersPage() {
  return <StubPage title="Set Reminders" description="Configure when and how you want to be reminded about domain expirations." />;
}

export function RemindersHistoryPage() {
  return <StubPage title="Reminders History" description="View history of all sent reminders and notifications." />;
}

// Static Pages
export function AboutPage() {
  return <StubPage title="About DRR" description="Learn more about Domain Renewal Reminder and our mission." />;
}

export function ProductsPage() {
  return <StubPage title="Products" description="Explore our products and pricing plans." />;
}

export function PartnersPage() {
  return <StubPage title="Partners" description="Meet our partners and integration providers." />;
}

export function CompanyPage() {
  return <StubPage title="Company" description="Learn about our company, team, and values." />;
}
