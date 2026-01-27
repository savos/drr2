import StubPage from './StubPage';
import Slack from './Slack';
import Telegram from './Telegram';
import Discord from './Discord';
import Teams from './Teams';
import Email from './Email';
import Solutions from './Solutions';

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
  return <Email />;
}

export function PushNotificationsPage() {
  return <StubPage title="Push Notifications" description="Enable browser push notifications for instant alerts." />;
}

export function SlackChannelPage() {
  return <Slack />;
}

export function TeamsChannelPage() {
  return <Teams />;
}

export function DiscordChannelPage() {
  return <Discord />;
}

export function TelegramChannelPage() {
  return <Telegram />;
}

export function GoogleChatChannelPage() {
  return <StubPage title="Google Chat Integration" description="Send domain and SSL expiration notifications to Google Chat spaces." />;
}

export function ZoomChannelPage() {
  return <StubPage title="Zoom Team Chat Integration" description="Receive domain reminders directly in Zoom Team Chat." />;
}

export function WebexChannelPage() {
  return <StubPage title="Cisco Webex Integration" description="Get notified about domain expirations in Cisco Webex spaces." />;
}

export function MattermostChannelPage() {
  return <StubPage title="Mattermost Integration" description="Connect with your self-hosted Mattermost for domain notifications." />;
}

// Incident Management Pages
export function PagerDutyPage() {
  return <StubPage title="PagerDuty Integration" description="Create incidents in PagerDuty when domains or SSL certificates are about to expire." />;
}

export function BetterStackPage() {
  return <StubPage title="BetterStack Integration" description="Send domain expiration alerts to BetterStack for incident management." />;
}

export function GrafanaOnCallPage() {
  return <StubPage title="Grafana OnCall Integration" description="Route domain expiration alerts through Grafana OnCall." />;
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

export function PowerAutomatePage() {
  return <StubPage title="Power Automate Integration" description="Connect with Microsoft Power Automate for workflow automation." />;
}

export function PipedreamPage() {
  return <StubPage title="Pipedream Integration" description="Build workflows with Pipedream's developer-friendly automation platform." />;
}

// Reminder Pages
export function SetRemindersPage() {
  return <StubPage title="Set Reminders" description="Configure when and how you want to be reminded about domain expirations." />;
}

export function RemindersHistoryPage() {
  return <StubPage title="Reminders History" description="View history of all sent reminders and notifications." />;
}

// Static Pages
export function SolutionsPage() {
  return <Solutions />;
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
