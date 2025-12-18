import { Link } from 'react-router-dom';
import './Home.css';

function Home() {
  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-image">
          <div className="placeholder-image">
            <span>🔒</span>
            <p>SSL Certificate</p>
          </div>
        </div>
        <div className="hero-content">
          <h1 className="hero-title">
            Your Business Runs on Trust<br />
            But...<br />
            One Expired Date Can Break It
          </h1>
          <p className="hero-subtitle">
            Every second, your domain and SSL certificates work invisibly to keep your business alive online.
            Your website loads. Emails deliver. Transactions process securely. Customers trust the padlock in their browser.
          </p>
          <p className="hero-warning">Until they don't.</p>
          <p className="hero-solution">
            Domain Renewal Reminder service will send you reminders if your domain or SSL is about to expire.
          </p>
          <div className="hero-cta">
            <Link to="/register" className="cta-button primary">
              Start Your Free Trial Today
            </Link>
            <Link to="/about" className="cta-button secondary">
              Learn More
            </Link>
          </div>
        </div>
      </section>

      {/* Problem Statement */}
      <section className="problem-section">
        <div className="container">
          <h2>What Happens When It Expires?</h2>
          <div className="problem-grid">
            <div className="problem-card">
              <div className="problem-icon">🌐</div>
              <h3>Site Vanishes</h3>
              <p>Your website disappears from search results instantly</p>
            </div>
            <div className="problem-card">
              <div className="problem-icon">📧</div>
              <h3>Email Bounces</h3>
              <p>All business communication grinds to a halt</p>
            </div>
            <div className="problem-card">
              <div className="problem-icon">💳</div>
              <h3>Payments Fail</h3>
              <p>Transaction systems stop processing orders</p>
            </div>
            <div className="problem-card">
              <div className="problem-icon">⚠️</div>
              <h3>Trust Broken</h3>
              <p>Browsers warn visitors your site is "Not Secure"</p>
            </div>
          </div>
          <div className="damage-note">
            <p>The damage compounds by the minute: lost sales, abandoned carts, confused customers, and a reputation that takes months to rebuild.</p>
            <p className="emphasis emphasis-large">This isn't a remote possibility. It's a recurring reality that has cost businesses millions.</p>
          </div>
        </div>
      </section>

      {/* Hidden Risk Section */}
      <section className="risk-section">
        <div className="container">
          <h2>The Hidden Risk No One Thinks About<br />(Until It's Too Late)</h2>
          <div className="risk-examples">
            <div className="risk-card">
              <h3>Microsoft Teams</h3>
              <p>Went offline globally when an authentication certificate expired unnoticed. <strong>Millions couldn't work.</strong></p>
            </div>
            <div className="risk-card">
              <h3>Marketo.com</h3>
              <p>Let their domain lapse—crashing not just their site, but <strong>thousands of customer campaigns</strong> running on their platform.</p>
            </div>
            <div className="risk-card">
              <h3>LinkedIn, O2, Cisco, Foursquare, Regions Bank</h3>
              <p>The list goes on. These aren't small startups. They're <strong>household names with entire IT departments.</strong></p>
            </div>
          </div>
          <p className="risk-conclusion">
            If it happened to them, it can happen to anyone.
          </p>
          <div className="culprit-box">
            <p>The culprit is never negligence—it's <strong>complexity</strong>.</p>
            <ul>
              <li>Domains registered years ago with a different team</li>
              <li>SSL certificates buried in a departing developer's inbox</li>
              <li>Renewal notices sent to defunct email addresses</li>
              <li>Credit cards that expired and were never updated</li>
            </ul>
          </div>
          <p className="risk-tagline">One forgotten date. One overlooked email. One moment of bad timing.</p>
        </div>
      </section>

      {/* Solution Section */}
      <section className="solution-section">
        <div className="container">
          <h2>DRR: The Insurance Policy for Your Digital Foundation</h2>
          <p className="section-intro">
            Think of how you protect everything else vital to your business—insurance for your office, your equipment, your team.
            You don't question those expenses because the alternative is unthinkable.
          </p>
          <p className="emphasis centered-protection">Your domain and SSL certificates deserve the same protection.</p>

          <div className="solution-description">
            <p>
              <strong>Domain & SSL Renewal Reminder (DRR)</strong> acts as your silent guardian—automatically tracking every domain
              and certificate you own, across every provider, and sending timely reminders so you never miss a renewal deadline.
            </p>
          </div>

          <h3>What You Get:</h3>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h4>Unified Dashboard</h4>
              <p>All your digital assets in one place—no more hunting through registrar accounts or forwarded emails</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔄</div>
              <h4>Automated Reminders</h4>
              <p>Timely renewal alerts sent automatically with full visibility into upcoming expirations</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🛡️</div>
              <h4>Brand Protection</h4>
              <p>Protection from domain squatters who monitor expired domains to steal your brand</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔐</div>
              <h4>SSL Management</h4>
              <p>Certificate management ensuring your site never shows security warnings</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🌍</div>
              <h4>Multi-Provider Support</h4>
              <p>Works with most major registrars and certificate providers, tracking domains and SSL certificates where expiration data is available</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">💼</div>
              <h4>Scalable Peace of Mind</h4>
              <p>From your first domain to your hundredth, without adding workload</p>
            </div>
          </div>
        </div>
      </section>

      {/* Cost Section */}
      <section className="cost-section">
        <div className="container">
          <h2>The Real Cost of Forgetting to "Remember to Renew It"</h2>
          <p className="section-intro downtime-cost-highlight">A single hour of downtime can cost:</p>
          <div className="cost-grid">
            <div className="cost-card">
              <h3>E-commerce Sites</h3>
              <p className="cost-amount">$100,000+</p>
              <p>in lost sales</p>
            </div>
            <div className="cost-card">
              <h3>SaaS Platforms</h3>
              <p className="cost-amount">Churned Customers</p>
              <p>who can't log in</p>
            </div>
            <div className="cost-card">
              <h3>Service Businesses</h3>
              <p className="cost-amount">Lost Bookings</p>
              <p>that never happen</p>
            </div>
            <div className="cost-card">
              <h3>Every Business</h3>
              <p className="cost-amount">SEO Rankings</p>
              <p>that take months to recover</p>
            </div>
          </div>

          <div className="recovery-costs">
            <h3>Recovery Costs Compound Fast:</h3>
            <ul>
              <li>Emergency domain reclamation fees</li>
              <li>Premium SSL rush orders</li>
              <li>Customer support fielding confused inquiries</li>
              <li>PR damage control</li>
            </ul>
          </div>

          <div className="value-prop">
            <p className="highlight">
              For less than the cost of a business lunch each month, DRR eliminates this entire category of risk.
            </p>
          </div>
        </div>
      </section>

      {/* Continuity Section */}
      <section className="continuity-section">
        <div className="container">
          <h2>You're Not Buying Reminders. You're Buying Continuity.</h2>
          <p>Every business has a breaking point—a threshold where "we'll handle it manually" becomes "how did we let this happen?"</p>

          <div className="breaking-points">
            <div className="breaking-point">
              <p>Maybe it's when your team grows beyond the person who "just knew" when renewals were due.</p>
            </div>
            <div className="breaking-point">
              <p>Maybe it's when you acquire another company and inherit their tangled domain portfolio.</p>
            </div>
            <div className="breaking-point">
              <p>Maybe it's simply when you realize that betting your entire online presence on remembering a date is a bet you shouldn't be making.</p>
            </div>
          </div>

          <p className="conclusion-statement">
            DRR isn't an expense. It's <strong>insurance for the foundation your business stands on.</strong>
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <h2>Don't Wait for the Crisis</h2>
          <p>Your competitors aren't taking this risk. Your customers won't give you a second chance. And the internet won't send a warning before your domain expires.</p>

          <div className="cta-buttons">
            <Link to="/register" className="cta-button large primary">
              Start Your Free Trial Today
            </Link>
            <p className="cta-note">Full protection, zero setup required</p>
          </div>

          <p className="closing-message">
            Because the most expensive mistake is the one you never saw coming.
          </p>

          <p className="trust-badge">
            Trusted by businesses who understand that the smallest details protect the biggest investments.
          </p>
        </div>
      </section>

      {/* Real-World Cases Section */}
      <section className="cases-section">
        <div className="container">
          <h2>Real-World Cases: When Digital Foundations Crumbled</h2>
          <p className="section-intro">
            These incidents aren't hypothetical—they're documented failures that cost real companies real money, customers, and credibility:
          </p>

          <div className="cases-grid">
            <div className="case-card">
              <h3>Microsoft Teams Global Outage (2020)</h3>
              <p>An expired authentication certificate took down Microsoft Teams worldwide, affecting millions of users unable to access the platform for work.</p>
              <a href="https://www.engadget.com/2020-02-03-microsoft-teams-expired-certificate.html" target="_blank" rel="noopener noreferrer" className="read-more">Read more →</a>
            </div>

            <div className="case-card">
              <h3>Marketo.com Domain Expiration (2018)</h3>
              <p>Marketing automation giant Marketo let their primary domain expire, causing their site and thousands of customer campaigns to go dark.</p>
              <a href="https://www.theregister.com/2018/10/25/marketo_domain_expired/" target="_blank" rel="noopener noreferrer" className="read-more">Read more →</a>
            </div>

            <div className="case-card">
              <h3>LinkedIn Certificate Expiration (2021)</h3>
              <p>An expired SSL certificate caused widespread login failures and security warnings for LinkedIn users globally.</p>
              <a href="https://www.thesslstore.com/blog/linkedin-ssl-certificate-expired/" target="_blank" rel="noopener noreferrer" className="read-more">Read more →</a>
            </div>

            <div className="case-card">
              <h3>O2 UK Network Outage (2018)</h3>
              <p>An expired Ericsson software certificate caused a complete network failure affecting 32 million O2 customers for over 24 hours.</p>
              <a href="https://www.theregister.com/2018/12/06/ericsson_o2_telefonica_uk_outage/" target="_blank" rel="noopener noreferrer" className="read-more">Read more →</a>
            </div>

            <div className="case-card">
              <h3>Spotify Certificate Issue (2020 & 2022)</h3>
              <p>Expired certificates caused service outages affecting millions of Spotify users, with major incidents in both 2020 and 2022.</p>
              <a href="https://www.bleepingcomputer.com/news/technology/spotify-hit-with-outage-after-forgetting-to-renew-a-certifficate/" target="_blank" rel="noopener noreferrer" className="read-more">Read more →</a>
            </div>

            <div className="case-card">
              <h3>Equifax Certificate Expiration (2017)</h3>
              <p>An expired security certificate prevented detection of the massive data breach for 76 days, affecting 147.9 million Americans.</p>
              <a href="https://www.thesslstore.com/blog/the-equifax-data-breach-went-undetected-for-76-days-because-of-an-expired-certificate/" target="_blank" rel="noopener noreferrer" className="read-more">Read more →</a>
            </div>

            <div className="case-card">
              <h3>Foursquare Domain Lapse</h3>
              <p>The location services company accidentally let a critical domain expire, causing service disruptions and customer confusion.</p>
              <a href="https://techcrunch.com/2010/10/26/foursquare-domain-name-expires/" target="_blank" rel="noopener noreferrer" className="read-more">Read more →</a>
            </div>

            <div className="case-card">
              <h3>Regions Bank Certificate Failure (2016)</h3>
              <p>An SSL certificate issue locked customers out of online banking for hours, causing significant frustration and service complaints.</p>
              <a href="https://www.al.com/business/2016/11/regions_online_banking_down_fo.html" target="_blank" rel="noopener noreferrer" className="read-more">Read more →</a>
            </div>

            <div className="case-card">
              <h3>Instagram Push Notification Failure (2019)</h3>
              <p>An expired certificate disabled push notifications for millions of Instagram users worldwide.</p>
              <a href="https://www.theverge.com/2019/5/21/18634327/instagram-push-notifications-down-outage" target="_blank" rel="noopener noreferrer" className="read-more">Read more →</a>
            </div>

            <div className="case-card">
              <h3>National Health Service (NHS) Certificate Issue (2018)</h3>
              <p>Expired SSL certificates affected NHS login systems, preventing healthcare workers from accessing critical patient systems.</p>
              <a href="https://www.digitalhealth.net/2018/05/nhs-digital-certificate-error/" target="_blank" rel="noopener noreferrer" className="read-more">Read more →</a>
            </div>
          </div>

          <p className="cases-conclusion">
            These are just the public cases we know about. Countless smaller businesses face the same failures without making headlines—but with equally devastating consequences.
          </p>
        </div>
      </section>

      {/* Final CTA */}
      <section className="final-cta-section">
        <div className="container">
          <h2>Protect Your Digital Foundation Today</h2>
          <Link to="/register" className="cta-button large primary">
            Get Started Now – Free Trial
          </Link>
        </div>
      </section>
    </div>
  );
}

export default Home;
