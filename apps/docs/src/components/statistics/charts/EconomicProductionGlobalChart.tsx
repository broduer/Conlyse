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

interface Props {
  data: Record<string, number>;
}

const RESOURCE_LABELS: Record<string, string> = {
  MONEY: 'Money',
  SUPPLY: 'Supply',
  MANPOWER: 'Manpower',
  FUEL: 'Fuel',
  ELECTRONIC: 'Electronics',
  RARE_MATERIAL: 'Rare Material',
  CONVENTIONAL_WARHEAD: 'Conv. Warhead',
  CHEMICAL_WARHEAD: 'Chem. Warhead',
  NUCLEAR_WARHEAD: 'Nuc. Warhead',
  DEPLOYABLE_GEAR: 'Deploy. Gear',
  COMPONENT: 'Component',
  PHARMACEUTICAL: 'Pharma.',
  GROUND_MUNITION: 'Gnd. Munition',
  SEA_MUNITION: 'Sea Munition',
  AIR_GROUND_MUNITION: 'Air Munition',
};

const RESOURCE_COLORS: Record<string, string> = {
  MONEY: '#f5a623',
  SUPPLY: '#50c878',
  MANPOWER: '#4a90e2',
  FUEL: '#e74c3c',
  ELECTRONIC: '#9b59b6',
  RARE_MATERIAL: '#1abc9c',
  CONVENTIONAL_WARHEAD: '#e67e22',
  CHEMICAL_WARHEAD: '#c0392b',
  NUCLEAR_WARHEAD: '#2c3e50',
  DEPLOYABLE_GEAR: '#3498db',
  COMPONENT: '#95a5a6',
  PHARMACEUTICAL: '#16a085',
};

function formatProduction(v: number): string {
  if (v >= 1e9) return `${(v / 1e9).toFixed(1)}B`;
  if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`;
  if (v >= 1e3) return `${(v / 1e3).toFixed(0)}k`;
  return String(Math.round(v));
}

export default function EconomicProductionGlobalChart({ data }: Props) {
  const chartData = Object.entries(data)
    .sort(([a], [b]) => {
      if (a === 'MONEY') return -1;
      if (b === 'MONEY') return 1;
      return a.localeCompare(b);
    })
    .map(([rtype, value]) => ({
      rtype,
      label: RESOURCE_LABELS[rtype] ?? rtype,
      value,
    }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 8, right: 32, left: 8, bottom: 32 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-300)" vertical={false} />
        <XAxis
          dataKey="label"
          tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
          angle={-35}
          textAnchor="end"
          interval={0}
        />
        <YAxis
          tickFormatter={formatProduction}
          tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
          width={52}
        />
        <Tooltip
          contentStyle={{
            background: 'var(--ifm-background-surface-color)',
            border: '1px solid var(--ifm-color-emphasis-300)',
            borderRadius: 6,
            color: 'var(--ifm-font-color-base)',
          }}
          formatter={(value: number, _: string, { payload }: { payload: { label: string } }) => [
            formatProduction(value),
            payload.label,
          ]}
        />
        <Bar dataKey="value" radius={[3, 3, 0, 0]}>
          {chartData.map((entry) => (
            <Cell
              key={entry.rtype}
              fill={RESOURCE_COLORS[entry.rtype] ?? 'var(--ifm-color-primary)'}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
