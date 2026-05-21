import React from 'react';
import CountryAggressivenessChart from '../charts/CountryAggressivenessChart';
import CountryEliminationChart from '../charts/CountryEliminationChart';
import CountryExpansionChart from '../charts/CountryExpansionChart';
import CountryPlacementChart from '../charts/CountryPlacementChart';
import CountryTerritoryChart from '../charts/CountryTerritoryChart';
import CountryWinRateChart from '../charts/CountryWinRateChart';
import type { CountryAggregate } from '../types';
import styles from './Section.module.css';

interface Props {
  data: CountryAggregate[];
}

export default function CountryStatsSection({ data }: Props) {
  return (
    <section className={styles.section}>
      <div className={styles.sectionHeader}>
        <div>
          <h2 className={styles.heading}>Country Performance</h2>
          <p className={styles.description}>
            Aggregated across all games per nation. {data.length} nations.
          </p>
        </div>
      </div>
      <div className={styles.grid}>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Win Rate by Country (Top 20)</h3>
          <p className={styles.chartSubtitle}>% of games won · coloured by performance tier</p>
          <CountryWinRateChart data={data} topN={20} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Territory Control (Top 20)</h3>
          <p className={styles.chartSubtitle}>Average provinces at start vs end of game</p>
          <CountryTerritoryChart data={data} topN={20} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Average Placement (Top 20)</h3>
          <p className={styles.chartSubtitle}>Lower = better rank · avg VP shown in tooltip</p>
          <CountryPlacementChart data={data} topN={20} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Elimination Rate (Top 20)</h3>
          <p className={styles.chartSubtitle}>% of games where country was eliminated · avg survival days in tooltip</p>
          <CountryEliminationChart data={data} topN={20} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Territory Expansion (Top 20)</h3>
          <p className={styles.chartSubtitle}>Avg province gain from game start to end</p>
          <CountryExpansionChart data={data} topN={20} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Territory Aggressiveness (Top 20)</h3>
          <p className={styles.chartSubtitle}>Avg provinces captured per game · tooltip shows losses and net gain</p>
          <CountryAggressivenessChart data={data} topN={20} />
        </div>
      </div>
    </section>
  );
}
