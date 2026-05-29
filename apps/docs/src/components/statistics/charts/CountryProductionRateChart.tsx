import React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
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

const RESOURCE_LABELS: Record<string, string> = {
  MONEY: 'Money',
  SUPPLY: 'Supply',
  MANPOWER: 'Manpower',
  FUEL: 'Fuel',
  ELECTRONIC: 'Electronics',
  RARE_MATERIAL: 'Rare Material',
  CONVENTIONAL_WARHEAD: 'Conv. Warhead',
  COMPONENT: 'Component',
  PHARMACEUTICAL: 'Pharma.',
};

const RESOURCE_COLORS: Record<string, string> = {
  MONEY: '#f5a623',
  SUPPLY: '#50c878',
  MANPOWER: '#4a90e2',
  FUEL: '#e74c3c',
  ELECTRONIC: '#9b59b6',
  RARE_MATERIAL: '#1abc9c',
  CONVENTIONAL_WARHEAD: '#e67e22',
  COMPONENT: '#95a5a6',
  PHARMACEUTICAL: '#16a085',
};

function formatRate(v: number): string {
  if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`;
  if (v >= 1e3) return `${(v / 1e3).toFixed(0)}k`;
  return String(Math.round(v));
}

export default function CountryProductionRateChart({ data, topN = 20 }: Props) {
  const allTypes = Array.from(
    new Set(data.flatMap((c) => Object.keys(c.avg_production_rate ?? {})))
  ).sort((a, b) => {
    if (a === 'MONEY') return -1;
    if (b === 'MONEY') return 1;
    return a.localeCompare(b);
  });

  if (allTypes.length === 0) {
    return <p style={{ color: 'var(--ifm-color-secondary)', fontSize: 13 }}>No production rate data available.</p>;
  }

  const chartData = [...data]
    .filter((c) => Object.keys(c.avg_production_rate ?? {}).length > 0)
    .sort((a, b) => {
      const totalA = Object.values(a.avg_production_rate ?? {}).reduce((s, v) => s + v, 0);
      const totalB = Object.values(b.avg_production_rate ?? {}).reduce((s, v) => s + v, 0);
      return totalB - totalA;
    })
    .slice(0, topN)
    .map((c) => {
      const row: Record<string, string | number> = { name: c.nation_name };
      for (const rtype of allTypes) {
        row[rtype] = c.avg_production_rate?.[rtype] ?? 0;
      }
      return row;
    });

  return (
    <ResponsiveContainer width="100%" height={Math.max(340, chartData.length * 26)}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 8, right: 16, left: 4, bottom: 8 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-300)" horizontal={false} />
        <XAxis
          type="number"
          tickFormatter={formatRate}
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
          formatter={(value: number, key: string) => [
            formatRate(value) + '/day',
            RESOURCE_LABELS[key] ?? key,
          ]}
        />
        <Legend
          wrapperStyle={{ fontSize: 11 }}
          formatter={(key) => RESOURCE_LABELS[key] ?? key}
        />
        {allTypes.map((rtype) => (
          <Bar
            key={rtype}
            dataKey={rtype}
            stackId="prod"
            fill={RESOURCE_COLORS[rtype] ?? '#aaa'}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
