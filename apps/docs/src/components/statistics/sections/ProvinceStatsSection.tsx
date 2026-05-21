import React, { useState } from 'react';
import ProvinceContestedChart from '../charts/ProvinceContestedChart';
import ProvinceMoraleChart from '../charts/ProvinceMoraleChart';
import ProvinceWinCorrelationChart from '../charts/ProvinceWinCorrelationChart';
import type { ProvinceAggregate } from '../types';
import styles from './Section.module.css';

interface Props {
  data: ProvinceAggregate[];
}

export default function ProvinceStatsSection({ data }: Props) {
  const [showCoastal, setShowCoastal] = useState<'all' | 'land' | 'coastal'>('all');

  const filtered = data.filter((p) => {
    if (showCoastal === 'coastal') return p.is_coastal;
    if (showCoastal === 'land') return !p.is_coastal;
    return true;
  });

  return (
    <section className={styles.section}>
      <div className={styles.sectionHeader}>
        <div>
          <h2 className={styles.heading}>Province Analysis</h2>
          <p className={styles.description}>
            Strategic importance and contest patterns across {data.length} provinces.
          </p>
        </div>
        <div className={styles.filter}>
          <label className={styles.filterLabel}>Filter:</label>
          <select
            className={styles.filterSelect}
            value={showCoastal}
            onChange={(e) => setShowCoastal(e.target.value as 'all' | 'land' | 'coastal')}
          >
            <option value="all">All provinces</option>
            <option value="land">Inland only</option>
            <option value="coastal">Coastal only</option>
          </select>
        </div>
      </div>
      <div className={styles.grid}>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Most Contested Provinces (Top 25)</h3>
          <p className={styles.chartSubtitle}>
            % of games where ownership changed at least once
          </p>
          <ProvinceContestedChart data={filtered} topN={25} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Win Correlation (Top 25)</h3>
          <p className={styles.chartSubtitle}>
            % of games where the winner controlled this province at game end
          </p>
          <ProvinceWinCorrelationChart data={filtered} topN={25} />
        </div>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Province Morale (Top 20)</h3>
          <p className={styles.chartSubtitle}>Average morale across all games · coloured by terrain type</p>
          <ProvinceMoraleChart data={filtered} topN={20} />
        </div>
      </div>
    </section>
  );
}
