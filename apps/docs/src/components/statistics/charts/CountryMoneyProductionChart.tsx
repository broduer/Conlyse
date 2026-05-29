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
import type { CountryAggregate } from '../types';

interface Props {
  data: CountryAggregate[];
  topN?: number;
}

function formatMoney(v: number): string {
  if (v >= 1e9) return `${(v / 1e9).toFixed(1)}B`;
  if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`;
  if (v >= 1e3) return `${(v / 1e3).toFixed(0)}k`;
  return String(Math.round(v));
}

export default function CountryMoneyProductionChart({ data, topN = 20 }: Props) {
  const chartData = [...data]
    .filter((c) => (c.avg_total_production?.['MONEY'] ?? 0) > 0)
    .sort((a, b) => (b.avg_total_production?.['MONEY'] ?? 0) - (a.avg_total_production?.['MONEY'] ?? 0))
    .slice(0, topN)
    .map((c) => ({
      name: c.nation_name,
      money: c.avg_total_production?.['MONEY'] ?? 0,
    }));

  if (chartData.length === 0) {
    return <p style={{ color: 'var(--ifm-color-secondary)', fontSize: 13 }}>No money production data available.</p>;
  }

  const maxVal = chartData[0]?.money ?? 0;

  return (
    <ResponsiveContainer width="100%" height={Math.max(300, chartData.length * 26)}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 8, right: 64, left: 4, bottom: 8 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-300)" horizontal={false} />
        <XAxis
          type="number"
          tickFormatter={formatMoney}
          tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
        />
        <YAxis
          type="category"
          dataKey="name"
          tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
          width={95}
        />
        <Tooltip
          contentStyle={{
            background: 'var(--ifm-background-surface-color)',
            border: '1px solid var(--ifm-color-emphasis-300)',
            borderRadius: 6,
            color: 'var(--ifm-font-color-base)',
          }}
          formatter={(value: number) => [formatMoney(value), 'Avg total money']}
        />
        <Bar dataKey="money" radius={[0, 3, 3, 0]}>
          {chartData.map((entry) => (
            <Cell
              key={entry.name}
              fill={entry.money >= maxVal * 0.75 ? '#f5a623' : entry.money >= maxVal * 0.5 ? '#e6c94f' : '#d4d17a'}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
