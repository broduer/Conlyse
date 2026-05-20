import React from 'react';
import GameDurationChart from '../charts/GameDurationChart';
import PlayerCountChart from '../charts/PlayerCountChart';
import VictoryTypeChart from '../charts/VictoryTypeChart';
import type { GlobalAggregate } from '../types';
import styles from './Section.module.css';

interface Props {
  data: GlobalAggregate;
}

export default function GlobalStatsSection({ data }: Props) {
  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Global Overview</h2>
      <p className={styles.description}>
        Patterns across all {data.total_games.toLocaleString()} recorded games.
      </p>
      <div className={styles.grid}>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Game Duration Distribution</h3>
          <p className={styles.chartSubtitle}>
            Median {data.median_duration_hours.toFixed(0)}h · σ {data.std_duration_hours.toFixed(0)}h
          </p>
          <GameDurationChart data={data.duration_distribution} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Victory Types</h3>
          <p className={styles.chartSubtitle}>How games were won</p>
          <VictoryTypeChart data={data.victory_type_distribution} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Players per Game</h3>
          <p className={styles.chartSubtitle}>
            Avg {data.avg_human_players_per_game.toFixed(1)} human players
          </p>
          <PlayerCountChart data={data.player_count_distribution} />
        </div>
      </div>
    </section>
  );
}
