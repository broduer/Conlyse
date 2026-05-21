import Layout from '@theme/Layout';
import React, { useEffect, useState } from 'react';
import StatsHero from '../../components/statistics/StatsHero';
import CountryStatsSection from '../../components/statistics/sections/CountryStatsSection';
import GlobalStatsSection from '../../components/statistics/sections/GlobalStatsSection';
import ProvinceStatsSection from '../../components/statistics/sections/ProvinceStatsSection';
import type {
  CountryAggregate,
  GlobalAggregate,
  MetaInfo,
  ProvinceAggregate,
} from '../../components/statistics/types';
import styles from './statistics.module.css';

interface StatsData {
  global: GlobalAggregate;
  countries: CountryAggregate[];
  provinces: ProvinceAggregate[];
  meta: MetaInfo;
}

const STATS_BASE_URL = 'https://r2.conlyse.zdox.dev/stats';

async function fetchStats(): Promise<StatsData> {
  const [global, countries, provinces, meta] = await Promise.all([
    fetch(`${STATS_BASE_URL}/global.json`).then((r) => r.json()),
    fetch(`${STATS_BASE_URL}/countries.json`).then((r) => r.json()),
    fetch(`${STATS_BASE_URL}/provinces.json`).then((r) => r.json()),
    fetch(`${STATS_BASE_URL}/meta.json`).then((r) => r.json()),
  ]);
  return { global, countries, provinces, meta };
}

export default function StatisticsPage() {
  const [data, setData] = useState<StatsData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats()
      .then(setData)
      .catch((err) => setError(String(err)));
  }, []);

  return (
    <Layout
      title="Statistics"
      description="Aggregated statistics from 1000+ recorded Conflict of Nations games"
    >
      <main className={styles.main}>
        {error && (
          <div className={styles.error}>
            <strong>Could not load statistics.</strong> Run the extractor first:
            <pre className={styles.errorPre}>
              {`pip install -e tools/game_stats_extractor\ngame-stats-extractor --replays-dir /path/to/replays --output /tmp/stats\n# then upload /tmp/stats/*.json to ${STATS_BASE_URL}`}
            </pre>
            <p className={styles.errorDetail}>{error}</p>
          </div>
        )}

        {!data && !error && (
          <div className={styles.loading}>
            <div className={styles.spinner} />
            <p>Loading statistics…</p>
          </div>
        )}

        {data && (
          <>
            <StatsHero global={data.global} meta={data.meta} />
            <GlobalStatsSection data={data.global} />
            <CountryStatsSection data={data.countries} />
            <ProvinceStatsSection data={data.provinces} />
          </>
        )}
      </main>
    </Layout>
  );
}
