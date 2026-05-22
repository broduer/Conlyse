import React from 'react';
import {
  Legend,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import type { CountryAggregate } from '../types';

interface Props {
  data: CountryAggregate[];
  topN?: number;
}

const COLORS = [
  '#4a90e2', '#50c878', '#f5a623', '#e74c3c', '#9b59b6', '#1abc9c',
];

const DIMENSIONS = [
  { key: 'win_rate',              label: 'Win Rate',      raw: (c: CountryAggregate) => c.win_rate },
  { key: 'avg_expansion',        label: 'Expansion',     raw: (c: CountryAggregate) => c.avg_expansion },
  { key: 'avg_prov_captured',    label: 'Aggression',    raw: (c: CountryAggregate) => c.avg_provinces_captured },
  { key: 'survival',             label: 'Survival',      raw: (c: CountryAggregate) => 1 - c.elimination_rate },
  { key: 'avg_final_provinces',  label: 'Territory',     raw: (c: CountryAggregate) => c.avg_final_provinces },
];

function normalize(values: number[]): number[] {
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (max === min) return values.map(() => 50);
  return values.map((v) => parseFloat(((v - min) / (max - min) * 100).toFixed(1)));
}

interface TooltipPayload {
  name: string;
  value: number;
  payload: Record<string, number | string>;
}

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: TooltipPayload[]; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'var(--ifm-background-surface-color)',
      border: '1px solid var(--ifm-color-emphasis-300)',
      borderRadius: 6,
      padding: '8px 12px',
      fontSize: 12,
      color: 'var(--ifm-font-color-base)',
      lineHeight: 1.6,
    }}>
      <div style={{ fontWeight: 600, marginBottom: 4 }}>{label}</div>
      {payload.map((p) => (
        <div key={p.name} style={{ color: 'var(--ifm-font-color-base)' }}>
          {p.name}: <strong>{p.value.toFixed(1)}</strong> (normalized)
        </div>
      ))}
    </div>
  );
}

export default function CountryRadarChart({ data, topN = 6 }: Props) {
  const top = [...data].sort((a, b) => b.games_played - a.games_played).slice(0, topN);

  const rawByDim = DIMENSIONS.map((dim) => top.map((c) => dim.raw(c)));
  const normalizedByDim = rawByDim.map(normalize);

  const chartData = DIMENSIONS.map((dim, di) => {
    const row: Record<string, number | string> = { dimension: dim.label };
    top.forEach((c, ci) => {
      row[c.nation_name] = normalizedByDim[di][ci];
    });
    return row;
  });

  return (
    <ResponsiveContainer width="100%" height={380}>
      <RadarChart data={chartData} margin={{ top: 16, right: 32, left: 32, bottom: 16 }}>
        <PolarGrid stroke="var(--ifm-color-emphasis-300)" />
        <PolarAngleAxis
          dataKey="dimension"
          tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
        />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 100]}
          tick={{ fontSize: 9, fill: 'var(--ifm-color-emphasis-400)' }}
          tickCount={4}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        {top.map((c, i) => (
          <Radar
            key={c.nation_name}
            name={c.nation_name}
            dataKey={c.nation_name}
            stroke={COLORS[i % COLORS.length]}
            fill={COLORS[i % COLORS.length]}
            fillOpacity={0.12}
            strokeWidth={2}
          />
        ))}
      </RadarChart>
    </ResponsiveContainer>
  );
}
