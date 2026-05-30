import type {
  ColumnarData,
  CountryAggregate,
  CountryTimeSeries,
  PlayerActivityPoint,
  ProvinceAggregate,
  TimeSeriesOutput,
} from './types';

export function deserializeCountries(raw: ColumnarData): CountryAggregate[] {
  const idx = Object.fromEntries(raw.columns.map((c, i) => [c, i]));
  return raw.rows.map((r) => ({
    nation_name:           r[idx.nation_name]           as string,
    games_played:          r[idx.games_played]          as number,
    wins:                  r[idx.wins]                  as number,
    win_rate:              r[idx.win_rate]              as number,
    avg_final_vp:          r[idx.avg_final_vp]          as number,
    avg_placement:         r[idx.avg_placement]         as number,
    median_placement:      r[idx.median_placement]      as number,
    avg_final_provinces:   r[idx.avg_final_provinces]   as number,
    avg_initial_provinces: r[idx.avg_initial_provinces] as number,
    avg_expansion:         r[idx.avg_expansion]         as number,
    avg_provinces_captured:r[idx.avg_provinces_captured]as number,
    avg_provinces_lost:    r[idx.avg_provinces_lost]    as number,
    elimination_rate:          r[idx.elimination_rate]          as number,
    avg_survival_days:         r[idx.avg_survival_days]         as number,
    avg_wars_declared:         r[idx.avg_wars_declared]         as number,
    avg_peace_treaties_signed: r[idx.avg_peace_treaties_signed] as number,
    avg_alliances_formed:      r[idx.avg_alliances_formed]      as number,
    avg_right_of_ways_signed:  r[idx.avg_right_of_ways_signed]  as number,
  }));
}

export function deserializeProvinces(raw: ColumnarData): ProvinceAggregate[] {
  const idx = Object.fromEntries(raw.columns.map((c, i) => [c, i]));
  return raw.rows.map((r) => ({
    province_id:              r[idx.province_id]              as number,
    province_name:            r[idx.province_name]            as string,
    terrain_type:             r[idx.terrain_type]             as string,
    is_coastal:               r[idx.is_coastal]               as boolean,
    games_appeared:           r[idx.games_appeared]           as number,
    avg_ownership_changes:    r[idx.avg_ownership_changes]    as number,
    contest_frequency:        r[idx.contest_frequency]        as number,
    win_correlation:          r[idx.win_correlation]          as number,
    resource_production_type: r[idx.resource_production_type] as string | null,
    avg_resource_production:  r[idx.avg_resource_production]  as number,
    avg_money_production:     r[idx.avg_money_production]     as number,
    avg_morale:               r[idx.avg_morale]               as number,
  }));
}

export function deserializeTimeSeries(raw: {
  pct_buckets: number[];
  max_game_days: number;
  generated_at: string;
  pct_alive?: (number | null)[];
  pct_alive_human?: (number | null)[];
  pct_alive_n?: (number | null)[];
  day_alive?: (number | null)[];
  day_alive_human?: (number | null)[];
  day_alive_n?: (number | null)[];
  countries: Array<{
    nation_name: string;
    games_played: number;
    pct_avg: (number | null)[];
    pct_n:   (number | null)[];
    pct_vp_avg?: (number | null)[];
    day_avg: (number | null)[];
    day_n:   (number | null)[];
    day_vp_avg?: (number | null)[];
  }>;
}): TimeSeriesOutput {
  const player_activity_pct: PlayerActivityPoint[] = raw.pct_buckets
    .map((b, i) => raw.pct_alive?.[i] != null
      ? {
          bucket: b,
          avg_alive: raw.pct_alive![i]!,
          avg_alive_human: raw.pct_alive_human?.[i] ?? 0,
          games_sampled: (raw.pct_alive_n?.[i] ?? 0) as number,
        }
      : null)
    .filter((p): p is PlayerActivityPoint => p !== null);

  const player_activity_days: PlayerActivityPoint[] = (raw.day_alive ?? [])
    .map((v, i) => v != null
      ? {
          bucket: i,
          avg_alive: v,
          avg_alive_human: raw.day_alive_human?.[i] ?? 0,
          games_sampled: (raw.day_alive_n?.[i] ?? 0) as number,
        }
      : null)
    .filter((p): p is PlayerActivityPoint => p !== null);

  return {
    pct_buckets:  raw.pct_buckets,
    max_game_days: raw.max_game_days,
    generated_at:  raw.generated_at,
    player_activity_pct,
    player_activity_days,
    countries: raw.countries.map((c): CountryTimeSeries => ({
      nation_name:  c.nation_name,
      games_played: c.games_played,
      pct_game: raw.pct_buckets
        .map((b, i) => c.pct_avg[i] != null
          ? { bucket: b, avg_provinces: c.pct_avg[i]!, avg_vp: c.pct_vp_avg?.[i] ?? 0, games_sampled: c.pct_n[i]! }
          : null)
        .filter((p): p is NonNullable<typeof p> => p !== null),
      game_days: c.day_avg
        .map((v, i) => v != null
          ? { bucket: i, avg_provinces: v, avg_vp: c.day_vp_avg?.[i] ?? 0, games_sampled: c.day_n[i]! }
          : null)
        .filter((p): p is NonNullable<typeof p> => p !== null),
    })),
  };
}
