"""Section 2.1 — global metrics aggregated across all games."""
import statistics

from .base import BaseAggregator
from ..models.aggregates import DurationBucket, GlobalAggregate
from ..models.intermediate import GameData

_BUCKET_COUNT = 12


class GlobalAggregator(BaseAggregator[GlobalAggregate]):
    def aggregate(self, games: list[GameData]) -> GlobalAggregate:
        if not games:
            return GlobalAggregate(
                total_games=0,
                avg_duration_hours=0,
                median_duration_hours=0,
                std_duration_hours=0,
                duration_distribution=[],
                victory_type_distribution={},
                avg_players_per_game=0,
                avg_human_players_per_game=0,
                player_count_distribution={},
                avg_dropout_rate=0,
                avg_game_days=0,
            )

        durations = [
            (g.end_time - g.start_time).total_seconds() / 3600.0 for g in games
        ]

        distribution = _build_histogram(durations, _BUCKET_COUNT)

        victory_dist: dict[str, int] = {}
        for g in games:
            victory_dist[g.victory_type] = victory_dist.get(g.victory_type, 0) + 1

        human_counts = [
            sum(1 for p in g.players if not p.is_ai) for g in games
        ]
        total_counts = [len(g.players) for g in games]

        # Distribution keyed by human player count (more meaningful for the UI)
        human_count_dist: dict[str, int] = {}
        for c in human_counts:
            human_count_dist[str(c)] = human_count_dist.get(str(c), 0) + 1

        dropout_rates = []
        for g in games:
            human = [p for p in g.players if not p.is_ai]
            if human:
                defeated = sum(1 for p in human if p.is_defeated)
                dropout_rates.append(defeated / len(human))

        # avg_game_days from duration (day ≈ 4h real time in CoN speed 1)
        # Use day_of_game when available (> 1), otherwise estimate from duration
        game_days_list = []
        for g in games:
            if g.game_days > 1:
                game_days_list.append(float(g.game_days))
            else:
                hours = (g.end_time - g.start_time).total_seconds() / 3600.0
                game_days_list.append(hours / 4.0)

        return GlobalAggregate(
            total_games=len(games),
            avg_duration_hours=statistics.mean(durations),
            median_duration_hours=statistics.median(durations),
            std_duration_hours=statistics.stdev(durations) if len(durations) > 1 else 0.0,
            duration_distribution=distribution,
            victory_type_distribution=victory_dist,
            avg_players_per_game=statistics.mean(human_counts),
            avg_human_players_per_game=statistics.mean(human_counts),
            player_count_distribution=human_count_dist,
            avg_dropout_rate=statistics.mean(dropout_rates) if dropout_rates else 0.0,
            avg_game_days=statistics.mean(game_days_list) if game_days_list else 0.0,
        )


def _build_histogram(values: list[float], n_buckets: int) -> list[DurationBucket]:
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return [DurationBucket(min_hours=lo, max_hours=hi, count=len(values))]
    width = (hi - lo) / n_buckets
    buckets: list[DurationBucket] = []
    for i in range(n_buckets):
        b_lo = lo + i * width
        b_hi = lo + (i + 1) * width
        # Last bucket is closed on both ends
        if i < n_buckets - 1:
            count = sum(1 for v in values if b_lo <= v < b_hi)
        else:
            count = sum(1 for v in values if b_lo <= v <= b_hi)
        buckets.append(DurationBucket(min_hours=round(b_lo, 1), max_hours=round(b_hi, 1), count=count))
    return buckets
