import React from 'react';
import type { CountryAggregate, GlobalAggregate, MetaInfo } from './types';
import styles from './StatsHero.module.css';

interface Props {
  global: GlobalAggregate;
  meta: MetaInfo;
  countries: CountryAggregate[];
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.card}>
      <div className={styles.value}>{value}</div>
      <div className={styles.label}>{label}</div>
    </div>
  );
}

function formatInterval(seconds: number): string {
  if (seconds <= 0) return '—';
  if (seconds >= 3600) return `${(seconds / 3600).toFixed(1)}h`;
  if (seconds >= 60) return `${Math.round(seconds / 60)}min`;
  return `${Math.round(seconds)}s`;
}

function formatDate(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
}

export default function StatsHero({ global: g, meta, countries }: Props) {
  const topVictoryType = Object.entries(g.victory_type_distribution).sort(
    ([, a], [, b]) => b - a,
  )[0];
  const topTypeLabel = topVictoryType
    ? topVictoryType[0].charAt(0).toUpperCase() + topVictoryType[0].slice(1)
    : '—';

  const topCountry = [...countries].sort((a, b) => b.win_rate - a.win_rate)[0];

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
        <StatCard label="Avg game days" value={g.avg_game_days.toFixed(0)} />
        <StatCard label="Top win rate" value={topCountry ? topCountry.nation_name : '—'} />
        <StatCard label="Avg dropout rate" value={`${(g.avg_dropout_rate * 100).toFixed(0)}%`} />
        <StatCard label="Avg update interval" value={formatInterval(g.avg_update_interval_seconds)} />
        <StatCard label="Most common win" value={topTypeLabel} />
      </div>
    </div>
  );
}
