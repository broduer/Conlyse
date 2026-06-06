import React, { useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { BuildingAggregate, CountryAggregate } from '../types';

interface Props {
  countries: CountryAggregate[];
  buildings: BuildingAggregate[];
  topN?: number;
}

const COLORS = [
  '#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f',
  '#edc948', '#b07aa1', '#ff9da7', '#9c755f', '#bab0ac',
];

export default function CountryBuildingChart({ countries, buildings, topN = 20 }: Props) {
  const topBuildings = [...buildings]
    .sort((a, b) => b.avg_per_game - a.avg_per_game)
    .slice(0, 12)
    .map((b) => b.upgrade_identifier);

  const [selectedBuilding, setSelectedBuilding] = useState<string>(topBuildings[0] ?? '');

  const chartData = [...countries]
    .filter((c) => c.avg_final_building_counts && (c.avg_final_building_counts[selectedBuilding] ?? 0) > 0)
    .sort((a, b) => (b.avg_final_building_counts?.[selectedBuilding] ?? 0) - (a.avg_final_building_counts?.[selectedBuilding] ?? 0))
    .slice(0, topN)
    .map((c) => ({
      name: c.nation_name,
      avg: c.avg_final_building_counts?.[selectedBuilding] ?? 0,
      level: c.avg_final_building_levels?.[selectedBuilding] ?? 0,
    }));

  return (
    <div>
      <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
        <span style={{ fontSize: 13, color: 'var(--ifm-font-color-base)' }}>Building:</span>
        <select
          value={selectedBuilding}
          onChange={(e) => setSelectedBuilding(e.target.value)}
          style={{
            background: 'var(--ifm-background-surface-color)',
            border: '1px solid var(--ifm-color-emphasis-300)',
            color: 'var(--ifm-font-color-base)',
            borderRadius: 4,
            padding: '3px 8px',
            fontSize: 13,
          }}
        >
          {topBuildings.map((uid) => (
            <option key={uid} value={uid}>{uid}</option>
          ))}
        </select>
      </div>
      <ResponsiveContainer width="100%" height={420}>
        <BarChart data={chartData} layout="vertical" margin={{ top: 4, right: 64, left: 120, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-300)" horizontal={false} />
          <XAxis
            type="number"
            tick={{ fill: 'var(--ifm-font-color-base)', fontSize: 11 }}
            label={{ value: 'Avg count at game end', position: 'insideBottom', offset: -2, fill: 'var(--ifm-font-color-base)', fontSize: 11 }}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={115}
            tick={{ fill: 'var(--ifm-font-color-base)', fontSize: 11 }}
          />
          <Tooltip
            formatter={(value: number, _name: string, entry) => {
              const level = entry.payload.level;
              return [`${value.toFixed(2)} avg${level > 0 ? ` (lvl ${level.toFixed(1)})` : ''}`, 'Avg count'];
            }}
            contentStyle={{ background: 'var(--ifm-background-surface-color)', border: '1px solid var(--ifm-color-emphasis-300)', fontSize: 12 }}
          />
          <Bar dataKey="avg" radius={[0, 3, 3, 0]}>
            {chartData.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
            <LabelList dataKey="avg" position="right" formatter={(v: number) => v.toFixed(1)} style={{ fill: 'var(--ifm-font-color-base)', fontSize: 11 }} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
