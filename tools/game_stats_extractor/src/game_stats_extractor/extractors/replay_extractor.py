"""
Extracts per-game statistics from a single .conrp replay file.

Opens the replay once, registers province hooks for owner_id and morale, then
iterates timestamps. Only changed provinces fire events — no full province scan
per tick. Player territory counts are maintained incrementally on ownership events.
"""
import logging
from collections import defaultdict
from pathlib import Path
from typing import Optional

from conflict_interface.hook_system.replay_hook_tag import ReplayHookTag
from conflict_interface.interface.replay_interface import ReplayInterface

from .base import BaseExtractor
from ..models.intermediate import GameData, PlayerData, ProvinceData

logger = logging.getLogger(__name__)

_UNOWNED = 0


def _is_land_province(province) -> bool:
    """True for LandProvince objects (which have owner_id / morale)."""
    return hasattr(province, "owner_id") and hasattr(province, "morale")


class ReplayExtractor(BaseExtractor):
    def __init__(self, map_data_dir: Optional[Path] = None):
        self._map_data_dir = map_data_dir

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract(self, file_path: Path) -> GameData:
        # --- Fast metadata check (no static map data needed) ---
        meta_replay = ReplayInterface(file_path)
        try:
            if not meta_replay.open(mode="read_metadata"):
                raise ValueError("replay.open(read_metadata) returned False")
            meta = meta_replay.get_timeline_metadata()
        finally:
            meta_replay.close()

        if not meta.game_ended:
            raise ValueError("game has not ended yet (game_ended=False in timeline metadata)")

        # --- Full extraction ---
        static_map_data = self._resolve_static_map_data(file_path)
        replay = ReplayInterface(file_path, static_map_data=static_map_data)
        try:
            if not replay.open():
                raise ValueError("replay.open() returned False — file may be incomplete or corrupted")
            return self._extract(replay, file_path, meta)
        finally:
            replay.close()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _resolve_static_map_data(self, file_path: Path) -> dict[str, Path]:
        if self._map_data_dir is None:
            return {}
        result: dict[str, Path] = {}
        for bin_file in self._map_data_dir.glob("*.bin"):
            result[bin_file.stem] = bin_file
        return result

    def _extract(self, replay: ReplayInterface, file_path: Path, meta) -> GameData:
        start_time = replay.start_time
        end_time = replay.last_time
        timestamps = replay.get_timestamps()
        total_updates = len(timestamps)
        avg_update_interval_seconds = (
            (end_time - start_time).total_seconds() / (total_updates - 1)
            if total_updates > 1
            else 0.0
        )

        # game_id and day_of_game come from the timeline metadata header (authoritative)
        game_id: int = meta.game_id or 0
        if not game_id:
            try:
                game_id = int(file_path.stem.replace("game_", ""))
            except (ValueError, AttributeError):
                pass
        game_days: int = meta.day_of_game or 0

        # ---- Initial state ----
        replay.jump_to(start_time)
        gs = replay.game_state
        if gs is None:
            raise ValueError("game_state is None after jump_to(start_time)")

        map_obj = gs.states.map_state.map
        map_id: str = getattr(map_obj, "map_id", "unknown")

        initial_land = {
            pid: p
            for pid, p in map_obj.provinces.items()
            if _is_land_province(p)
        }

        # Province static info (name, terrain, coastal) — read once
        province_meta: dict[int, dict] = {
            pid: {
                "name": p.name,
                "terrain_type": str(p.terrain_type.name) if hasattr(p.terrain_type, "name") else str(p.terrain_type),
                "is_coastal": bool(getattr(p, "costal", False)),
                "resource_production_type": (
                    str(p.resource_production_type.name)
                    if p.resource_production_type and hasattr(p.resource_production_type, "name")
                    else (str(p.resource_production_type) if p.resource_production_type else None)
                ),
            }
            for pid, p in initial_land.items()
        }

        initial_owners: dict[int, int] = {pid: p.owner_id for pid, p in initial_land.items()}

        # Incrementally maintained ownership and player counts
        current_owners: dict[int, int] = dict(initial_owners)
        current_player_counts: dict[int, int] = defaultdict(int)
        for oid in initial_owners.values():
            if oid > _UNOWNED:
                current_player_counts[oid] += 1

        ownership_changes: dict[int, int] = defaultdict(int)
        player_captures: dict[int, int] = defaultdict(int)
        player_losses: dict[int, int] = defaultdict(int)

        # Morale accumulators — seeded with the initial snapshot
        prov_morale_sum: dict[int, float] = {pid: float(p.morale) for pid, p in initial_land.items()}
        prov_morale_n: dict[int, int] = {pid: 1 for pid in initial_land}
        prov_morale_min: dict[int, float] = {pid: float(p.morale) for pid, p in initial_land.items()}
        prov_morale_max: dict[int, float] = {pid: float(p.morale) for pid, p in initial_land.items()}

        # Player territory accumulators — seeded with the initial snapshot
        player_prov_sum: dict[int, float] = defaultdict(float)
        player_prov_n: dict[int, int] = defaultdict(int)
        player_prov_max: dict[int, int] = defaultdict(int)
        player_prov_min: dict[int, int] = {}
        for player_id, cnt in current_player_counts.items():
            if cnt > 0:
                player_prov_sum[player_id] = float(cnt)
                player_prov_n[player_id] = 1
                player_prov_max[player_id] = cnt
                player_prov_min[player_id] = cnt

        # ---- Register hooks — only changed provinces fire events ----
        replay.register_province_trigger(["owner_id", "morale"])

        # ---- Iterate all timestamps ----
        while replay.jump_to_next_patch():
            events = replay.poll_events()
            for event in events.get(ReplayHookTag.ProvinceChanged, []):
                province = event.reference
                pid = province.id
                attrs = event.attributes

                if "owner_id" in attrs:
                    old_owner, new_owner = attrs["owner_id"]
                    ownership_changes[pid] += 1
                    current_owners[pid] = new_owner if new_owner is not None else _UNOWNED
                    if old_owner is not None and old_owner > _UNOWNED:
                        current_player_counts[old_owner] = max(0, current_player_counts[old_owner] - 1)
                        player_losses[old_owner] += 1
                    if new_owner is not None and new_owner > _UNOWNED:
                        current_player_counts[new_owner] += 1
                        player_captures[new_owner] += 1

                if "morale" in attrs:
                    _, new_morale = attrs["morale"]
                    if new_morale is not None:
                        morale = float(new_morale)
                        prov_morale_sum[pid] = prov_morale_sum.get(pid, 0.0) + morale
                        prov_morale_n[pid] = prov_morale_n.get(pid, 0) + 1
                        if pid in prov_morale_min:
                            prov_morale_min[pid] = min(prov_morale_min[pid], morale)
                            prov_morale_max[pid] = max(prov_morale_max[pid], morale)
                        else:
                            prov_morale_min[pid] = morale
                            prov_morale_max[pid] = morale

            # Snapshot player territory counts — O(players), not O(provinces)
            for player_id, cnt in current_player_counts.items():
                if cnt <= 0:
                    continue
                player_prov_sum[player_id] += cnt
                player_prov_n[player_id] += 1
                player_prov_max[player_id] = max(player_prov_max[player_id], cnt)
                if player_id in player_prov_min:
                    player_prov_min[player_id] = min(player_prov_min[player_id], cnt)
                else:
                    player_prov_min[player_id] = cnt

        # ---- Final state — game_state accessed once, only for production values ----
        gs = replay.game_state
        if gs is None:
            raise ValueError("game_state is None at end of replay")

        final_land = {
            pid: p
            for pid, p in gs.states.map_state.map.provinces.items()
            if _is_land_province(p)
        }

        # ---- Players ----
        players_map = gs.states.player_state.players

        initial_player_counts: dict[int, int] = defaultdict(int)
        for oid in initial_owners.values():
            if oid > _UNOWNED:
                initial_player_counts[oid] += 1

        players: list[PlayerData] = []
        for player_id, profile in players_map.items():
            # Skip system/neutral slots (pid <= 0) and Guest placeholder
            if player_id <= 0 or not profile.nation_name or profile.name == "Guest":
                continue
            n = player_prov_n.get(player_id, 1)
            players.append(PlayerData(
                player_id=player_id,
                nation_name=profile.nation_name,
                player_name=profile.name,
                team_id=profile.team_id,
                is_ai=bool(profile.computer_player),
                is_defeated=bool(profile.defeated),
                is_playing=bool(profile.playing),
                final_vp=int(profile.victory_points),
                initial_province_count=initial_player_counts.get(player_id, 0),
                final_province_count=current_player_counts.get(player_id, 0),
                max_province_count=player_prov_max.get(player_id, 0),
                min_province_count=player_prov_min.get(player_id, 0),
                avg_province_count=player_prov_sum.get(player_id, 0) / n,
                provinces_captured=player_captures.get(player_id, 0),
                provinces_lost=player_losses.get(player_id, 0),
            ))

        # ---- Victory detection ----
        winner_ids, victory_type = _determine_winners(players)

        # ---- Provinces ----
        provinces: list[ProvinceData] = []
        for pid, pmeta in province_meta.items():
            final_p = final_land.get(pid)
            n = prov_morale_n.get(pid, 1)
            provinces.append(ProvinceData(
                province_id=pid,
                province_name=pmeta["name"],
                terrain_type=pmeta["terrain_type"],
                is_coastal=pmeta["is_coastal"],
                initial_owner_id=initial_owners.get(pid, -1),
                final_owner_id=current_owners.get(pid, -1),
                ownership_changes=ownership_changes.get(pid, 0),
                resource_production_type=pmeta["resource_production_type"],
                resource_production=int(final_p.resource_production or 0) if final_p else 0,
                money_production=int(final_p.money_production) if final_p else 0,
                avg_morale=prov_morale_sum.get(pid, 0.0) / n,
                min_morale=prov_morale_min.get(pid, 0.0),
                max_morale=prov_morale_max.get(pid, 0.0),
            ))

        return GameData(
            game_id=game_id,
            map_id=map_id,
            file_path=str(file_path),
            start_time=start_time,
            end_time=end_time,
            game_days=game_days,
            total_updates=total_updates,
            avg_update_interval_seconds=avg_update_interval_seconds,
            winner_ids=winner_ids,
            victory_type=victory_type,
            game_ended=True,  # guaranteed by early exit in extract()
            players=players,
            provinces=provinces,
        )


def _determine_winners(players: list[PlayerData]) -> tuple[list[int], str]:
    if not players:
        return [], "unknown"

    # Prefer still-playing non-defeated players as the winner pool
    still_playing = [p for p in players if p.is_playing and not p.is_defeated]

    if len(still_playing) == 1:
        return [still_playing[0].player_id], "solo"

    if len(still_playing) >= 2:
        # All on same team → coalition
        team_ids = {p.team_id for p in still_playing if p.team_id > 0}
        if len(team_ids) == 1 and all(p.team_id > 0 for p in still_playing):
            return [p.player_id for p in still_playing], "coalition"

    # Fallback: use VP among non-defeated (covers games where playing flag is unreliable)
    pool = still_playing or [p for p in players if not p.is_defeated] or players
    max_vp = max((p.final_vp for p in pool), default=0)
    if max_vp <= 0:
        return [], "unknown"

    threshold = max_vp * 0.9
    winners = [p for p in pool if p.final_vp >= threshold]

    if len(winners) == 1:
        return [winners[0].player_id], "solo"

    team_ids = {p.team_id for p in winners if p.team_id > 0}
    if len(team_ids) == 1:
        return [p.player_id for p in winners], "coalition"

    top = max(winners, key=lambda p: p.final_vp)
    return [top.player_id], "solo"
