import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Icon } from '../utils/icons';
import Footer from '../components/Footer';

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

  const fadeInUp = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5 }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-zinc-950">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-indigo-600 via-indigo-700 to-indigo-800 dark:from-indigo-800 dark:via-indigo-900 dark:to-zinc-950 min-h-[90vh] py-20 px-5 flex items-center justify-center text-white overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-72 h-72 bg-indigo-400/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-400/10 rounded-full blur-3xl"></div>
        </div>

        {/* SSL Certificate floating card - Desktop only */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="absolute left-10 top-1/2 -translate-y-1/2 hidden lg:block z-10"
        >
          <div className="bg-white/10 border-2 border-white/20 rounded-2xl p-8 text-center backdrop-blur-lg shadow-depth-5">
            <div className="w-16 h-16 mx-auto mb-4 bg-white/20 rounded-xl flex items-center justify-center">
              <Icon name="shield" size="xl" className="text-white" />
            </div>
            <p className="text-base font-semibold">SSL Certificate</p>
          </div>
        </motion.div>

        <div className="max-w-5xl text-center flex flex-col justify-center mx-auto z-10 relative">
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-4xl md:text-6xl lg:text-7xl font-extrabold mb-8 leading-tight"
          >
            Your Business Runs on Trust<br />
            <span className="text-indigo-200">But...</span><br />
            One Expired Date Can Break It
          </motion.h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg md:text-xl lg:text-2xl leading-relaxed mb-6 opacity-95 max-w-4xl mx-auto"
          >
            Every second, your domain and SSL certificates work invisibly to keep your business alive online.
            Your website loads. Emails deliver. Transactions process securely. Customers trust the padlock in their browser.
          </motion.p>

          <motion.p
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="text-2xl md:text-3xl font-bold mb-6 text-amber-300"
          >
            Until they don't.
          </motion.p>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="text-xl md:text-2xl leading-relaxed mb-12 opacity-95 font-medium max-w-3xl mx-auto"
          >
            Domain Renewal Reminder service will send you reminders if your domain or SSL is about to expire.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="flex gap-4 flex-wrap justify-center"
          >
            <Link
              to="/register"
              className="group px-8 py-4 rounded-xl text-lg font-bold transition-all duration-300 inline-flex items-center gap-2 bg-white text-indigo-600 hover:-translate-y-1 hover:shadow-depth-5 shadow-depth-3"
            >
              Start Your Free Trial Today
              <Icon name="rocket" size="md" className="group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/solutions"
              className="px-8 py-4 rounded-xl text-lg font-bold transition-all duration-300 inline-flex items-center gap-2 bg-white/10 text-white border-2 border-white/30 hover:bg-white/20 backdrop-blur-sm"
            >
              Learn More
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Problem Statement */}
      <section className="py-24 px-5 bg-zinc-50 dark:bg-zinc-900">
        <div className="max-w-7xl mx-auto">
          <motion.h2
            {...fadeInUp}
            className="text-3xl md:text-5xl text-center mb-16 text-zinc-900 dark:text-zinc-100 font-extrabold"
          >
            What Happens When It Expires?
          </motion.h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {[
              { icon: 'globe', title: 'Site Vanishes', desc: 'Your website disappears from search results instantly', color: 'text-red-600 dark:text-red-400' },
              { icon: 'envelope', title: 'Email Bounces', desc: 'All business communication grinds to a halt', color: 'text-orange-600 dark:text-orange-400' },
              { icon: 'chart', title: 'Payments Fail', desc: 'Transaction systems stop processing orders', color: 'text-amber-600 dark:text-amber-400' },
              { icon: 'warning', title: 'Trust Broken', desc: 'Browsers warn visitors your site is "Not Secure"', color: 'text-red-600 dark:text-red-400' }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-white dark:bg-zinc-800 p-8 rounded-2xl text-center shadow-depth-1 transition-all duration-300 hover:-translate-y-2 hover:shadow-depth-3 border border-zinc-200 dark:border-zinc-700"
              >
                <div className="mb-5">
                  <Icon name={item.icon} variant="solid" size="xl" className={item.color} />
                </div>
                <h3 className="text-xl font-bold mb-3 text-red-700 dark:text-red-400">{item.title}</h3>
                <p className="text-base text-zinc-600 dark:text-zinc-400 leading-relaxed">{item.desc}</p>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="max-w-4xl mx-auto text-center p-10 bg-white dark:bg-zinc-800 rounded-2xl shadow-depth-2 border border-zinc-200 dark:border-zinc-700"
          >
            <p className="text-lg leading-relaxed text-zinc-600 dark:text-zinc-400 mb-4">
              The damage compounds by the minute: lost sales, abandoned carts, confused customers, and a reputation that takes months to rebuild.
            </p>
            <p className="font-bold text-zinc-900 dark:text-zinc-100 text-xl">
              This isn't a remote possibility. It's a recurring reality that has cost businesses millions.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Hidden Risk Section */}
      <section className="py-24 px-5 bg-gradient-to-br from-zinc-800 to-zinc-950 dark:from-zinc-950 dark:to-black text-white">
        <div className="max-w-7xl mx-auto">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl md:text-5xl text-center mb-16 font-extrabold leading-tight"
          >
            The Hidden Risk No One Thinks About<br />
            <span className="text-amber-400">(Until It's Too Late)</span>
          </motion.h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            {[
              { company: 'Microsoft Teams', text: 'Went offline globally when an authentication certificate expired unnoticed. Millions couldn\'t work.' },
              { company: 'Marketo.com', text: 'Let their domain lapse—crashing not just their site, but thousands of customer campaigns running on their platform.' },
              { company: 'LinkedIn, O2, Cisco, Foursquare', text: 'The list goes on. These aren\'t small startups. They\'re household names with entire IT departments.' }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-white/5 p-8 rounded-2xl border border-white/10 backdrop-blur-sm hover:bg-white/10 transition-all duration-300"
              >
                <h3 className="text-2xl mb-4 text-amber-400 font-bold">{item.company}</h3>
                <p className="text-lg leading-relaxed opacity-90">{item.text}</p>
              </motion.div>
            ))}
          </div>

          <motion.p
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl text-center font-bold my-12 text-amber-400"
          >
            If it happened to them, it can happen to anyone.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-white/10 p-12 rounded-2xl border-l-8 border-amber-400 max-w-3xl mx-auto backdrop-blur-sm"
          >
            <p className="text-xl leading-relaxed mb-5">The culprit is never negligence—it's <strong>complexity</strong>.</p>
            <ul className="list-none p-0 my-8 space-y-4">
              {[
                'Domains registered years ago with a different team',
                'SSL certificates buried in a departing developer\'s inbox',
                'Renewal notices sent to defunct email addresses',
                'Credit cards that expired and were never updated'
              ].map((item, index) => (
                <li key={index} className="flex items-start gap-3">
                  <Icon name="warning" size="sm" className="text-amber-400 mt-1 flex-shrink-0" />
                  <span className="text-lg leading-relaxed">{item}</span>
                </li>
              ))}
            </ul>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-3xl md:text-5xl font-extrabold text-white text-center mt-16 max-w-5xl mx-auto leading-tight"
          >
            One forgotten date. One overlooked email. One moment of bad timing.
          </motion.p>
        </div>
      </section>

      {/* Solution Section */}
      <section className="py-24 px-5 bg-white dark:bg-zinc-900">
        <div className="max-w-7xl mx-auto">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl md:text-5xl text-center mb-10 text-zinc-900 dark:text-zinc-100 font-extrabold"
          >
            DRR: The Insurance Policy for Your Digital Foundation
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-xl text-center max-w-4xl mx-auto mb-5 text-zinc-600 dark:text-zinc-400 leading-relaxed"
          >
            Think of how you protect everything else vital to your business—insurance for your office, your equipment, your team.
            You don't question those expenses because the alternative is unthinkable.
          </motion.p>

          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="font-bold text-zinc-900 dark:text-zinc-100 text-xl text-center mb-12"
          >
            Your domain and SSL certificates deserve the same protection.
          </motion.p>

          <motion.h3
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-3xl text-center my-16 text-zinc-900 dark:text-zinc-100 font-bold"
          >
            What You Get:
          </motion.h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-10">
            {[
              { icon: 'chart', title: 'Unified Dashboard', desc: 'All your digital assets in one place—no more hunting through registrar accounts or forwarded emails' },
              { icon: 'refresh', title: 'Automated Reminders', desc: 'Timely renewal alerts sent automatically with full visibility into upcoming expirations' },
              { icon: 'shield', title: 'Brand Protection', desc: 'Protection from domain squatters who monitor expired domains to steal your brand' },
              { icon: 'shield', title: 'SSL Management', desc: 'Certificate management ensuring your site never shows security warnings' },
              { icon: 'globe', title: 'Multi-Provider Support', desc: 'Works with most major registrars and certificate providers, tracking domains and SSL certificates where expiration data is available' },
              { icon: 'rocket', title: 'Scalable Peace of Mind', desc: 'From your first domain to your hundredth, without adding workload' }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-zinc-50 dark:bg-zinc-800 p-8 rounded-2xl transition-all duration-300 border-2 border-transparent hover:-translate-y-2 hover:shadow-depth-4 hover:border-indigo-300 dark:hover:border-indigo-600"
              >
                <div className="mb-5">
                  <Icon name={item.icon} variant="solid" size="xl" className="text-indigo-600 dark:text-indigo-400" />
                </div>
                <h4 className="text-xl font-bold mb-3 text-zinc-900 dark:text-zinc-100">{item.title}</h4>
                <p className="text-base text-zinc-600 dark:text-zinc-400 leading-relaxed">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Real-World Cases Section */}
      {cases.length > 0 && (
        <section className="py-24 px-5 bg-zinc-50 dark:bg-zinc-950">
          <div className="max-w-7xl mx-auto">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-3xl md:text-5xl text-center mb-8 text-zinc-900 dark:text-zinc-100 font-extrabold"
            >
              Real-World Cases: When Digital Foundations Crumbled
            </motion.h2>

            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="text-xl text-center max-w-4xl mx-auto mb-12 text-zinc-600 dark:text-zinc-400 leading-relaxed"
            >
              These incidents aren't hypothetical—they're documented failures that cost real companies real money, customers, and credibility:
            </motion.p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 my-16">
              {loading ? (
                <div className="col-span-full text-center py-16">
                  <div className="inline-block w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-4"></div>
                  <p className="text-zinc-500 dark:text-zinc-400 text-lg">Loading cases...</p>
                </div>
              ) : (
                visibleCases.map((caseItem, index) => (
                  <motion.div
                    key={caseItem.id}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: index * 0.05 }}
                    className="relative bg-white dark:bg-zinc-800 p-8 rounded-2xl shadow-depth-2 transition-all duration-300 border-l-4 border-red-600 hover:-translate-y-2 hover:shadow-depth-4"
                  >
                    <span className="absolute top-3 left-3 text-xs text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {caseItem.problem}
                    </span>
                    <span className="absolute top-3 right-3 text-sm text-zinc-500 dark:text-zinc-400 font-semibold">
                      {caseItem.year}
                    </span>
                    <h5 className="text-center text-sm font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider mb-3 mt-6">
                      {caseItem.company}
                    </h5>
                    <h3 className="text-xl font-bold mb-4 text-zinc-900 dark:text-zinc-100">{caseItem.heading}</h3>
                    <p className="text-base leading-relaxed text-zinc-600 dark:text-zinc-400 mb-4">{caseItem.text}</p>
                    {caseItem.links && caseItem.links.length > 0 && (
                      <div className="mt-4">
                        <button
                          className="inline-flex items-center gap-2 bg-transparent border-none text-indigo-600 dark:text-indigo-400 font-semibold text-sm cursor-pointer py-2 transition-colors duration-200 hover:text-indigo-700 dark:hover:text-indigo-300"
                          onClick={() => toggleCase(caseItem.id)}
                        >
                          {expandedCases[caseItem.id] ? 'Hide sources' : 'Show sources'}
                          <motion.span
                            animate={{ rotate: expandedCases[caseItem.id] ? 180 : 0 }}
                            transition={{ duration: 0.3 }}
                          >
                            <Icon name="chevron" size="xs" className="text-current" />
                          </motion.span>
                        </button>
                        <motion.div
                          initial={false}
                          animate={{
                            height: expandedCases[caseItem.id] ? 'auto' : 0,
                            opacity: expandedCases[caseItem.id] ? 1 : 0
                          }}
                          transition={{ duration: 0.3 }}
                          className="overflow-hidden"
                        >
                          <div className="flex flex-col gap-2 pt-3">
                            {caseItem.links.map((link) => (
                              <a
                                key={link.id}
                                href={link.link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-2 text-indigo-600 dark:text-indigo-400 text-sm no-underline py-2 px-3 bg-zinc-50 dark:bg-zinc-900 rounded-lg transition-all duration-200 border-l-2 border-indigo-600 hover:bg-zinc-100 dark:hover:bg-zinc-700"
                              >
                                <Icon name="link" size="xs" />
                                {formatLinkText(link.link)}
                              </a>
                            ))}
                          </div>
                        </motion.div>
                      </div>
                    )}
                  </motion.div>
                ))
              )}
            </div>

            {hasMoreCases && (
              <div className="text-center mt-10">
                <button
                  className="px-8 py-3 bg-indigo-600 dark:bg-indigo-700 text-white rounded-xl font-semibold hover:bg-indigo-700 dark:hover:bg-indigo-600 transition-all duration-200 hover:-translate-y-1 hover:shadow-depth-3"
                  onClick={handleShowMore}
                >
                  Show More Cases
                </button>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Final CTA */}
      <section className="py-24 px-5 bg-gradient-to-br from-indigo-600 via-indigo-700 to-indigo-800 dark:from-indigo-800 dark:via-indigo-900 dark:to-zinc-950 text-white text-center relative overflow-hidden">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-72 h-72 bg-indigo-400/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-400/10 rounded-full blur-3xl"></div>
        </div>

        <div className="max-w-5xl mx-auto relative z-10">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-4xl md:text-6xl mb-10 font-extrabold"
          >
            Don't Wait for the Crisis
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-xl md:text-2xl max-w-4xl mx-auto mb-12 leading-relaxed"
          >
            Your competitors aren't taking this risk. Your customers won't give you a second chance.
            And the internet won't send a warning before your domain expires.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="my-16"
          >
            <Link
              to="/register"
              className="group inline-flex items-center gap-3 px-12 py-5 rounded-xl text-lg font-bold transition-all duration-300 bg-white text-indigo-600 hover:-translate-y-1 hover:shadow-depth-5 shadow-depth-3"
            >
              Start Your Free Trial Today
              <Icon name="rocket" size="lg" className="group-hover:translate-x-1 transition-transform" />
            </Link>
            <p className="text-base mt-5 opacity-90">Full protection, zero setup required</p>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-2xl font-bold my-12 italic text-amber-300"
          >
            Because the most expensive mistake is the one you never saw coming.
          </motion.p>

          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-lg opacity-90"
          >
            Trusted by businesses who understand that the smallest details protect the biggest investments.
          </motion.p>
        </div>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  );
}

export default Home;
