import { Link } from 'react-router-dom';
import { AnimatedPage } from '../components/AnimatedPage';
import { Icon } from '../utils/icons';
import Footer from '../components/Footer';

function Solutions() {
  return (
    <AnimatedPage>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-zinc-900 dark:text-zinc-100 mb-6">
            Never Miss a Domain or SSL Renewal Again
          </h1>
          <p className="text-xl sm:text-2xl text-zinc-600 dark:text-zinc-400 max-w-4xl mx-auto leading-relaxed">
            DRR ensures your business stays online 24/7 with intelligent monitoring and multi-channel alerts for domain and SSL certificate expirations.
          </p>
        </div>

        {/* The Problem */}
        <div className="mb-20">
          <div className="bg-gradient-to-br from-red-50 to-orange-50 dark:from-red-950/20 dark:to-orange-950/20 rounded-2xl p-8 sm:p-12 border-2 border-red-200 dark:border-red-800">
            <div className="flex items-start gap-4 mb-6">
              <div className="shrink-0">
                <Icon name="warning" variant="solid" size="lg" className="text-red-600 dark:text-red-400" />
              </div>
              <div>
                <h2 className="text-2xl sm:text-3xl font-bold text-zinc-900 dark:text-zinc-100 mb-4">
                  One Missed Renewal = Business Disaster
                </h2>
                <p className="text-lg text-zinc-700 dark:text-zinc-300 leading-relaxed">
                  Expired domains and SSL certificates cause immediate service outages, lost revenue, damaged reputation, and security warnings that drive customers away. The average cost of downtime? <strong>$5,600 per minute</strong>. Don't let a forgotten renewal date destroy your business continuity.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* The Solution */}
        <div className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-zinc-900 dark:text-zinc-100 mb-4">
              Automated Protection for Your Digital Assets
            </h2>
            <p className="text-xl text-zinc-600 dark:text-zinc-400 max-w-3xl mx-auto">
              DRR continuously monitors your domains and SSL certificates, delivering timely reminders across your preferred channels so you never face an unexpected expiration.
            </p>
          </div>

          {/* Key Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8 mb-12">
            {/* Feature 1 */}
            <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 sm:p-8 border border-zinc-200 dark:border-zinc-700 shadow-depth-1 hover:shadow-depth-3 transition-all duration-200">
              <div className="mb-4">
                <Icon name="clock" variant="solid" size="lg" className="text-indigo-600 dark:text-indigo-400" />
              </div>
              <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
                Intelligent Monitoring
              </h3>
              <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
                Our system automatically tracks expiration dates for all your domains and SSL certificates, checking them 24/7 so you don't have to.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 sm:p-8 border border-zinc-200 dark:border-zinc-700 shadow-depth-1 hover:shadow-depth-3 transition-all duration-200">
              <div className="mb-4">
                <Icon name="bell" variant="solid" size="lg" className="text-indigo-600 dark:text-indigo-400" />
              </div>
              <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
                Customizable Reminders
              </h3>
              <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
                Set alerts for 15 days, 7 days, 3 days, 1 day—or any custom timeframe before expiration. Get multiple reminders to ensure renewals never slip through the cracks.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 sm:p-8 border border-zinc-200 dark:border-zinc-700 shadow-depth-1 hover:shadow-depth-3 transition-all duration-200">
              <div className="mb-4">
                <Icon name="chat" variant="solid" size="lg" className="text-indigo-600 dark:text-indigo-400" />
              </div>
              <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
                Multi-Channel Delivery
              </h3>
              <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
                Receive alerts via email, push notifications, Slack, Microsoft Teams, Discord, or Telegram. Choose the channels where your team actually works.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 sm:p-8 border border-zinc-200 dark:border-zinc-700 shadow-depth-1 hover:shadow-depth-3 transition-all duration-200">
              <div className="mb-4">
                <Icon name="link" variant="solid" size="lg" className="text-indigo-600 dark:text-indigo-400" />
              </div>
              <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
                Powerful Integrations
              </h3>
              <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
                Connect with workflow automation tools like Zapier, Make, Power Automate, n8n, and Pipedream to trigger custom actions when renewals are due.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 sm:p-8 border border-zinc-200 dark:border-zinc-700 shadow-depth-1 hover:shadow-depth-3 transition-all duration-200">
              <div className="mb-4">
                <Icon name="users" variant="solid" size="lg" className="text-indigo-600 dark:text-indigo-400" />
              </div>
              <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
                Team Collaboration
              </h3>
              <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
                Share monitoring responsibilities across your organization. Multiple team members can receive alerts and manage renewals together.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 sm:p-8 border border-zinc-200 dark:border-zinc-700 shadow-depth-1 hover:shadow-depth-3 transition-all duration-200">
              <div className="mb-4">
                <Icon name="check" variant="solid" size="lg" className="text-emerald-600 dark:text-emerald-400" />
              </div>
              <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
                Guaranteed Uptime
              </h3>
              <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
                With timely reminders across multiple channels, you'll never miss a renewal window. Keep your services running without interruption.
              </p>
            </div>
          </div>
        </div>

        {/* How It Works */}
        <div className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-zinc-900 dark:text-zinc-100 mb-4">
              Simple Setup, Powerful Protection
            </h2>
            <p className="text-xl text-zinc-600 dark:text-zinc-400 max-w-3xl mx-auto">
              Get started in minutes with our streamlined three-step process
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            {/* Step 1 */}
            <div className="flex gap-6 mb-8 pb-8 border-b border-zinc-200 dark:border-zinc-700">
              <div className="shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center font-bold text-xl">
                1
              </div>
              <div>
                <h3 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
                  Add Your Domains & SSL Certificates
                </h3>
                <p className="text-lg text-zinc-600 dark:text-zinc-400 leading-relaxed">
                  Import your domains and SSL certificates in seconds. DRR automatically detects expiration dates and begins monitoring immediately.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex gap-6 mb-8 pb-8 border-b border-zinc-200 dark:border-zinc-700">
              <div className="shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center font-bold text-xl">
                2
              </div>
              <div>
                <h3 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
                  Configure Your Reminder Schedule
                </h3>
                <p className="text-lg text-zinc-600 dark:text-zinc-400 leading-relaxed">
                  Choose when to receive alerts: 15 days out, 7 days, 3 days, 1 day—or create a custom schedule that matches your renewal workflow. Set up multiple reminders to ensure nothing falls through.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex gap-6 mb-8">
              <div className="shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center font-bold text-xl">
                3
              </div>
              <div>
                <h3 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
                  Select Your Communication Channels
                </h3>
                <p className="text-lg text-zinc-600 dark:text-zinc-400 leading-relaxed mb-4">
                  Connect the channels your team uses every day. Email is enabled by default, and you can add:
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-zinc-700 dark:text-zinc-300">
                  <div className="flex items-center gap-2">
                    <Icon name="check" variant="solid" size="sm" className="text-emerald-600 dark:text-emerald-400" />
                    <span>Push Notifications</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Icon name="check" variant="solid" size="sm" className="text-emerald-600 dark:text-emerald-400" />
                    <span>Slack</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Icon name="check" variant="solid" size="sm" className="text-emerald-600 dark:text-emerald-400" />
                    <span>Microsoft Teams</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Icon name="check" variant="solid" size="sm" className="text-emerald-600 dark:text-emerald-400" />
                    <span>Discord</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Icon name="check" variant="solid" size="sm" className="text-emerald-600 dark:text-emerald-400" />
                    <span>Telegram</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Icon name="check" variant="solid" size="sm" className="text-emerald-600 dark:text-emerald-400" />
                    <span>Automation Tools</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Business Impact */}
        <div className="mb-20">
          <div className="bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-950/20 dark:to-purple-950/20 rounded-2xl p-8 sm:p-12 border-2 border-indigo-200 dark:border-indigo-800">
            <h2 className="text-3xl sm:text-4xl font-bold text-zinc-900 dark:text-zinc-100 mb-6 text-center">
              Uninterrupted Business Continuity
            </h2>
            <div className="max-w-3xl mx-auto">
              <p className="text-lg text-zinc-700 dark:text-zinc-300 leading-relaxed mb-6">
                When your domains and SSL certificates are properly maintained, your business operates seamlessly. Your customers access your services without interruption. Your email continues flowing. Your security certificates remain valid. Your reputation stays intact.
              </p>
              <p className="text-lg text-zinc-700 dark:text-zinc-300 leading-relaxed mb-6">
                DRR acts as your safety net. At the scheduled times you configure—whether it's 15 days, 3 days, or 1 day before expiration—you receive clear, actionable reminders through your preferred channels. No more surprise expirations. No more emergency renewals. No more downtime.
              </p>
              <p className="text-lg text-zinc-700 dark:text-zinc-300 leading-relaxed">
                <strong>The result?</strong> Peace of mind. Business continuity. And the confidence that your digital infrastructure is protected around the clock by intelligent, automated monitoring that never sleeps.
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-zinc-900 dark:text-zinc-100 mb-6">
            Ready to Protect Your Business?
          </h2>
          <p className="text-xl text-zinc-600 dark:text-zinc-400 mb-8 max-w-2xl mx-auto">
            Join leading organizations that trust DRR to keep their services online 24/7
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              className="btn btn-primary btn-large w-full sm:w-auto"
            >
              Start Free Trial
            </Link>
            <Link
              to="/products"
              className="btn btn-secondary btn-large w-full sm:w-auto"
            >
              View Pricing
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <Footer />
    </AnimatedPage>
  );
}

export default Solutions;
