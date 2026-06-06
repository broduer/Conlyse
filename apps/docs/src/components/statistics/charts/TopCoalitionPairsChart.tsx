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
import type { GlobalAggregate } from '../types';

interface Props {
  data: GlobalAggregate;
  topN?: number;
}

export default function TopCoalitionPairsChart({ data, topN = 15 }: Props) {
  const pairs = data.top_coalition_pairs ?? [];
  if (pairs.length === 0) return <p style={{ color: 'var(--ifm-color-emphasis-500)', fontSize: 13 }}>No coalition pair data available yet.</p>;

  const chartData = pairs.slice(0, topN).map(([a, b, count]) => ({
    label: `${a} & ${b}`,
    count: count as number,
  }));

  return (
    <ResponsiveContainer width="100%" height={Math.max(260, chartData.length * 26)}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 8, right: 48, left: 4, bottom: 8 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-300)" horizontal={false} />
        <XAxis
          type="number"
          allowDecimals={false}
          tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
        />
        <YAxis
          type="category"
          dataKey="label"
          tick={{ fontSize: 10, fill: 'var(--ifm-font-color-base)' }}
          width={160}
        />
        <Tooltip
          contentStyle={{
            background: 'var(--ifm-background-surface-color)',
            border: '1px solid var(--ifm-color-emphasis-300)',
            borderRadius: 6,
            color: 'var(--ifm-font-color-base)',
          }}
          formatter={(value: number) => [value, 'Coalition wins together']}
        />
        <Bar dataKey="count" fill="#9b59b6" radius={[0, 3, 3, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
