"""Section 1.4 — per-country province-count time series, averaged across all games."""
import statistics
from collections import defaultdict
from datetime import datetime

from .base import BaseAggregator
from ..models.aggregates import CountryTimeSeries, TimeSeriesOutput, TimeSeriesPoint
from ..models.intermediate import GameData, PlayerData

_PCT_BUCKETS = list(range(0, 101, 5))


class TimeSeriesAggregator(BaseAggregator[TimeSeriesOutput]):
    def __init__(self, min_games: int = 3):
        self._min_games = min_games

    def aggregate(self, games: list[GameData]) -> TimeSeriesOutput:
        by_nation: dict[str, list[tuple[GameData, PlayerData]]] = defaultdict(list)
        for game in games:
            for player in game.players:
                by_nation[player.nation_name].append((game, player))

        countries: list[CountryTimeSeries] = []
        max_game_days = 0

        for nation_name, entries in by_nation.items():
            if len(entries) < self._min_games:
                continue

            pct_series = _aggregate_buckets(
                [p.pct_buckets for _, p in entries], _PCT_BUCKETS
            )

            all_day_keys: set[int] = set()
            for _, p in entries:
                all_day_keys.update(p.day_buckets.keys())
            day_series = _aggregate_buckets(
                [p.day_buckets for _, p in entries], sorted(all_day_keys)
            )

            if all_day_keys:
                max_game_days = max(max_game_days, max(all_day_keys))

            countries.append(CountryTimeSeries(
                nation_name=nation_name,
                games_played=len(entries),
                pct_game=pct_series,
                game_days=day_series,
            ))

        countries.sort(key=lambda c: c.games_played, reverse=True)

        return TimeSeriesOutput(
            countries=countries,
            pct_buckets=_PCT_BUCKETS,
            max_game_days=max_game_days,
            generated_at=datetime.utcnow(),
        )


def _aggregate_buckets(
    player_buckets: list[dict[int, int]],
    bucket_keys: list[int],
) -> list[TimeSeriesPoint]:
    points: list[TimeSeriesPoint] = []
    for b in bucket_keys:
        values = [pb[b] for pb in player_buckets if b in pb]
        if not values:
            continue
        points.append(TimeSeriesPoint(
            bucket=b,
            avg_provinces=round(statistics.mean(values), 2),
            games_sampled=len(values),
        ))
    return points
