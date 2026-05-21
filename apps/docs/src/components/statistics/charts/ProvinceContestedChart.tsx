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
import type { ProvinceAggregate } from '../types';

interface Props {
  data: ProvinceAggregate[];
  topN?: number;
}

export default function ProvinceContestedChart({ data, topN = 25 }: Props) {
  const chartData = [...data]
    .sort((a, b) => b.contest_frequency - a.contest_frequency)
    .slice(0, topN)
    .map((p) => ({
      name: p.province_name,
      contest_pct: parseFloat((p.contest_frequency * 100).toFixed(1)),
      avg_changes: parseFloat(p.avg_ownership_changes.toFixed(2)),
      games: p.games_appeared,
    }));

  return (
    <ResponsiveContainer width="100%" height={Math.max(300, chartData.length * 24)}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 8, right: 48, left: 110, bottom: 8 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-300)" horizontal={false} />
        <XAxis
          type="number"
          domain={[0, 100]}
          tickFormatter={(v) => `${v}%`}
          tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
        />
        <YAxis
          type="category"
          dataKey="name"
          tick={{ fontSize: 10, fill: 'var(--ifm-font-color-base)' }}
          width={105}
        />
        <Tooltip
          contentStyle={{
            background: 'var(--ifm-background-surface-color)',
            border: '1px solid var(--ifm-color-emphasis-300)',
            borderRadius: 6,
            color: 'var(--ifm-font-color-base)',
          }}
          formatter={(value: number, _: string, props) => [
            `${value}% of games (avg ${props.payload.avg_changes} changes)`,
            'Contest frequency',
          ]}
        />
        <Bar dataKey="contest_pct" radius={[0, 3, 3, 0]}>
          {chartData.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={entry.contest_pct >= 75 ? '#e74c3c' : entry.contest_pct >= 50 ? '#f5a623' : '#4a90e2'}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
