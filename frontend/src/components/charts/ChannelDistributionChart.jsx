import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { useTheme } from '../../contexts/ThemeContext';

/**
 * Pie chart showing distribution of integrations by channel type
 */
export function ChannelDistributionChart({ data }) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Color palette for different channels
  const COLORS = {
    Teams: '#6264A7',
    Slack: '#E01E5A',
    Discord: '#5865F2',
    Telegram: '#0088CC',
    Email: '#10b981',
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-lg p-3 shadow-depth-2">
          <p className="font-semibold text-zinc-900 dark:text-zinc-100 mb-1">{data.name}</p>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Count: <span className="font-semibold">{data.value}</span>
          </p>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Percentage: <span className="font-semibold">{data.payload.percentage}%</span>
          </p>
        </div>
      );
    }
    return null;
  };

  // Custom label renderer
  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return percent > 0.05 ? (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        className="text-xs font-semibold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    ) : null;
  };

  return (
    <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 border border-zinc-200 dark:border-zinc-700 shadow-depth-1">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-4">Channel Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomLabel}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#6366f1'} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '14px' }}
            iconType="circle"
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
