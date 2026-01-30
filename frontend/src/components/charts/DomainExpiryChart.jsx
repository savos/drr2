import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useTheme } from '../../contexts/ThemeContext';

/**
 * Chart showing domain expiration trends over time
 * Displays expiring vs renewed domains by month
 */
export function DomainExpiryChart({ data }) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Custom tooltip for better UX
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-lg p-3 shadow-depth-2">
          <p className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: <span className="font-semibold">{entry.value}</span>
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 border border-zinc-200 dark:border-zinc-700 shadow-depth-1">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-4">Domain Expiration Timeline</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#3f3f46' : '#e5e7eb'} />
          <XAxis
            dataKey="month"
            stroke={isDark ? '#a1a1aa' : '#71717a'}
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke={isDark ? '#a1a1aa' : '#71717a'}
            style={{ fontSize: '12px' }}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: isDark ? '#27272a' : '#f4f4f5' }} />
          <Legend
            wrapperStyle={{ paddingTop: '20px', fontSize: '14px' }}
            iconType="square"
          />
          <Bar dataKey="expiring" fill="#f59e0b" name="Expiring Soon" radius={[4, 4, 0, 0]} />
          <Bar dataKey="renewed" fill="#10b981" name="Renewed" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
