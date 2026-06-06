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
import type { BuildingAggregate } from '../types';

interface Props {
  data: BuildingAggregate[];
  topN?: number;
}

export default function BuildingWinCorrelationChart({ data, topN = 15 }: Props) {
  // Sort by winner advantage (winner - loser delta), show top N
  const sorted = [...data]
    .filter((b) => b.avg_per_game >= 0.5)
    .sort((a, b) => (b.avg_per_winner - b.avg_per_loser) - (a.avg_per_winner - a.avg_per_loser))
    .slice(0, topN);

  const chartData = sorted.map((b) => ({
    name: b.upgrade_identifier,
    winner: b.avg_per_winner,
    loser: b.avg_per_loser,
    delta: +(b.avg_per_winner - b.avg_per_loser).toFixed(2),
  }));

  return (
    <ResponsiveContainer width="100%" height={420}>
      <BarChart data={chartData} layout="vertical" margin={{ top: 4, right: 32, left: 160, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-300)" horizontal={false} />
        <XAxis
          type="number"
          tick={{ fill: 'var(--ifm-font-color-base)', fontSize: 11 }}
          label={{ value: 'Avg count at game end', position: 'insideBottom', offset: -2, fill: 'var(--ifm-font-color-base)', fontSize: 11 }}
        />
        <YAxis
          type="category"
          dataKey="name"
          width={155}
          tick={{ fill: 'var(--ifm-font-color-base)', fontSize: 11 }}
        />
        <Tooltip
          formatter={(value: number, name: string) => [value.toFixed(2), name === 'winner' ? 'Winner avg' : 'Loser avg']}
          contentStyle={{ background: 'var(--ifm-background-surface-color)', border: '1px solid var(--ifm-color-emphasis-300)', fontSize: 12 }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} formatter={(v) => v === 'winner' ? 'Winner' : 'Loser'} />
        <Bar dataKey="winner" fill="#4caf80" radius={[0, 3, 3, 0]} />
        <Bar dataKey="loser"  fill="#e57373" radius={[0, 3, 3, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
