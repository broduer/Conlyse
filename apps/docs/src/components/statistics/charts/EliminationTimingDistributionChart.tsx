import React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { GlobalAggregate } from '../types';

interface Props {
  data: GlobalAggregate;
}

const LABELS: Record<string, string> = {
  '0': '0–10%', '10': '10–20%', '20': '20–30%', '30': '30–40%', '40': '40–50%',
  '50': '50–60%', '60': '60–70%', '70': '70–80%', '80': '80–90%', '90': '90–100%',
};

export default function EliminationTimingDistributionChart({ data }: Props) {
  const dist = data.elimination_timing_distribution ?? {};
  if (Object.keys(dist).length === 0) return <p style={{ color: 'var(--ifm-color-emphasis-500)', fontSize: 13 }}>No elimination timing data available yet.</p>;

  const chartData = ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90']
    .map((b) => ({ label: LABELS[b], bucket: parseInt(b), count: dist[b] ?? 0 }))
    .filter((d) => d.count > 0);

  const max = Math.max(...chartData.map((d) => d.count));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={chartData} margin={{ top: 8, right: 16, left: 4, bottom: 24 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-300)" vertical={false} />
        <XAxis
          dataKey="label"
          tick={{ fontSize: 10, fill: 'var(--ifm-font-color-base)' }}
          angle={-30}
          textAnchor="end"
          interval={0}
        />
        <YAxis tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }} />
        <Tooltip
          contentStyle={{
            background: 'var(--ifm-background-surface-color)',
            border: '1px solid var(--ifm-color-emphasis-300)',
            borderRadius: 6,
            color: 'var(--ifm-font-color-base)',
          }}
          formatter={(value: number) => [value, 'Eliminations']}
        />
        <Bar dataKey="count" radius={[3, 3, 0, 0]}>
          {chartData.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={entry.count === max ? '#e74c3c' : '#4a90e2'}
              fillOpacity={0.85 + (entry.count / max) * 0.15}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
