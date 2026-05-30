"""Section 1.4 — per-country province-count and VP time series, averaged across all games."""
import statistics
from collections import defaultdict
from datetime import datetime

from .base import BaseAggregator
from ..models.aggregates import CountryTimeSeries, PlayerActivityPoint, TimeSeriesOutput, TimeSeriesPoint
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
                [p.pct_buckets for _, p in entries],
                [p.pct_vp_buckets for _, p in entries],
                _PCT_BUCKETS,
            )

            all_day_keys: set[int] = set()
            for _, p in entries:
                all_day_keys.update(p.day_buckets.keys())
            day_series = _aggregate_buckets(
                [p.day_buckets for _, p in entries],
                [p.day_vp_buckets for _, p in entries],
                sorted(all_day_keys),
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

        player_activity_pct = _aggregate_player_activity(games, _PCT_BUCKETS, mode="pct")
        player_activity_days = _aggregate_player_activity(
            games, list(range(max_game_days + 1)), mode="days"
        )

        return TimeSeriesOutput(
            countries=countries,
            pct_buckets=_PCT_BUCKETS,
            max_game_days=max_game_days,
            generated_at=datetime.utcnow(),
            player_activity_pct=player_activity_pct,
            player_activity_days=player_activity_days,
        )


def _aggregate_player_activity(
    games: list[GameData],
    bucket_keys: list[int],
    mode: str,
) -> list[PlayerActivityPoint]:
    points: list[PlayerActivityPoint] = []
    for b in bucket_keys:
        alive_vals = []
        human_vals = []
        if mode == "pct":
            for g in games:
                if b in g.pct_alive_buckets:
                    alive_vals.append(g.pct_alive_buckets[b])
                    human_vals.append(g.pct_human_buckets.get(b, 0))
        else:
            for g in games:
                if b in g.day_alive_buckets:
                    alive_vals.append(g.day_alive_buckets[b])
                    human_vals.append(g.day_human_buckets.get(b, 0))
        if not alive_vals:
            continue
        points.append(PlayerActivityPoint(
            bucket=b,
            avg_alive=round(statistics.mean(alive_vals), 2),
            avg_alive_human=round(statistics.mean(human_vals), 2),
            games_sampled=len(alive_vals),
        ))
    return points


def _aggregate_buckets(
    prov_buckets: list[dict[int, int]],
    vp_buckets: list[dict[int, int]],
    bucket_keys: list[int],
) -> list[TimeSeriesPoint]:
    points: list[TimeSeriesPoint] = []
    for b in bucket_keys:
        prov_values = [pb[b] for pb in prov_buckets if b in pb]
        vp_values = [vb[b] for vb in vp_buckets if b in vb]
        if not prov_values:
            continue
        points.append(TimeSeriesPoint(
            bucket=b,
            avg_provinces=round(statistics.mean(prov_values), 2),
            avg_vp=round(statistics.mean(vp_values), 2) if vp_values else 0.0,
            games_sampled=len(prov_values),
        ))
    return points
