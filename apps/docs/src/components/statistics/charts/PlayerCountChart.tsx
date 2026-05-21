import React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

interface Props {
  data: Record<string, number>;
}

export default function PlayerCountChart({ data }: Props) {
  const chartData = Object.entries(data)
    .map(([players, count]) => ({ players: `${players}p`, count }))
    .sort((a, b) => parseInt(a.players) - parseInt(b.players));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-300)" />
        <XAxis dataKey="players" tick={{ fontSize: 12, fill: 'var(--ifm-font-color-base)' }} />
        <YAxis tick={{ fontSize: 12, fill: 'var(--ifm-font-color-base)' }} allowDecimals={false} />
        <Tooltip
          contentStyle={{
            background: 'var(--ifm-background-surface-color)',
            border: '1px solid var(--ifm-color-emphasis-300)',
            borderRadius: 6,
            color: 'var(--ifm-font-color-base)',
          }}
          formatter={(value: number) => [value, 'Games']}
        />
        <Bar dataKey="count" fill="#50c878" radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
