import React, { useState } from 'react';
import CountryTerritoryChart from '../charts/CountryTerritoryChart';
import CountryWinRateChart from '../charts/CountryWinRateChart';
import type { CountryAggregate } from '../types';
import styles from './Section.module.css';

interface Props {
  data: CountryAggregate[];
}

const MIN_GAMES_OPTIONS = [3, 5, 10, 20];

export default function CountryStatsSection({ data }: Props) {
  const [minGames, setMinGames] = useState(5);

  const eligible = data.filter((c) => c.games_played >= minGames);

  return (
    <section className={styles.section}>
      <div className={styles.sectionHeader}>
        <div>
          <h2 className={styles.heading}>Country Performance</h2>
          <p className={styles.description}>
            Aggregated across all games per nation. {eligible.length} nations with ≥{minGames} games.
          </p>
        </div>
        <div className={styles.filter}>
          <label htmlFor="min-games" className={styles.filterLabel}>
            Min games:
          </label>
          <select
            id="min-games"
            className={styles.filterSelect}
            value={minGames}
            onChange={(e) => setMinGames(Number(e.target.value))}
          >
            {MIN_GAMES_OPTIONS.map((n) => (
              <option key={n} value={n}>
                {n}+
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className={styles.grid}>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Win Rate by Country (Top 20)</h3>
          <p className={styles.chartSubtitle}>% of games won · coloured by performance tier</p>
          <CountryWinRateChart data={data} minGames={minGames} topN={20} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Territory Control (Top 20)</h3>
          <p className={styles.chartSubtitle}>Average provinces at start vs end of game</p>
          <CountryTerritoryChart data={data} minGames={minGames} topN={20} />
        </div>
      </div>
    </section>
  );
}
