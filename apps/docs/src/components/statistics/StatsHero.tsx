import React from 'react';
import type { GlobalAggregate, MetaInfo } from './types';
import styles from './StatsHero.module.css';

interface Props {
  global: GlobalAggregate;
  meta: MetaInfo;
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.card}>
      <div className={styles.value}>{value}</div>
      <div className={styles.label}>{label}</div>
    </div>
  );
}

function formatDate(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
}

export default function StatsHero({ global: g, meta }: Props) {
  const topVictoryType = Object.entries(g.victory_type_distribution).sort(
    ([, a], [, b]) => b - a,
  )[0];
  const topTypeLabel = topVictoryType
    ? topVictoryType[0].charAt(0).toUpperCase() + topVictoryType[0].slice(1)
    : '—';

  return (
    <div className={styles.hero}>
      <div className={styles.heading}>
        <h1 className={styles.title}>Game Statistics</h1>
        <p className={styles.subtitle}>
          Aggregated from {g.total_games.toLocaleString()} recorded Conflict of Nations games
          {meta.date_range_start && (
            <>
              {' '}
              ({formatDate(meta.date_range_start)} – {formatDate(meta.date_range_end)})
            </>
          )}
        </p>
        <p className={styles.generated}>
          Last updated: {new Date(meta.generated_at).toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric',
          })}
        </p>
      </div>
      <div className={styles.cards}>
        <StatCard label="Games analyzed" value={g.total_games.toLocaleString()} />
        <StatCard label="Avg duration" value={`${g.avg_duration_hours.toFixed(0)}h`} />
        <StatCard label="Avg game days" value={g.avg_game_days.toFixed(0)} />
        <StatCard label="Avg players" value={g.avg_players_per_game.toFixed(1)} />
        <StatCard label="Avg dropout rate" value={`${(g.avg_dropout_rate * 100).toFixed(0)}%`} />
        <StatCard label="Most common win" value={topTypeLabel} />
      </div>
    </div>
  );
}
