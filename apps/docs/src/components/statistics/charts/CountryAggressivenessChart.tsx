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
  minGames?: number;
}

export default function CountryAggressivenessChart({ data, topN = 20, minGames = 3 }: Props) {
  const chartData = [...data]
    .filter((c) => c.games_played >= minGames)
    .sort((a, b) => b.avg_provinces_captured - a.avg_provinces_captured)
    .slice(0, topN)
    .map((c) => ({
      name: c.nation_name,
      captured: parseFloat(c.avg_provinces_captured.toFixed(1)),
      lost: parseFloat(c.avg_provinces_lost.toFixed(1)),
      net: parseFloat((c.avg_provinces_captured - c.avg_provinces_lost).toFixed(1)),
      games: c.games_played,
    }));

  return (
    <ResponsiveContainer width="100%" height={Math.max(300, chartData.length * 26)}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 8, right: 48, left: 4, bottom: 8 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-300)" horizontal={false} />
        <XAxis
          type="number"
          tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
          allowDecimals={false}
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
          formatter={(value: number, _: string, props) => {
            const { lost, net, games } = props.payload;
            const sign = net >= 0 ? '+' : '';
            return [
              `${value} captured · ${lost} lost · net ${sign}${net} · ${games} games`,
              'Avg provinces captured',
            ];
          }}
        />
        <Bar dataKey="captured" radius={[0, 3, 3, 0]}>
          {chartData.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={entry.net >= 5 ? '#e74c3c' : entry.net >= 0 ? '#f5a623' : '#4a90e2'}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
