import React, { useMemo } from 'react';
import type { BuildingAggregate } from '../types';

interface Props {
  data: BuildingAggregate[];
}

const TIERS = [1, 2, 3, 4, 5];

function cellColor(value: number, maxValue: number): string {
  if (value <= 0 || maxValue <= 0) return 'transparent';
  const intensity = Math.pow(value / maxValue, 0.5);
  const lightness = Math.round(65 - intensity * 40);
  return `hsl(210, 70%, ${lightness}%)`;
}

function cellTextColor(value: number, maxValue: number): string {
  if (value <= 0 || maxValue <= 0) return 'var(--ifm-color-emphasis-400)';
  const intensity = Math.pow(value / maxValue, 0.5);
  return intensity > 0.55 ? '#fff' : 'var(--ifm-font-color-base)';
}

export default function BuildingFrequencyChart({ data }: Props) {
  const sorted = useMemo(
    () => [...data].sort((a, b) => b.avg_per_game - a.avg_per_game),
    [data],
  );

  const maxValue = useMemo(() => {
    let m = 0;
    for (const b of sorted) {
      for (const t of TIERS) {
        const v = b.avg_per_tier[String(t)] ?? 0;
        if (v > m) m = v;
      }
    }
    return m;
  }, [sorted]);

  const colWidth = 80;
  const labelWidth = 160;
  const rowHeight = 36;
  const headerHeight = 32;

  return (
    <div style={{ overflowX: 'auto' }}>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `${labelWidth}px ${TIERS.map(() => `${colWidth}px`).join(' ')}`,
          minWidth: labelWidth + TIERS.length * colWidth,
        }}
      >
        {/* Header row */}
        <div style={{ height: headerHeight, display: 'flex', alignItems: 'flex-end', paddingBottom: 6 }}>
          <span style={{ fontSize: 11, color: 'var(--ifm-color-emphasis-600)', fontWeight: 600 }}>Building</span>
        </div>
        {TIERS.map((t) => (
          <div
            key={t}
            style={{
              height: headerHeight,
              display: 'flex',
              alignItems: 'flex-end',
              justifyContent: 'center',
              paddingBottom: 6,
              fontSize: 11,
              fontWeight: 600,
              color: 'var(--ifm-color-emphasis-600)',
            }}
          >
            Tier {t}
          </div>
        ))}

        {/* Data rows */}
        {sorted.map((b) => (
          <React.Fragment key={b.upgrade_identifier}>
            <div
              style={{
                height: rowHeight,
                display: 'flex',
                alignItems: 'center',
                paddingRight: 12,
                fontSize: 12,
                color: 'var(--ifm-font-color-base)',
                borderTop: '1px solid var(--ifm-color-emphasis-200)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
              title={b.upgrade_identifier}
            >
              {b.upgrade_identifier}
            </div>
            {TIERS.map((t) => {
              const v = b.avg_per_tier[String(t)] ?? 0;
              return (
                <div
                  key={t}
                  title={`${b.upgrade_identifier} tier ${t}: ${v > 0 ? v.toFixed(2) : '—'} avg/game`}
                  style={{
                    height: rowHeight,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 11,
                    fontWeight: v > 0 ? 500 : 400,
                    background: cellColor(v, maxValue),
                    color: cellTextColor(v, maxValue),
                    borderTop: '1px solid var(--ifm-color-emphasis-200)',
                    borderLeft: '1px solid var(--ifm-color-emphasis-200)',
                    cursor: 'default',
                  }}
                >
                  {v > 0 ? v.toFixed(1) : ''}
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>

      {/* Legend */}
      <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: 11, color: 'var(--ifm-color-emphasis-600)' }}>Low</span>
        <div
          style={{
            width: 160,
            height: 10,
            borderRadius: 3,
            background: 'linear-gradient(to right, hsl(210,70%,65%), hsl(210,70%,25%))',
          }}
        />
        <span style={{ fontSize: 11, color: 'var(--ifm-color-emphasis-600)' }}>High · values = avg count at game end</span>
      </div>
    </div>
  );
}
