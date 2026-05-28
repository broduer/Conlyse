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

export default function CountryTerritoryChart({ data, topN = 20 }: Props) {
  const chartData = data
    .sort((a, b) => b.avg_final_provinces - a.avg_final_provinces)
    .slice(0, topN)
    .map((c) => ({
      name: c.nation_name,
      avg_final: parseFloat(c.avg_final_provinces.toFixed(1)),
      avg_initial: parseFloat(c.avg_initial_provinces.toFixed(1)),
    }));

  return (
    <ResponsiveContainer width="100%" height={Math.max(300, chartData.length * 26)}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 8, right: 32, left: 4, bottom: 8 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-300)" horizontal={false} />
        <XAxis
          type="number"
          tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
          label={{ value: 'Provinces', position: 'insideBottomRight', offset: -8, fontSize: 11 }}
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
          formatter={(value: number, name: string) => [
            value,
            name === 'avg_final' ? 'Avg final provinces' : 'Avg starting provinces',
          ]}
        />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Bar dataKey="avg_initial" name="Starting Provinces" fill="var(--ifm-color-emphasis-400)" radius={[0, 3, 3, 0]} />
        <Bar dataKey="avg_final" name="Final Provinces" fill="var(--ifm-color-primary)" radius={[0, 3, 3, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
