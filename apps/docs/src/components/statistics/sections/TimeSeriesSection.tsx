import React from 'react';
import CountryProvincesTimeSeriesChart from '../charts/CountryProvincesTimeSeriesChart';
import CountryRadarChart from '../charts/CountryRadarChart';
import type { CountryAggregate, TimeSeriesOutput } from '../types';
import styles from './Section.module.css';

interface Props {
  data: TimeSeriesOutput;
  countries: CountryAggregate[];
}

export default function TimeSeriesSection({ data, countries }: Props) {
  return (
    <section className={styles.section}>
      <div className={styles.sectionHeader}>
        <div>
          <h2 className={styles.heading}>Province Control Over Time</h2>
          <p className={styles.description}>
            Average territory per country across {data.countries.length} nations · top 10 by games played · toggle between % of game and absolute game days
          </p>
        </div>
      </div>
      <div className={styles.grid}>
        <div className={styles.chartCard} style={{ gridColumn: '1 / -1' }}>
          <h3 className={styles.chartTitle}>Province Count Progression (Top 10 Nations)</h3>
          <p className={styles.chartSubtitle}>Avg provinces held at each point in the game · use buttons to switch time axis</p>
          <CountryProvincesTimeSeriesChart data={data} countries={countries} topN={10} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Nation Profile Comparison (Top 6)</h3>
          <p className={styles.chartSubtitle}>Normalized across all nations · win rate, expansion, aggression, survival, territory</p>
          <CountryRadarChart data={countries} topN={6} />
        </div>
      </div>
    </section>
  );
}
