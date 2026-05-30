import React, { useState } from 'react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { CountryAggregate, TimeSeriesOutput } from '../types';

interface Props {
  data: TimeSeriesOutput;
  countries: CountryAggregate[];
  topN?: number;
}

type Mode = 'pct' | 'days';

const COLORS = [
  '#4a90e2', '#50c878', '#f5a623', '#e74c3c', '#9b59b6',
  '#1abc9c', '#e67e22', '#3498db', '#c0392b', '#2ecc71',
];

export default function CountryVPTimeSeriesChart({ data, countries, topN = 10 }: Props) {
  const [mode, setMode] = useState<Mode>('pct');

  const topCountries = [...countries]
    .sort((a, b) => b.win_rate - a.win_rate)
    .slice(0, topN)
    .map((c) => c.nation_name);

  const seriesData = data.countries.filter((c) => topCountries.includes(c.nation_name));

  const buckets = mode === 'pct'
    ? data.pct_buckets
    : Array.from({ length: data.max_game_days + 1 }, (_, i) => i);

  const chartData = buckets.map((b) => {
    const row: Record<string, number | string> = { bucket: b };
    for (const c of seriesData) {
      const series = mode === 'pct' ? c.pct_game : c.game_days;
      const pt = series.find((p) => p.bucket === b);
      if (pt !== undefined) {
        row[c.nation_name] = pt.avg_vp;
      }
    }
    return row;
  });

  return (
    <div>
      <div style={{ marginBottom: 12, display: 'flex', gap: 8 }}>
        <button
          onClick={() => setMode('pct')}
          style={{
            padding: '4px 14px',
            borderRadius: 4,
            border: '1px solid var(--ifm-color-emphasis-300)',
            background: mode === 'pct' ? 'var(--ifm-color-primary)' : 'transparent',
            color: mode === 'pct' ? '#fff' : 'var(--ifm-font-color-base)',
            cursor: 'pointer',
            fontSize: 12,
          }}
        >
          % of Game
        </button>
        <button
          onClick={() => setMode('days')}
          style={{
            padding: '4px 14px',
            borderRadius: 4,
            border: '1px solid var(--ifm-color-emphasis-300)',
            background: mode === 'days' ? 'var(--ifm-color-primary)' : 'transparent',
            color: mode === 'days' ? '#fff' : 'var(--ifm-font-color-base)',
            cursor: 'pointer',
            fontSize: 12,
          }}
        >
          Game Days
        </button>
      </div>

      <ResponsiveContainer width="100%" height={420}>
        <LineChart data={chartData} margin={{ top: 8, right: 16, left: 4, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-300)" />
          <XAxis
            dataKey="bucket"
            tickFormatter={(v) => mode === 'pct' ? `${v}%` : `Day ${v}`}
            tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
            interval={mode === 'pct' ? 3 : Math.floor(data.max_game_days / 10)}
          />
          <YAxis
            tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
            label={{
              value: 'Avg Victory Points',
              angle: -90,
              position: 'insideLeft',
              offset: 12,
              style: { fontSize: 11, fill: 'var(--ifm-font-color-base)' },
            }}
          />
          <Tooltip
            contentStyle={{
              background: 'var(--ifm-background-surface-color)',
              border: '1px solid var(--ifm-color-emphasis-300)',
              borderRadius: 6,
              color: 'var(--ifm-font-color-base)',
            }}
            formatter={(value: number, name: string) => [`${value} avg VP`, name]}
            labelFormatter={(label) => mode === 'pct' ? `${label}% of game` : `Day ${label}`}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          {seriesData.map((c, i) => (
            <Line
              key={c.nation_name}
              type="monotone"
              dataKey={c.nation_name}
              stroke={COLORS[i % COLORS.length]}
              dot={false}
              strokeWidth={2}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
