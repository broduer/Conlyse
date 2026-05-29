import React from 'react';
import CountryMoneyProductionChart from '../charts/CountryMoneyProductionChart';
import CountryProductionRateChart from '../charts/CountryProductionRateChart';
import EconomicProductionGlobalChart from '../charts/EconomicProductionGlobalChart';
import EconomicProductionTimeSeriesChart from '../charts/EconomicProductionTimeSeriesChart';
import type { CountryAggregate, GlobalAggregate, TimeSeriesOutput } from '../types';
import styles from './Section.module.css';

interface Props {
  global: GlobalAggregate;
  countries: CountryAggregate[];
  timeseries: TimeSeriesOutput;
}

export default function EconomicStatsSection({ global: g, countries, timeseries }: Props) {
  const prodData = g.avg_game_total_production;
  if (!prodData || Object.keys(prodData).length === 0) {
    return (
      <section className={styles.section}>
        <h2 className={styles.heading}>Economic Overview</h2>
        <p className={styles.description}>
          No economic data available — re-run the extractor to generate these metrics.
        </p>
      </section>
    );
  }

  const totalMoney = prodData['MONEY'] ?? 0;
  const resourceTypes = Object.keys(prodData).filter((k) => k !== 'MONEY');

  return (
    <section className={styles.section}>
      <div className={styles.sectionHeader}>
        <div>
          <h2 className={styles.heading}>Economic Overview</h2>
          <p className={styles.description}>
            Avg {totalMoney >= 1e6
              ? `${(totalMoney / 1e6).toFixed(1)}M`
              : `${(totalMoney / 1e3).toFixed(0)}k`} money earned per game
            {resourceTypes.length > 0 && ` · ${resourceTypes.length} resource type${resourceTypes.length !== 1 ? 's' : ''} tracked`}.
          </p>
        </div>
      </div>
      <div className={styles.grid}>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Average Production per Game</h3>
          <p className={styles.chartSubtitle}>Total production accumulated over an average game, by resource type</p>
          <EconomicProductionGlobalChart data={prodData} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Average Money Earned by Country (Top 20)</h3>
          <p className={styles.chartSubtitle}>Total money accumulated over an average game · sorted by earnings</p>
          <CountryMoneyProductionChart data={countries} topN={20} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Production Rate by Resource Type (Top 20)</h3>
          <p className={styles.chartSubtitle}>Time-averaged production rate per country · stacked by resource type</p>
          <CountryProductionRateChart data={countries} topN={20} />
        </div>
        <div className={styles.chartCard} style={{ gridColumn: '1 / -1' }}>
          <h3 className={styles.chartTitle}>Production Rate Over Game Progression (Top 10)</h3>
          <p className={styles.chartSubtitle}>Avg production rate per day · top 10 countries by win rate</p>
          <EconomicProductionTimeSeriesChart data={timeseries} countries={countries} topN={10} />
        </div>
      </div>
    </section>
  );
}
