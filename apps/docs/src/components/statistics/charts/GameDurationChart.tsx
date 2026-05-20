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
import type { DurationBucket } from '../types';

interface Props {
  data: DurationBucket[];
}

export default function GameDurationChart({ data }: Props) {
  const chartData = data.map((b) => ({
    label: `${b.min_hours.toFixed(0)}–${b.max_hours.toFixed(0)}h`,
    count: b.count,
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 32 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-300)" />
        <XAxis
          dataKey="label"
          tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
          angle={-35}
          textAnchor="end"
          interval={0}
        />
        <YAxis tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }} allowDecimals={false} />
        <Tooltip
          contentStyle={{
            background: 'var(--ifm-background-surface-color)',
            border: '1px solid var(--ifm-color-emphasis-300)',
            borderRadius: 6,
            color: 'var(--ifm-font-color-base)',
          }}
          formatter={(value: number) => [value, 'Games']}
        />
        <Bar dataKey="count" fill="var(--ifm-color-primary)" radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
