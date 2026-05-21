"""Serializes aggregate models to JSON files in the output directory."""
import json
from datetime import datetime
from pathlib import Path

from .models.aggregates import CountryAggregate, GlobalAggregate, MetaInfo, ProvinceAggregate
from .models.intermediate import GameData


def _default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def write_output(
    output_dir: Path,
    global_agg: GlobalAggregate,
    country_aggs: list[CountryAggregate],
    province_aggs: list[ProvinceAggregate],
    games: list[GameData],
    replay_dir: Path,
    failed_replays: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    start_times = [g.start_time for g in games]
    meta = MetaInfo(
        game_count=len(games),
        failed_replays=failed_replays,
        generated_at=datetime.utcnow(),
        replay_dir=str(replay_dir),
        date_range_start=min(start_times) if start_times else None,
        date_range_end=max(start_times) if start_times else None,
    )

    _write_json(output_dir / "global.json", global_agg.model_dump())
    _write_json(output_dir / "countries.json", [c.model_dump() for c in country_aggs])
    _write_json(output_dir / "provinces.json", [p.model_dump() for p in province_aggs])
    _write_json(output_dir / "meta.json", meta.model_dump())


def _write_json(path: Path, data) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=_default)
