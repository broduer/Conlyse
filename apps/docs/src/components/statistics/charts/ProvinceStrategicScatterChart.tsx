import React, { useMemo } from 'react';
import {
  CartesianGrid,
  Label,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  XAxis,
  YAxis,
} from 'recharts';
import type { ProvinceAggregate } from '../types';

interface Props {
  data: ProvinceAggregate[];
}

const TERRAIN_COLOURS: Record<string, string> = {
  PLAINS:   '#7bc67a',
  HILLS:    '#b8a05a',
  MOUNTAIN: '#8c9db5',
  FOREST:   '#3a8a4a',
  URBAN:    '#5b7ec9',
  JUNGLE:   '#2e7d52',
  TUNDRA:   '#8ecae6',
  DESERT:   '#e9c46a',
  SUBURBAN: '#9b72cf',
};

const QUADRANT_STYLE = {
  fontSize: 10,
  fill: 'var(--ifm-color-emphasis-400)',
  fontStyle: 'italic' as const,
};

interface ScatterPoint {
  name: string;
  terrain: string;
  contest: number;
  winCorr: number;
  fill: string;
}

const OUTLIER_N = 8;

function buildOutlierSet(points: ScatterPoint[]): Set<string> {
  const top = (sorted: ScatterPoint[]) => sorted.slice(0, OUTLIER_N).map((p) => p.name);
  return new Set([
    ...top([...points].sort((a, b) => b.contest - a.contest)),
    ...top([...points].sort((a, b) => b.winCorr - a.winCorr)),
    ...top([...points].sort((a, b) => (b.contest + b.winCorr) - (a.contest + a.winCorr))),
  ]);
}

function makeDotRenderer(outliers: Set<string>) {
  return function CustomDot(props: { cx?: number; cy?: number; payload?: ScatterPoint }) {
    const { cx = 0, cy = 0, payload } = props;
    if (!payload) return null;
    const isOutlier = outliers.has(payload.name);
    const lx = payload.contest > 55 ? cx - 6 : cx + 6;
    const ly = payload.winCorr > 55 ? cy + 11 : cy - 5;
    return (
      <g>
        <circle
          cx={cx}
          cy={cy}
          r={isOutlier ? 4 : 2}
          fill={payload.fill}
          fillOpacity={isOutlier ? 0.9 : 0.4}
        />
        {isOutlier && (
          <text
            x={lx}
            y={ly}
            fontSize={9}
            fill="var(--ifm-font-color-base)"
            textAnchor={payload.contest > 55 ? 'end' : 'start'}
          >
            {payload.name}
          </text>
        )}
      </g>
    );
  };
}

function TerrainLegend({ terrains }: { terrains: string[] }) {
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 14px', marginTop: 10, fontSize: 11, color: 'var(--ifm-font-color-base)' }}>
      {terrains.map((t) => (
        <span key={t} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: TERRAIN_COLOURS[t] ?? '#aaa', display: 'inline-block' }} />
          {t.charAt(0) + t.slice(1).toLowerCase()}
        </span>
      ))}
    </div>
  );
}

export default function ProvinceStrategicScatterChart({ data }: Props) {
  const points = useMemo<ScatterPoint[]>(
    () => data.map((p) => ({
      name: p.province_name,
      terrain: p.terrain_type,
      contest: p.contest_frequency * 100,
      winCorr: p.win_correlation * 100,
      fill: TERRAIN_COLOURS[p.terrain_type] ?? '#aaaaaa',
    })),
    [data],
  );

  const outlierSet = useMemo(() => buildOutlierSet(points), [points]);
  const terrains = useMemo(() => [...new Set(points.map((p) => p.terrain))].sort(), [points]);
  const CustomDot = useMemo(() => makeDotRenderer(outlierSet), [outlierSet]);

  return (
    <div>
      <ResponsiveContainer width="100%" height={480}>
        <ScatterChart margin={{ top: 24, right: 24, left: 8, bottom: 24 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--ifm-color-emphasis-200)" />
          <XAxis
            type="number"
            dataKey="contest"
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
            label={{ value: 'Contest frequency →', position: 'insideBottom', offset: -14, fontSize: 11, fill: 'var(--ifm-color-emphasis-500)' }}
          />
          <YAxis
            type="number"
            dataKey="winCorr"
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 11, fill: 'var(--ifm-font-color-base)' }}
            label={{ value: '← Win correlation', angle: -90, position: 'insideLeft', offset: 14, fontSize: 11, fill: 'var(--ifm-color-emphasis-500)' }}
          />
          <ReferenceLine x={50} stroke="var(--ifm-color-emphasis-300)" strokeDasharray="4 4">
            <Label value="Strategic Hotspots" position="insideTopRight" style={QUADRANT_STYLE} />
            <Label value="Battlegrounds" position="insideBottomRight" style={QUADRANT_STYLE} />
          </ReferenceLine>
          <ReferenceLine y={50} stroke="var(--ifm-color-emphasis-300)" strokeDasharray="4 4">
            <Label value="Key Objectives" position="insideTopLeft" style={QUADRANT_STYLE} />
            <Label value="Peripheral" position="insideBottomLeft" style={QUADRANT_STYLE} />
          </ReferenceLine>
          <Scatter data={points} shape={CustomDot} />
        </ScatterChart>
      </ResponsiveContainer>
      <TerrainLegend terrains={terrains} />
    </div>
  );
}
