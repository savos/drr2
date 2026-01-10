import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function Home() {
  const [cases, setCases] = useState([]);
  const [expandedCases, setExpandedCases] = useState({});
  const [loading, setLoading] = useState(true);
  const [visibleCount, setVisibleCount] = useState(9);

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const response = await fetch('/api/cases');
        if (response.ok) {
          const data = await response.json();
          setCases(data);
        }
      } catch (error) {
        console.error('Failed to fetch cases:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCases();
  }, []);

  const toggleCase = (caseId) => {
    setExpandedCases(prev => ({
      ...prev,
      [caseId]: !prev[caseId]
    }));
  };

  const formatLinkText = (url) => {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname.replace('www.', '');
    } catch {
      return url;
    }
  };

  const handleShowMore = () => {
    setVisibleCount(prev => prev + 9);
  };

  const visibleCases = cases.slice(0, visibleCount);
  const hasMoreCases = visibleCount < cases.length;

  return (
    <div className="min-h-[calc(100vh-70px)]">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-[#667eea] to-[#764ba2] min-h-[80vh] py-16 px-5 flex items-center justify-center text-white relative">
        <div className="absolute left-10 top-1/2 -translate-y-1/2 hidden lg:block">
          <div className="bg-white/10 border-[3px] border-white/30 rounded-[20px] p-10 text-center backdrop-blur-sm">
            <span className="text-7xl block mb-4">🔒</span>
            <p className="text-base font-semibold m-0">SSL Certificate</p>
          </div>
        </div>
        <div className="max-w-[910px] text-center flex flex-col justify-center mx-auto z-10">
          <h1 className="text-4xl md:text-5xl font-extrabold mb-6 leading-tight">
            Your Business Runs on Trust<br />
            But...<br />
            One Expired Date Can Break It
          </h1>
          <p className="text-lg md:text-xl leading-relaxed mb-5 opacity-95">
            Every second, your domain and SSL certificates work invisibly to keep your business alive online.
            Your website loads. Emails deliver. Transactions process securely. Customers trust the padlock in their browser.
          </p>
          <p className="text-xl md:text-[22px] font-bold italic mb-5 text-yellow-300">Until they don't.</p>
          <p className="text-2xl leading-relaxed mb-10 opacity-95 font-medium">
            Domain Renewal Reminder service will send you reminders if your domain or SSL is about to expire.
          </p>
          <div className="flex gap-4 flex-wrap justify-center">
            <Link to="/register" className="px-9 py-4 rounded-lg text-base font-bold transition-all duration-300 inline-block text-center bg-white text-[#667eea] hover:-translate-y-[3px] hover:shadow-[0_10px_25px_rgba(0,0,0,0.2)]">
              Start Your Free Trial Today
            </Link>
            <Link to="/about" className="px-9 py-4 rounded-lg text-base font-bold transition-all duration-300 inline-block text-center bg-white/15 text-white border-2 border-white hover:bg-white/25">
              Learn More
            </Link>
          </div>
        </div>
      </section>

      {/* Problem Statement */}
      <section className="py-24 px-5 bg-gray-50">
        <div className="max-w-[1200px] mx-auto">
          <h2 className="text-3xl md:text-[42px] text-center mb-16 text-gray-800 font-extrabold">What Happens When It Expires?</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
            <div className="bg-white p-10 rounded-xl text-center shadow-md transition-all duration-300 hover:-translate-y-2 hover:shadow-xl">
              <div className="text-5xl mb-5">🌐</div>
              <h3 className="text-xl font-bold mb-3 text-red-700">Site Vanishes</h3>
              <p className="text-base text-gray-500 leading-relaxed">Your website disappears from search results instantly</p>
            </div>
            <div className="bg-white p-10 rounded-xl text-center shadow-md transition-all duration-300 hover:-translate-y-2 hover:shadow-xl">
              <div className="text-5xl mb-5">📧</div>
              <h3 className="text-xl font-bold mb-3 text-red-700">Email Bounces</h3>
              <p className="text-base text-gray-500 leading-relaxed">All business communication grinds to a halt</p>
            </div>
            <div className="bg-white p-10 rounded-xl text-center shadow-md transition-all duration-300 hover:-translate-y-2 hover:shadow-xl">
              <div className="text-5xl mb-5">💳</div>
              <h3 className="text-xl font-bold mb-3 text-red-700">Payments Fail</h3>
              <p className="text-base text-gray-500 leading-relaxed">Transaction systems stop processing orders</p>
            </div>
            <div className="bg-white p-10 rounded-xl text-center shadow-md transition-all duration-300 hover:-translate-y-2 hover:shadow-xl">
              <div className="text-5xl mb-5">⚠️</div>
              <h3 className="text-xl font-bold mb-3 text-red-700">Trust Broken</h3>
              <p className="text-base text-gray-500 leading-relaxed">Browsers warn visitors your site is "Not Secure"</p>
            </div>
          </div>
          <div className="max-w-[900px] mx-auto text-center p-10 bg-white rounded-xl shadow-md">
            <p className="text-lg leading-relaxed text-gray-600 mb-4">The damage compounds by the minute: lost sales, abandoned carts, confused customers, and a reputation that takes months to rebuild.</p>
            <p className="font-bold text-gray-800 text-xl">This isn't a remote possibility. It's a recurring reality that has cost businesses millions.</p>
          </div>
        </div>
      </section>

      {/* Hidden Risk Section */}
      <section className="py-24 px-5 bg-gradient-to-br from-gray-800 to-gray-900 text-white">
        <div className="max-w-[1200px] mx-auto">
          <h2 className="text-3xl md:text-[42px] text-center mb-16 font-extrabold leading-tight">The Hidden Risk No One Thinks About<br />(Until It's Too Late)</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            <div className="bg-white/5 p-9 rounded-xl border-2 border-white/10 backdrop-blur-sm">
              <h3 className="text-2xl mb-4 text-yellow-300 font-bold">Microsoft Teams</h3>
              <p className="text-[17px] leading-relaxed opacity-90">Went offline globally when an authentication certificate expired unnoticed. <strong>Millions couldn't work.</strong></p>
            </div>
            <div className="bg-white/5 p-9 rounded-xl border-2 border-white/10 backdrop-blur-sm">
              <h3 className="text-2xl mb-4 text-yellow-300 font-bold">Marketo.com</h3>
              <p className="text-[17px] leading-relaxed opacity-90">Let their domain lapse—crashing not just their site, but <strong>thousands of customer campaigns</strong> running on their platform.</p>
            </div>
            <div className="bg-white/5 p-9 rounded-xl border-2 border-white/10 backdrop-blur-sm">
              <h3 className="text-2xl mb-4 text-yellow-300 font-bold">LinkedIn, O2, Cisco, Foursquare, Regions Bank</h3>
              <p className="text-[17px] leading-relaxed opacity-90">The list goes on. These aren't small startups. They're <strong>household names with entire IT departments.</strong></p>
            </div>
          </div>
          <p className="text-2xl text-center font-bold my-12 text-yellow-300">
            If it happened to them, it can happen to anyone.
          </p>
          <div className="bg-white/10 p-12 rounded-xl border-l-[6px] border-yellow-300 max-w-[640px] mx-auto">
            <p className="text-xl leading-relaxed mb-5">The culprit is never negligence—it's <strong>complexity</strong>.</p>
            <ul className="list-none p-0 my-8">
              <li className="text-lg py-3 pl-8 relative leading-relaxed before:content-['▸'] before:absolute before:left-0 before:text-yellow-300 before:font-bold">Domains registered years ago with a different team</li>
              <li className="text-lg py-3 pl-8 relative leading-relaxed before:content-['▸'] before:absolute before:left-0 before:text-yellow-300 before:font-bold">SSL certificates buried in a departing developer's inbox</li>
              <li className="text-lg py-3 pl-8 relative leading-relaxed before:content-['▸'] before:absolute before:left-0 before:text-yellow-300 before:font-bold">Renewal notices sent to defunct email addresses</li>
              <li className="text-lg py-3 pl-8 relative leading-relaxed before:content-['▸'] before:absolute before:left-0 before:text-yellow-300 before:font-bold">Credit cards that expired and were never updated</li>
            </ul>
          </div>
          <p className="text-3xl md:text-[42px] font-extrabold text-white text-center mt-12 max-w-[900px] mx-auto leading-tight">One forgotten date. One overlooked email. One moment of bad timing.</p>
        </div>
      </section>

      {/* Solution Section */}
      <section className="py-24 px-5 bg-white">
        <div className="max-w-[1200px] mx-auto">
          <h2 className="text-3xl md:text-[42px] text-center mb-10 text-gray-800 font-extrabold">DRR: The Insurance Policy for Your Digital Foundation</h2>
          <p className="text-xl text-center max-w-[900px] mx-auto mb-5 text-gray-600 leading-relaxed">
            Think of how you protect everything else vital to your business—insurance for your office, your equipment, your team.
            You don't question those expenses because the alternative is unthinkable.
          </p>
          <p className="font-bold text-gray-800 text-xl text-center">Your domain and SSL certificates deserve the same protection.</p>

          <div className="max-w-[900px] mx-auto my-10 text-center p-10 bg-gray-50 rounded-xl">
            <p className="text-xl leading-relaxed text-gray-800">
              <strong>Domain & SSL Renewal Reminder (DRR)</strong> acts as your silent guardian—automatically tracking every domain
              and certificate you own, across every provider, and sending timely reminders so you never miss a renewal deadline.
            </p>
          </div>

          <h3 className="text-3xl text-center my-10 text-gray-800 font-bold">What You Get:</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-10">
            <div className="bg-gray-50 p-10 rounded-xl transition-all duration-300 border-2 border-transparent hover:-translate-y-[5px] hover:shadow-xl hover:border-[#667eea]">
              <div className="text-5xl mb-5">📊</div>
              <h4 className="text-xl font-bold mb-3 text-gray-800">Unified Dashboard</h4>
              <p className="text-base text-gray-500 leading-relaxed">All your digital assets in one place—no more hunting through registrar accounts or forwarded emails</p>
            </div>
            <div className="bg-gray-50 p-10 rounded-xl transition-all duration-300 border-2 border-transparent hover:-translate-y-[5px] hover:shadow-xl hover:border-[#667eea]">
              <div className="text-5xl mb-5">🔄</div>
              <h4 className="text-xl font-bold mb-3 text-gray-800">Automated Reminders</h4>
              <p className="text-base text-gray-500 leading-relaxed">Timely renewal alerts sent automatically with full visibility into upcoming expirations</p>
            </div>
            <div className="bg-gray-50 p-10 rounded-xl transition-all duration-300 border-2 border-transparent hover:-translate-y-[5px] hover:shadow-xl hover:border-[#667eea]">
              <div className="text-5xl mb-5">🛡️</div>
              <h4 className="text-xl font-bold mb-3 text-gray-800">Brand Protection</h4>
              <p className="text-base text-gray-500 leading-relaxed">Protection from domain squatters who monitor expired domains to steal your brand</p>
            </div>
            <div className="bg-gray-50 p-10 rounded-xl transition-all duration-300 border-2 border-transparent hover:-translate-y-[5px] hover:shadow-xl hover:border-[#667eea]">
              <div className="text-5xl mb-5">🔐</div>
              <h4 className="text-xl font-bold mb-3 text-gray-800">SSL Management</h4>
              <p className="text-base text-gray-500 leading-relaxed">Certificate management ensuring your site never shows security warnings</p>
            </div>
            <div className="bg-gray-50 p-10 rounded-xl transition-all duration-300 border-2 border-transparent hover:-translate-y-[5px] hover:shadow-xl hover:border-[#667eea]">
              <div className="text-5xl mb-5">🌍</div>
              <h4 className="text-xl font-bold mb-3 text-gray-800">Multi-Provider Support</h4>
              <p className="text-base text-gray-500 leading-relaxed">Works with most major registrars and certificate providers, tracking domains and SSL certificates where expiration data is available</p>
            </div>
            <div className="bg-gray-50 p-10 rounded-xl transition-all duration-300 border-2 border-transparent hover:-translate-y-[5px] hover:shadow-xl hover:border-[#667eea]">
              <div className="text-5xl mb-5">💼</div>
              <h4 className="text-xl font-bold mb-3 text-gray-800">Scalable Peace of Mind</h4>
              <p className="text-base text-gray-500 leading-relaxed">From your first domain to your hundredth, without adding workload</p>
            </div>
          </div>
        </div>
      </section>

      {/* Cost Section */}
      <section className="py-24 px-5 bg-gradient-to-br from-red-700 to-red-800 text-white">
        <div className="max-w-[1200px] mx-auto">
          <h2 className="text-3xl md:text-[42px] text-center mb-10 font-extrabold">The Real Cost of Forgetting to "Remember to Renew It"</h2>
          <p className="text-2xl md:text-3xl text-center font-bold text-yellow-300">A single hour of downtime can cost:</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 my-12">
            <div className="bg-white/10 p-10 rounded-xl text-center backdrop-blur-sm border-2 border-white/20">
              <h3 className="text-xl font-bold mb-5">E-commerce Sites</h3>
              <p className="text-3xl font-extrabold my-5 text-yellow-300">$100,000+</p>
              <p>in lost sales</p>
            </div>
            <div className="bg-white/10 p-10 rounded-xl text-center backdrop-blur-sm border-2 border-white/20">
              <h3 className="text-xl font-bold mb-5">SaaS Platforms</h3>
              <p className="text-3xl font-extrabold my-5 text-yellow-300">Churned Customers</p>
              <p>who can't log in</p>
            </div>
            <div className="bg-white/10 p-10 rounded-xl text-center backdrop-blur-sm border-2 border-white/20">
              <h3 className="text-xl font-bold mb-5">Service Businesses</h3>
              <p className="text-3xl font-extrabold my-5 text-yellow-300">Lost Bookings</p>
              <p>that never happen</p>
            </div>
            <div className="bg-white/10 p-10 rounded-xl text-center backdrop-blur-sm border-2 border-white/20">
              <h3 className="text-xl font-bold mb-5">Every Business</h3>
              <p className="text-3xl font-extrabold my-5 text-yellow-300">SEO Rankings</p>
              <p>that take months to recover</p>
            </div>
          </div>

          <div className="max-w-[700px] mx-auto my-16 bg-white/10 p-10 rounded-xl backdrop-blur-sm">
            <h3 className="text-2xl font-bold mb-6">Recovery Costs Compound Fast:</h3>
            <ul className="list-none p-0">
              <li className="text-lg py-3 pl-8 relative leading-relaxed before:content-['✗'] before:absolute before:left-0 before:text-yellow-300 before:font-bold before:text-xl">Emergency domain reclamation fees</li>
              <li className="text-lg py-3 pl-8 relative leading-relaxed before:content-['✗'] before:absolute before:left-0 before:text-yellow-300 before:font-bold before:text-xl">Premium SSL rush orders</li>
              <li className="text-lg py-3 pl-8 relative leading-relaxed before:content-['✗'] before:absolute before:left-0 before:text-yellow-300 before:font-bold before:text-xl">Customer support fielding confused inquiries</li>
              <li className="text-lg py-3 pl-8 relative leading-relaxed before:content-['✗'] before:absolute before:left-0 before:text-yellow-300 before:font-bold before:text-xl">PR damage control</li>
            </ul>
          </div>

          <div className="max-w-[800px] mx-auto mt-16 text-center">
            <p className="text-2xl font-bold p-10 bg-white/15 rounded-xl backdrop-blur-sm border-[3px] border-yellow-300 leading-relaxed">
              For less than the cost of a business lunch each month, DRR eliminates this entire category of risk.
            </p>
          </div>
        </div>
      </section>

      {/* Continuity Section */}
      <section className="py-24 px-5 bg-white">
        <div className="max-w-[1200px] mx-auto">
          <h2 className="text-3xl md:text-[42px] text-center mb-10 text-gray-800 font-extrabold">You're Not Buying Reminders. You're Buying Continuity.</h2>
          <p className="text-xl text-center max-w-[900px] mx-auto mb-16 text-gray-600 leading-relaxed">Every business has a breaking point—a threshold where "we'll handle it manually" becomes "how did we let this happen?"</p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <div className="bg-gray-50 p-9 rounded-xl border-l-[5px] border-[#667eea]">
              <p className="text-lg leading-relaxed text-gray-600 m-0">Maybe it's when your team grows beyond the person who "just knew" when renewals were due.</p>
            </div>
            <div className="bg-gray-50 p-9 rounded-xl border-l-[5px] border-[#667eea]">
              <p className="text-lg leading-relaxed text-gray-600 m-0">Maybe it's when you acquire another company and inherit their tangled domain portfolio.</p>
            </div>
            <div className="bg-gray-50 p-9 rounded-xl border-l-[5px] border-[#667eea]">
              <p className="text-lg leading-relaxed text-gray-600 m-0">Maybe it's simply when you realize that betting your entire online presence on remembering a date is a bet you shouldn't be making.</p>
            </div>
          </div>

          <p className="text-2xl md:text-[28px] text-center text-gray-800 max-w-[900px] mx-auto p-12 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl leading-relaxed">
            DRR isn't an expense. It's <strong>insurance for the foundation your business stands on.</strong>
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-5 bg-gradient-to-br from-[#667eea] to-[#764ba2] text-white text-center">
        <div className="max-w-[1200px] mx-auto">
          <h2 className="text-4xl md:text-5xl mb-8 font-extrabold">Don't Wait for the Crisis</h2>
          <p className="text-xl md:text-[22px] max-w-[900px] mx-auto mb-12 leading-relaxed">Your competitors aren't taking this risk. Your customers won't give you a second chance. And the internet won't send a warning before your domain expires.</p>

          <div className="my-16">
            <Link to="/register" className="px-12 py-5 rounded-lg text-lg font-bold transition-all duration-300 inline-block text-center bg-white text-[#667eea] hover:-translate-y-[3px] hover:shadow-[0_10px_25px_rgba(0,0,0,0.2)]">
              Start Your Free Trial Today
            </Link>
            <p className="text-base mt-5 opacity-90 italic">Full protection, zero setup required</p>
          </div>

          <p className="text-2xl font-bold my-12 italic">
            Because the most expensive mistake is the one you never saw coming.
          </p>

          <p className="text-lg opacity-90 italic">
            Trusted by businesses who understand that the smallest details protect the biggest investments.
          </p>
        </div>
      </section>

      {/* Real-World Cases Section */}
      <section className="py-24 px-5 bg-gray-50">
        <div className="max-w-[1200px] mx-auto">
          <h2 className="text-3xl md:text-[42px] text-center mb-8 text-gray-800 font-extrabold">Real-World Cases: When Digital Foundations Crumbled</h2>
          <p className="text-xl text-center max-w-[900px] mx-auto mb-5 text-gray-600 leading-relaxed">
            These incidents aren't hypothetical—they're documented failures that cost real companies real money, customers, and credibility:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 my-16">
            {loading ? (
              <div className="col-span-full text-center py-16 text-gray-500 text-lg">Loading cases...</div>
            ) : visibleCases.length > 0 ? (
              visibleCases.map((caseItem) => (
                <div key={caseItem.id} className="relative bg-white p-9 rounded-xl shadow-md transition-all duration-300 border-l-[5px] border-red-700 hover:-translate-y-[5px] hover:shadow-xl">
                  <span className="absolute top-3 left-3 text-xs text-gray-500">{caseItem.problem.toUpperCase()}</span>
                  <span className="absolute top-3 right-3 text-sm text-gray-500">{caseItem.year}</span>
                  <h5 className="text-center text-sm font-semibold text-[#667eea] uppercase tracking-wider mb-3 mt-2">{caseItem.company}</h5>
                  <h3 className="text-xl font-bold mb-4 text-gray-800">{caseItem.heading}</h3>
                  <p className="text-base leading-relaxed text-gray-600 mb-4">{caseItem.text}</p>
                  {caseItem.links && caseItem.links.length > 0 && (
                    <div className="mt-4">
                      <button
                        className={`inline-flex items-center gap-2 bg-transparent border-none text-[#667eea] font-semibold text-[15px] cursor-pointer py-2 transition-colors duration-200 hover:text-[#764ba2]`}
                        onClick={() => toggleCase(caseItem.id)}
                      >
                        {expandedCases[caseItem.id] ? 'Hide sources' : 'Show sources'}
                        <span className={`text-[10px] transition-transform duration-300 ${expandedCases[caseItem.id] ? 'rotate-180' : ''}`}>
                          {expandedCases[caseItem.id] ? '▲' : '▼'}
                        </span>
                      </button>
                      <div className={`flex flex-col gap-2 overflow-hidden transition-all duration-300 ${expandedCases[caseItem.id] ? 'max-h-[300px] pt-3' : 'max-h-0'}`}>
                        {caseItem.links.map((link) => (
                          <a
                            key={link.id}
                            href={link.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-block text-[#667eea] text-sm no-underline py-1.5 px-3 bg-gray-50 rounded-md transition-all duration-200 border-l-[3px] border-[#667eea] hover:bg-gray-100 hover:text-[#764ba2] hover:border-[#764ba2]"
                          >
                            {formatLinkText(link.link)}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="col-span-full text-center py-16 text-gray-500 text-lg">No cases available.</div>
            )}
          </div>

          {hasMoreCases && (
            <div className="text-center mt-10">
              <button
                className="bg-transparent border-none text-[#667eea] text-base font-semibold cursor-pointer py-3 px-6 transition-all duration-200 hover:text-[#764ba2] hover:underline"
                onClick={handleShowMore}
              >
                Show More
              </button>
            </div>
          )}

          <p className="text-xl text-center max-w-[900px] mx-auto mt-16 text-gray-800 leading-relaxed italic p-10 bg-white rounded-xl shadow-md">
            These are just the public cases we know about. Countless smaller businesses face the same failures without making headlines—but with equally devastating consequences.
          </p>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 px-5 bg-gradient-to-br from-gray-800 to-gray-900 text-white text-center">
        <div className="max-w-[1200px] mx-auto">
          <h2 className="text-4xl md:text-5xl mb-10 font-extrabold">Protect Your Digital Foundation Today</h2>
          <Link to="/register" className="px-12 py-5 rounded-lg text-lg font-bold transition-all duration-300 inline-block text-center bg-white text-[#667eea] hover:-translate-y-[3px] hover:shadow-[0_10px_25px_rgba(0,0,0,0.2)]">
            Get Started Now – Free Trial
          </Link>
        </div>
      </section>
    </div>
  );
}

export default Home;
