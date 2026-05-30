import React from 'react';
import CountryAggressivenessChart from '../charts/CountryAggressivenessChart';
import CountryDiplomacyChart from '../charts/CountryDiplomacyChart';
import CountryEliminationChart from '../charts/CountryEliminationChart';
import CountryExpansionChart from '../charts/CountryExpansionChart';
import CountryPlacementChart from '../charts/CountryPlacementChart';
import CountryRadarChart from '../charts/CountryRadarChart';
import CountryTerritoryChart from '../charts/CountryTerritoryChart';
import CountryVPTimeSeriesChart from '../charts/CountryVPTimeSeriesChart';
import CountryWinRateChart from '../charts/CountryWinRateChart';
import type { CountryAggregate, TimeSeriesOutput } from '../types';
import styles from './Section.module.css';

interface Props {
  data: CountryAggregate[];
  timeseries: TimeSeriesOutput;
}

export default function CountryStatsSection({ data, timeseries }: Props) {
  return (
    <section id="section-countries" className={styles.section}>
      <div className={styles.sectionHeader}>
        <div>
          <h2 className={styles.heading}>Country Performance</h2>
          <p className={styles.description}>
            Aggregated across all games per nation. {data.length} nations.
          </p>
        </div>
      </div>
      <div className={styles.grid}>
        <div id="chart-countries-vp" className={styles.chartCard} style={{ gridColumn: '1 / -1' }}>
          <h3 className={styles.chartTitle}>Victory Point Progression (Top 10 Nations)</h3>
          <p className={styles.chartSubtitle}>Avg VP at each point in the game for the top 10 nations by win rate · use buttons to switch time axis</p>
          <CountryVPTimeSeriesChart data={timeseries} countries={data} topN={10} />
        </div>
        <div id="chart-countries-winrate" className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Win Rate by Country (Top 20)</h3>
          <p className={styles.chartSubtitle}>% of games won · coloured by performance tier</p>
          <CountryWinRateChart data={data} topN={20} />
        </div>
        <div id="chart-countries-territory" className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Territory Control (Top 20)</h3>
          <p className={styles.chartSubtitle}>Average provinces at start vs end of game</p>
          <CountryTerritoryChart data={data} topN={20} />
        </div>
        <div id="chart-countries-placement" className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Average Placement (Top 20)</h3>
          <p className={styles.chartSubtitle}>Lower = better rank · avg VP shown in tooltip</p>
          <CountryPlacementChart data={data} topN={20} />
        </div>
        <div id="chart-countries-elimination" className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Elimination Rate (Top 20)</h3>
          <p className={styles.chartSubtitle}>% of games where country was eliminated · avg survival days in tooltip</p>
          <CountryEliminationChart data={data} topN={20} />
        </div>
        <div id="chart-countries-expansion" className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Territory Expansion (Top 20)</h3>
          <p className={styles.chartSubtitle}>Avg province gain from game start to end</p>
          <CountryExpansionChart data={data} topN={20} />
        </div>
        <div id="chart-countries-aggressiveness" className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Territory Aggressiveness (Top 20)</h3>
          <p className={styles.chartSubtitle}>Avg provinces captured vs lost per game</p>
          <CountryAggressivenessChart data={data} topN={20} />
        </div>
        <div id="chart-countries-diplomacy" className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Diplomatic Activity by Country (Top 20)</h3>
          <p className={styles.chartSubtitle}>Avg wars · right-of-ways · peace treaties per game · sorted by total activity</p>
          <CountryDiplomacyChart data={data} topN={20} />
        </div>
        <div id="chart-countries-radar" className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Nation Profile Comparison (Top 6)</h3>
          <p className={styles.chartSubtitle}>Top 6 by win rate · normalized across all nations · win rate, expansion, aggression, survival, territory</p>
          <CountryRadarChart data={data} topN={6} />
        </div>
      </div>
    </section>
  );
}
