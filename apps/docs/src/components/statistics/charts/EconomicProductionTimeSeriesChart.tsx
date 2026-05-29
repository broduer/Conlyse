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
  '#f5a623', '#4a90e2', '#50c878', '#e74c3c', '#9b59b6',
  '#1abc9c', '#e67e22', '#3498db', '#c0392b', '#2ecc71',
];

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

function formatRate(v: number): string {
  if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`;
  if (v >= 1e3) return `${(v / 1e3).toFixed(0)}k`;
  return String(Math.round(v));
}

export default function EconomicProductionTimeSeriesChart({ data, countries, topN = 10 }: Props) {
  const [mode, setMode] = useState<Mode>('pct');
  const [selectedType, setSelectedType] = useState<string>('MONEY');

  const allTypes = Array.from(
    new Set(
      data.countries.flatMap((c) =>
        Object.keys(c.production_pct_game ?? {})
      )
    )
  ).sort((a, b) => {
    if (a === 'MONEY') return -1;
    if (b === 'MONEY') return 1;
    return a.localeCompare(b);
  });

  const topCountryNames = [...countries]
    .sort((a, b) => b.win_rate - a.win_rate)
    .slice(0, topN)
    .map((c) => c.nation_name);

  const seriesData = data.countries.filter((c) => topCountryNames.includes(c.nation_name));

  const buckets = mode === 'pct'
    ? data.pct_buckets
    : Array.from({ length: data.max_game_days + 1 }, (_, i) => i);

  const chartData = buckets.map((b) => {
    const row: Record<string, number | string> = { bucket: b };
    for (const c of seriesData) {
      const series = mode === 'pct'
        ? (c.production_pct_game?.[selectedType] ?? [])
        : (c.production_game_days?.[selectedType] ?? []);
      const pt = series.find((p) => p.bucket === b);
      if (pt !== undefined) {
        row[c.nation_name] = pt.avg_production;
      }
    }
    return row;
  });

  const btnStyle = (active: boolean): React.CSSProperties => ({
    padding: '4px 14px',
    borderRadius: 4,
    border: '1px solid var(--ifm-color-emphasis-300)',
    background: active ? 'var(--ifm-color-primary)' : 'transparent',
    color: active ? '#fff' : 'var(--ifm-font-color-base)',
    cursor: 'pointer',
    fontSize: 12,
  });

  return (
    <div>
      <div style={{ marginBottom: 12, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: 4 }}>
          <button onClick={() => setMode('pct')} style={btnStyle(mode === 'pct')}>% of Game</button>
          <button onClick={() => setMode('days')} style={btnStyle(mode === 'days')}>Game Days</button>
        </div>
        {allTypes.length > 1 && (
          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
            {allTypes.map((rtype) => (
              <button
                key={rtype}
                onClick={() => setSelectedType(rtype)}
                style={btnStyle(selectedType === rtype)}
              >
                {RESOURCE_LABELS[rtype] ?? rtype}
              </button>
            ))}
          </div>
        )}
      </div>

      {chartData.every((row) => Object.keys(row).length <= 1) ? (
        <p style={{ color: 'var(--ifm-color-secondary)', fontSize: 13 }}>
          No production time-series data for {RESOURCE_LABELS[selectedType] ?? selectedType}.
        </p>
      ) : (
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
              tickFormatter={formatRate}
              tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
              label={{
                value: `${RESOURCE_LABELS[selectedType] ?? selectedType}/day`,
                angle: -90,
                position: 'insideLeft',
                offset: 12,
                style: { fontSize: 11, fill: 'var(--ifm-font-color-base)' },
              }}
              width={60}
            />
            <Tooltip
              contentStyle={{
                background: 'var(--ifm-background-surface-color)',
                border: '1px solid var(--ifm-color-emphasis-300)',
                borderRadius: 6,
                color: 'var(--ifm-font-color-base)',
              }}
              formatter={(value: number, name: string) => [
                `${formatRate(value)}/day`,
                name,
              ]}
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
      )}
    </div>
  );
}
