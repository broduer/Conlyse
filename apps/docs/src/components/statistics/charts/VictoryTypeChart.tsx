import React from 'react';
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';

interface Props {
  data: Record<string, number>;
}

const COLORS = ['#4a90e2', '#50c878', '#f5a623', '#e74c3c'];

const LABELS: Record<string, string> = {
  solo: 'Solo Victory',
  coalition: 'Coalition Victory',
  unknown: 'Unknown',
};

export default function VictoryTypeChart({ data }: Props) {
  const chartData = Object.entries(data)
    .filter(([, v]) => v > 0)
    .map(([key, value]) => ({
      name: LABELS[key] ?? key,
      value,
    }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="45%"
          outerRadius={90}
          dataKey="value"
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          labelLine={false}
        >
          {chartData.map((_, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            background: 'var(--ifm-background-surface-color)',
            border: '1px solid var(--ifm-color-emphasis-300)',
            borderRadius: 6,
            color: 'var(--ifm-font-color-base)',
          }}
          formatter={(value: number) => [value, 'Games']}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: 'var(--ifm-font-color-base)' }} />
      </PieChart>
    </ResponsiveContainer>
  );
}
