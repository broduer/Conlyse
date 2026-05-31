import Link from '@docusaurus/Link';
import React, { useEffect, useRef, useState } from 'react';
import type { GlobalAggregate } from '../statistics/types';
import styles from './styles.module.css';

const STATS_BASE_URL = process.env.NODE_ENV === 'development'
  ? '/data/stats'
  : 'https://r2.conlyse.zdox.dev/stats';

function useCountUp(target: number, decimals: number, active: boolean): string {
  const [display, setDisplay] = useState('0');
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    if (!active || target === 0) {
      setDisplay(target.toFixed(decimals));
      return;
    }
    const duration = 800;
    const start = performance.now();
    function tick(now: number) {
      const elapsed = Math.min(now - start, duration);
      const progress = elapsed / duration;
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = target * eased;
      setDisplay(current.toFixed(decimals));
      if (elapsed < duration) {
        rafRef.current = requestAnimationFrame(tick);
      } else {
        setDisplay(target.toFixed(decimals));
      }
    }
    rafRef.current = requestAnimationFrame(tick);
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
  }, [target, decimals, active]);

  return display;
}

interface StatItemProps {
  label: string;
  value: number;
  suffix: string;
  decimals: number;
  active: boolean;
}

function StatItem({ label, value, suffix, decimals, active }: StatItemProps) {
  const display = useCountUp(value, decimals, active);
  return (
    <div className={styles.stat}>
      <span className={styles.value}>{display}{suffix}</span>
      <span className={styles.label}>{label}</span>
    </div>
  );
}

export default function StatsTeaserStrip() {
  const [data, setData] = useState<GlobalAggregate | null>(null);

  useEffect(() => {
    fetch(`${STATS_BASE_URL}/global.json`)
      .then((r) => r.json())
      .then((json) => setData(json as GlobalAggregate))
      .catch(() => {});
  }, []);

  if (!data) return null;

  const soloWinRate = data.total_games > 0
    ? ((data.victory_type_distribution['solo'] ?? 0) / data.total_games) * 100
    : 0;

  const stats: StatItemProps[] = [
    { label: 'Games Analyzed',   value: data.total_games,                       suffix: '',  decimals: 0, active: true },
    { label: 'Avg Game Length',  value: data.avg_game_days,                     suffix: 'd', decimals: 0, active: true },
    { label: 'Avg Dropout Rate', value: data.avg_dropout_rate * 100,            suffix: '%', decimals: 0, active: true },
    { label: 'Solo Win Rate',    value: soloWinRate,                             suffix: '%', decimals: 0, active: true },
  ];

  return (
    <section className={styles.strip}>
      <p className={styles.eyebrow}>By the numbers</p>
      <div className={styles.grid}>
        {stats.map((s) => <StatItem key={s.label} {...s} />)}
      </div>
      <div className={styles.cta}>
        <Link className="button button--secondary button--sm" to="/statistics">
          Explore full statistics →
        </Link>
      </div>
    </section>
  );
}
