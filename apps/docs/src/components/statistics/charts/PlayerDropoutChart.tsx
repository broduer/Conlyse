import React from 'react';
import {
  Bar,
  BarChart,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

interface Props {
  dropout_rate: number;
  total_players: number;
}

export default function PlayerDropoutChart({ dropout_rate, total_players }: Props) {
  const active = parseFloat((total_players * (1 - dropout_rate)).toFixed(1));
  const dropped = parseFloat((total_players * dropout_rate).toFixed(1));

  const chartData = [
    {
      label: 'Typical game',
      active,
      dropped,
    },
  ];

  return (
    <ResponsiveContainer width="100%" height={140}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 24, right: 48, left: 16, bottom: 8 }}
        barSize={36}
      >
        <XAxis
          type="number"
          domain={[0, total_players]}
          tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
          tickFormatter={(v) => `${v}p`}
        />
        <YAxis
          type="category"
          dataKey="label"
          tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
          width={90}
        />
        <Tooltip
          contentStyle={{
            background: 'var(--ifm-background-surface-color)',
            border: '1px solid var(--ifm-color-emphasis-300)',
            borderRadius: 6,
            color: 'var(--ifm-font-color-base)',
          }}
          formatter={(value: number, name: string) => [
            `${value} players (${((value / total_players) * 100).toFixed(0)}%)`,
            name,
          ]}
        />
        <Bar dataKey="active" name="Active at end" stackId="a" fill="#50c878" radius={[0, 0, 0, 0]}>
          <LabelList
            dataKey="active"
            position="center"
            formatter={(v: number) => `${v}p active`}
            style={{ fontSize: 11, fill: '#fff', fontWeight: 600 }}
          />
        </Bar>
        <Bar dataKey="dropped" name="Dropped out" stackId="a" fill="#e74c3c" radius={[0, 3, 3, 0]}>
          <LabelList
            dataKey="dropped"
            position="center"
            formatter={(v: number) => `${v}p dropped (${((v / total_players) * 100).toFixed(0)}%)`}
            style={{ fontSize: 11, fill: '#fff', fontWeight: 600 }}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
