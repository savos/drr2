import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Footer from '../components/Footer';

function CheckIcon() {
  return (
    <svg className="w-5 h-5 text-indigo-500 dark:text-indigo-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  );
}

function PlanFeatures({ plan, billing }) {
  const price = billing === 'yearly' ? plan.yearly_price : plan.monthly_price;
  const monthlyEquiv = billing === 'yearly' ? (plan.yearly_price / 12).toFixed(2) : null;

  const features = [];

  // Domains
  if (plan.max_domains === null || plan.max_domains === undefined) {
    features.push(`${plan.min_domains}+ domains (open-ended)`);
  } else if (plan.min_domains === plan.max_domains) {
    features.push(`${plan.min_domains} domain${plan.min_domains !== 1 ? 's' : ''}`);
  } else {
    features.push(`${plan.min_domains}–${plan.max_domains} domains`);
  }

  // Users
  features.push(`Up to ${plan.max_users} user${plan.max_users !== 1 ? 's' : ''}`);

  // Overage
  if (plan.per_domain_overage_price) {
    features.push(`$${plan.per_domain_overage_price}/domain overage`);
  }

  // Standard features
  features.push('Domain uptime monitoring');
  features.push('SSL certificate tracking');
  features.push('Instant alerts');
  features.push('Email notifications');

  return { features, price, monthlyEquiv };
}

const PLAN_FEATURES = [
  'Email notifications',
  'Push notifications',
  'Slack, Discord & Telegram alerts',
  'n8n, Zapier & Make automation',
];

export default function Pricing() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [billing, setBilling] = useState('monthly');

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const response = await fetch('/api/pricing/');
        if (response.ok) {
          const data = await response.json();
          setPlans(data);
        }
      } catch (err) {
        console.error('Failed to fetch pricing plans:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchPlans();
  }, []);

  const POPULAR_PLAN = 'team';

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900">
      {/* Hero */}
      <section className="py-16 px-6 text-center">
        <div className="max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 text-sm font-medium px-4 py-2 rounded-full mb-6 border border-indigo-200 dark:border-indigo-800">
            First month completely free — cancel anytime
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold text-zinc-900 dark:text-zinc-50 mb-4">
            Simple, transparent pricing
          </h1>
          <p className="text-xl text-zinc-600 dark:text-zinc-400">
            Monitor all your domains and SSL certificates. No hidden fees.
            Your first month is free — billing starts after 30 days.
          </p>
        </div>
      </section>

      {/* First month free banner */}
      <section className="px-6 pb-4">
        <div className="max-w-6xl mx-auto">
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950 dark:to-purple-950 border border-indigo-200 dark:border-indigo-800 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center shrink-0">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
              </svg>
            </div>
            <div>
              <p className="font-semibold text-zinc-900 dark:text-zinc-100">
                First month free on all plans
              </p>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Start your subscription today — we won't charge you anything for the first 30 days.
                Cancel at any time, no questions asked. Charging begins automatically after your free month.
              </p>
            </div>
          </div>

          {/* Billing toggle */}
          <div className="flex justify-center mt-6">
            <div className="inline-flex items-center gap-1 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-xl p-1 shadow-sm">
              <button
                onClick={() => setBilling('monthly')}
                className={`px-5 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                  billing === 'monthly'
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBilling('yearly')}
                className={`px-5 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 flex items-center gap-2 ${
                  billing === 'yearly'
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100'
                }`}
              >
                Yearly
                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                  billing === 'yearly'
                    ? 'bg-white/20 text-white'
                    : 'bg-emerald-100 dark:bg-emerald-900 text-emerald-700 dark:text-emerald-300'
                }`}>
                  Save ~17%
                </span>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Plan cards */}
      <section className="px-6 py-10">
        <div className="max-w-6xl mx-auto">
          {loading ? (
            <div className="text-center py-20 text-zinc-500 dark:text-zinc-400">Loading plans...</div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {plans.map((plan) => {
                const isPopular = plan.name.toLowerCase() === POPULAR_PLAN;
                const isAgency = plan.max_domains === null;

                return (
                  <div
                    key={plan.id}
                    className={`relative flex flex-col rounded-2xl border transition-all duration-200 ${
                      isPopular
                        ? 'border-indigo-500 dark:border-indigo-400 shadow-lg shadow-indigo-100 dark:shadow-indigo-950 scale-[1.02]'
                        : 'border-zinc-200 dark:border-zinc-700 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md'
                    } bg-white dark:bg-zinc-800`}
                  >
                    {isPopular && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                        <span className="bg-indigo-600 text-white text-xs font-bold px-4 py-1.5 rounded-full whitespace-nowrap">
                          Most Popular
                        </span>
                      </div>
                    )}

                    <div className="p-6 flex flex-col flex-1">
                      {/* Plan name */}
                      <div className="mb-4">
                        <h3 className="text-lg font-bold text-zinc-900 dark:text-zinc-100 capitalize mb-1">
                          {plan.name}
                          {isAgency && (
                            <span className="ml-2 text-xs font-medium bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 px-2 py-0.5 rounded-full">
                              Unlimited
                            </span>
                          )}
                        </h3>
                        <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed">
                          {plan.plan_description}
                        </p>
                      </div>

                      {/* Price */}
                      <div className="mb-5">
                        <div className="flex items-baseline gap-2 flex-wrap">
                          <span className={`text-3xl font-extrabold ${billing === 'monthly' ? 'text-zinc-900 dark:text-zinc-50' : 'text-zinc-400 dark:text-zinc-500'}`}>
                            ${plan.monthly_price}<span className="text-base font-semibold">/mo</span>
                          </span>
                          <span className="text-zinc-400 dark:text-zinc-500 text-sm">or</span>
                          <span className={`text-3xl font-extrabold ${billing === 'yearly' ? 'text-zinc-900 dark:text-zinc-50' : 'text-zinc-400 dark:text-zinc-500'}`}>
                            ${plan.yearly_price}<span className="text-base font-semibold">/yr</span>
                          </span>
                        </div>
                        {billing === 'yearly' && (
                          <p className="text-xs text-emerald-600 dark:text-emerald-400 font-medium mt-1">
                            ~${(plan.yearly_price / 12).toFixed(2)}/month
                          </p>
                        )}
                        {isAgency && plan.per_domain_overage_price && (
                          <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                            + ${plan.per_domain_overage_price}/domain over {plan.min_domains}
                          </p>
                        )}
                      </div>

                      {/* Domain/users info */}
                      <div className="flex gap-3 mb-5">
                        <div className="flex-1 bg-zinc-50 dark:bg-zinc-700/50 rounded-lg px-3 py-2 text-center">
                          <div className="text-xs text-zinc-500 dark:text-zinc-400 mb-0.5">Domains</div>
                          <div className="text-sm font-semibold text-zinc-800 dark:text-zinc-200">
                            {isAgency
                              ? `${plan.min_domains}+`
                              : plan.min_domains === plan.max_domains
                                ? plan.min_domains
                                : `${plan.min_domains}–${plan.max_domains}`}
                          </div>
                        </div>
                        <div className="flex-1 bg-zinc-50 dark:bg-zinc-700/50 rounded-lg px-3 py-2 text-center">
                          <div className="text-xs text-zinc-500 dark:text-zinc-400 mb-0.5">Users</div>
                          <div className="text-sm font-semibold text-zinc-800 dark:text-zinc-200">
                            {plan.max_users}
                          </div>
                        </div>
                      </div>

                      {/* Features list */}
                      <ul className="space-y-2.5 mb-6 flex-1">
                        {PLAN_FEATURES.map((feature, idx) => (
                          <li key={idx} className="flex items-start gap-2.5 text-sm text-zinc-700 dark:text-zinc-300">
                            <CheckIcon />
                            {feature}
                          </li>
                        ))}
                      </ul>

                      {/* CTA */}
                      <Link
                        to="/register"
                        className={`w-full text-center py-3 px-4 rounded-xl font-semibold text-sm transition-all duration-200 no-underline ${
                          isPopular
                            ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm hover:shadow-md'
                            : 'bg-zinc-100 dark:bg-zinc-700 hover:bg-indigo-600 dark:hover:bg-indigo-600 text-zinc-800 dark:text-zinc-200 hover:text-white dark:hover:text-white'
                        }`}
                      >
                        Start free month
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </section>

      {/* FAQ / reassurance section */}
      <section className="px-6 py-12">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 text-center mb-8">
            Common questions
          </h2>
          <div className="space-y-4">
            {[
              {
                q: 'When does billing start?',
                a: 'Your first month is completely free. After 30 days, your chosen plan is billed automatically. You can cancel before the trial ends and you will never be charged.',
              },
              {
                q: 'Can I cancel at any time?',
                a: 'Yes. You can cancel your subscription at any time from your account settings. No cancellation fees, no lock-in.',
              },
              {
                q: 'What happens if I exceed my domain limit?',
                a: 'For fixed-tier plans, you can upgrade to a higher plan. The Agency plan is open-ended — you pay a small per-domain fee for every domain above the base of 50.',
              },
              {
                q: 'Can I switch plans later?',
                a: 'Absolutely. You can upgrade or downgrade your plan at any time. Upgrades are prorated immediately; downgrades take effect at the next billing cycle.',
              },
              {
                q: 'Do you offer yearly billing?',
                a: 'Yes — paying yearly saves you approximately 17% compared to the monthly rate.',
              },
            ].map(({ q, a }, idx) => (
              <div key={idx} className="bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-xl p-6">
                <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100 mb-2">{q}</h3>
                <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed m-0">{a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
