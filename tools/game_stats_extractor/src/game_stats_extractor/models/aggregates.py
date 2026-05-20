"""
Pydantic output models for cross-game aggregate statistics (Step 2).
These are serialized to JSON for the Docusaurus statistics page.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DurationBucket(BaseModel):
    min_hours: float
    max_hours: float
    count: int


class GlobalAggregate(BaseModel):
    """Section 2.1 — global metrics across all games."""
    total_games: int
    avg_duration_hours: float
    median_duration_hours: float
    std_duration_hours: float
    duration_distribution: list[DurationBucket]
    victory_type_distribution: dict[str, int]
    avg_players_per_game: float
    avg_human_players_per_game: float
    player_count_distribution: dict[str, int]
    avg_dropout_rate: float
    avg_game_days: float


class CountryAggregate(BaseModel):
    """Section 2.2 — per-country aggregate across all games where that country was played."""
    nation_name: str
    games_played: int
    wins: int
    win_rate: float
    avg_final_vp: float
    avg_placement: float
    avg_final_provinces: float
    avg_initial_provinces: float
    avg_expansion: float
    elimination_rate: float
    avg_survival_days: float


class ProvinceAggregate(BaseModel):
    """Section 2.3 — per-province aggregate across all games where that province appeared."""
    province_id: int
    province_name: str
    terrain_type: str
    is_coastal: bool
    games_appeared: int
    avg_ownership_changes: float
    contest_frequency: float
    win_correlation: float
    resource_production_type: Optional[str]
    avg_resource_production: float
    avg_money_production: float


class MetaInfo(BaseModel):
    """Metadata written alongside aggregate JSON files."""
    game_count: int
    failed_replays: int
    generated_at: datetime
    replay_dir: str
    date_range_start: Optional[datetime]
    date_range_end: Optional[datetime]
