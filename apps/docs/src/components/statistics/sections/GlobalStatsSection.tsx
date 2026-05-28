import React from 'react';
import DiplomacyGlobalChart from '../charts/DiplomacyGlobalChart';
import GameDurationChart from '../charts/GameDurationChart';
import PlayerDropoutChart from '../charts/PlayerDropoutChart';
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
            Mean {(data.avg_duration_hours / 24).toFixed(0)}d · Median {(data.median_duration_hours / 24).toFixed(0)}d · σ {(data.std_duration_hours / 24).toFixed(0)}d
          </p>
          <GameDurationChart
            data={data.duration_distribution}
            mean_days={data.avg_duration_hours / 24}
            median_days={data.median_duration_hours / 24}
          />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Victory Types</h3>
          <p className={styles.chartSubtitle}>How games were won</p>
          <VictoryTypeChart data={data.victory_type_distribution} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Player Dropout</h3>
          <p className={styles.chartSubtitle}>
            Avg {(data.avg_dropout_rate * 100).toFixed(0)}% of players drop out before the game ends
          </p>
          <PlayerDropoutChart dropout_rate={data.avg_dropout_rate} total_players={data.avg_players_per_game} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Diplomacy per Game</h3>
          <p className={styles.chartSubtitle}>
            Avg {data.avg_wars_per_game.toFixed(0)} wars · {data.avg_right_of_ways_per_game.toFixed(0)} right-of-ways · {data.avg_peace_treaties_per_game.toFixed(0)} peace treaties
          </p>
          <DiplomacyGlobalChart data={data} />
        </div>
      </div>
    </section>
  );
}
