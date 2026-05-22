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

export default function CountryDiplomacyChart({ data, topN = 20, minGames = 3 }: Props) {
  const chartData = [...data]
    .filter((c) => c.games_played >= minGames)
    .sort((a, b) => b.avg_wars_declared - a.avg_wars_declared)
    .slice(0, topN)
    .map((c) => ({
      name: c.nation_name,
      wars: parseFloat(c.avg_wars_declared.toFixed(1)),
      peace: parseFloat(c.avg_peace_treaties_signed.toFixed(1)),
      alliances: parseFloat(c.avg_alliances_formed.toFixed(1)),
      rows: parseFloat(c.avg_right_of_ways_signed.toFixed(1)),
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
            const { peace, alliances, rows, games } = props.payload;
            return [
              `${value} wars · ${peace} peace · ${alliances} alliances · ${rows} ROW · ${games} games`,
              'Avg wars declared',
            ];
          }}
        />
        <Bar dataKey="wars" radius={[0, 3, 3, 0]}>
          {chartData.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={entry.wars >= 5 ? '#e74c3c' : entry.wars >= 2 ? '#f5a623' : '#4a90e2'}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
