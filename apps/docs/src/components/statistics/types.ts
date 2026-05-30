/** TypeScript interfaces mirroring the Python Pydantic aggregate models in game_stats_extractor. */

/** Wire format for columnar JSON files (countries.json, provinces.json). */
export interface ColumnarData {
  columns: string[];
  rows: unknown[][];
}

export interface DurationBucket {
  min_days: number;
  max_days: number;
  count: number;
}

export interface GlobalAggregate {
  total_games: number;
  avg_duration_hours: number;
  median_duration_hours: number;
  std_duration_hours: number;
  duration_distribution: DurationBucket[];
  victory_type_distribution: Record<string, number>;
  avg_players_per_game: number;
  avg_human_players_per_game: number;
  player_count_distribution: Record<string, number>;
  avg_dropout_rate: number;
  avg_game_days: number;
  avg_update_interval_seconds: number;
  avg_wars_per_game: number;
  avg_peace_treaties_per_game: number;
  avg_alliances_per_game: number;
  avg_right_of_ways_per_game: number;
}

export interface CountryAggregate {
  nation_name: string;
  games_played: number;
  wins: number;
  win_rate: number;
  avg_final_vp: number;
  avg_placement: number;
  median_placement: number;
  avg_final_provinces: number;
  avg_initial_provinces: number;
  avg_expansion: number;
  avg_provinces_captured: number;
  avg_provinces_lost: number;
  elimination_rate: number;
  avg_survival_days: number;
  avg_wars_declared: number;
  avg_peace_treaties_signed: number;
  avg_alliances_formed: number;
  avg_right_of_ways_signed: number;
}

export interface ProvinceAggregate {
  province_id: number;
  province_name: string;
  terrain_type: string;
  is_coastal: boolean;
  games_appeared: number;
  avg_ownership_changes: number;
  contest_frequency: number;
  win_correlation: number;
  resource_production_type: string | null;
  avg_resource_production: number;
  avg_money_production: number;
  avg_morale: number;
}

export interface TimeSeriesPoint {
  bucket: number;
  avg_provinces: number;
  avg_vp: number;
  games_sampled: number;
}

export interface CountryTimeSeries {
  nation_name: string;
  games_played: number;
  pct_game: TimeSeriesPoint[];
  game_days: TimeSeriesPoint[];
}

export interface PlayerActivityPoint {
  bucket: number;
  avg_alive: number;
  avg_alive_human: number;
  games_sampled: number;
}

export interface TimeSeriesOutput {
  countries: CountryTimeSeries[];
  pct_buckets: number[];
  max_game_days: number;
  generated_at: string;
  player_activity_pct: PlayerActivityPoint[];
  player_activity_days: PlayerActivityPoint[];
}

export interface MetaInfo {
  game_count: number;
  failed_replays: number;
  generated_at: string;
  replay_dir: string;
  date_range_start: string | null;
  date_range_end: string | null;
}
