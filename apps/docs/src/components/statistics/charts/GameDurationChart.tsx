import React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Label,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { DurationBucket } from '../types';

interface Props {
  data: DurationBucket[];
  mean_days?: number;
  median_days?: number;
}

export default function GameDurationChart({ data, mean_days, median_days }: Props) {
  const chartData = data.map((b) => ({
    mid: parseFloat(((b.min_days + b.max_days) / 2).toFixed(1)),
    label: `${b.min_days.toFixed(0)}–${b.max_days.toFixed(0)}d`,
    count: b.count,
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 16, right: 16, left: 0, bottom: 32 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-300)" />
        <XAxis
          dataKey="mid"
          type="number"
          domain={['dataMin - 5', 'dataMax + 5']}
          tickFormatter={(v) => `${v}d`}
          tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
          interval={1}
        />
        <YAxis tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }} allowDecimals={false} />
        <Tooltip
          contentStyle={{
            background: 'var(--ifm-background-surface-color)',
            border: '1px solid var(--ifm-color-emphasis-300)',
            borderRadius: 6,
            color: 'var(--ifm-font-color-base)',
          }}
          labelFormatter={(mid) => {
            const bucket = chartData.find((b) => b.mid === mid);
            return bucket ? bucket.label : `${mid}d`;
          }}
          formatter={(value: number) => [value, 'Games']}
        />
        <Bar dataKey="count" fill="var(--ifm-color-primary)" radius={[3, 3, 0, 0]} />
        {median_days !== undefined && (
          <ReferenceLine x={median_days} stroke="var(--ifm-color-emphasis-600)" strokeDasharray="4 4" strokeWidth={1.5}>
            <Label value={`Median ${median_days.toFixed(0)}d`} position="top" fontSize={10} fill="var(--ifm-color-emphasis-600)" />
          </ReferenceLine>
        )}
        {mean_days !== undefined && (
          <ReferenceLine x={mean_days} stroke="var(--ifm-color-primary)" strokeDasharray="4 4" strokeWidth={1.5}>
            <Label value={`Mean ${mean_days.toFixed(0)}d`} position="top" fontSize={10} fill="var(--ifm-color-primary)" />
          </ReferenceLine>
        )}
      </BarChart>
    </ResponsiveContainer>
  );
}
