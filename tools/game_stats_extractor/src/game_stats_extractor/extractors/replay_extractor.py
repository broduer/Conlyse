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

from conflict_interface.data_types.newest.foreign_affairs_state.foreign_affairs_state_enums import (
    ForeignAffairRelationTypes,
)
from conflict_interface.hook_system.replay_hook_tag import ReplayHookTag
from conflict_interface.interface.replay_interface import ReplayInterface

from .base import BaseExtractor
from ..models.intermediate import GameData, PlayerData, ProvinceData

logger = logging.getLogger(__name__)

_UNOWNED = 0


def _is_land_province(province) -> bool:
    """True for LandProvince objects (which have owner_id / morale)."""
    return hasattr(province, "owner_id") and hasattr(province, "morale")


def _pct_bucket(elapsed: float, total: float) -> int:
    if total <= 0:
        return 0
    return max(0, min(100, round((elapsed / total) * 100 / 5) * 5))


def _day_bucket(elapsed: float, total: float, game_days: int) -> int:
    if total <= 0 or game_days <= 0:
        return 0
    return round((elapsed / total) * game_days)


def _finalize_buckets(sums: dict[int, float], ns: dict[int, int]) -> dict[int, int]:
    return {b: round(sums[b] / ns[b]) for b in sums if ns[b] > 0}


def _finalize_float_buckets(sums: dict[int, float], ns: dict[int, int]) -> dict[int, float]:
    return {b: sums[b] / ns[b] for b in sums if ns[b] > 0}


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

        # Province production state: pid -> {resource_type_name: current_amount}
        # "MONEY" always present; additional type key present if province has resource_production_type
        province_production: dict[int, dict[str, float]] = {}
        for pid, p in initial_land.items():
            prod: dict[str, float] = {"MONEY": float(int(p.money_production or 0))}
            rtype = province_meta[pid]["resource_production_type"]
            if rtype:
                prod[rtype] = float(int(p.resource_production or 0))
            province_production[pid] = prod

        # Per-player running production sums (updated on ownership and upgrade events)
        current_player_production: dict[int, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for pid, prod in province_production.items():
            owner = initial_owners[pid]
            if owner > _UNOWNED:
                for rtype, amount in prod.items():
                    current_player_production[owner][rtype] += amount

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

        # Time-series bucket accumulators
        total_duration_seconds = (end_time - start_time).total_seconds()
        pct_bucket_sum: dict[int, dict[int, float]] = defaultdict(lambda: defaultdict(float))
        pct_bucket_n: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
        day_bucket_sum: dict[int, dict[int, float]] = defaultdict(lambda: defaultdict(float))
        day_bucket_n: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))

        # Production accumulators: [player_id][resource_type][bucket]
        player_prod_sum: dict[int, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        player_prod_n: dict[int, int] = defaultdict(int)
        player_total_prod: dict[int, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        player_peak_prod: dict[int, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        prod_pct_sum: dict[int, dict[str, dict[int, float]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        prod_pct_n:   dict[int, dict[str, dict[int, int]]]   = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        prod_day_sum: dict[int, dict[str, dict[int, float]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        prod_day_n:   dict[int, dict[str, dict[int, int]]]   = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        prev_time = start_time

        # Diplomacy counters — keyed by 1-indexed player id; populated by ForeignAffairsChanged events
        dp_wars: dict[int, int] = defaultdict(int)
        dp_peace: dict[int, int] = defaultdict(int)
        dp_alliances: dict[int, int] = defaultdict(int)
        dp_allianced: dict[int, int] = defaultdict(int)
        dp_rows: dict[int, int] = defaultdict(int)
        game_wars = game_peace = game_alliances = game_allianced = game_rows = 0

        # ---- Register hooks — only changed provinces/relations fire events ----
        replay.register_province_trigger(["owner_id", "morale", "resource_production", "money_production"])
        replay.register_foreign_affairs_trigger()

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
                    # Transfer production sums between players
                    for rtype, amount in province_production.get(pid, {}).items():
                        if amount <= 0:
                            continue
                        if old_owner is not None and old_owner > _UNOWNED:
                            current_player_production[old_owner][rtype] = max(
                                0.0, current_player_production[old_owner][rtype] - amount
                            )
                        if new_owner is not None and new_owner > _UNOWNED:
                            current_player_production[new_owner][rtype] += amount

                if "money_production" in attrs:
                    _, new_mprod = attrs["money_production"]
                    if new_mprod is not None:
                        old_val = province_production.get(pid, {}).get("MONEY", 0.0)
                        new_val = float(int(new_mprod))
                        province_production.setdefault(pid, {})["MONEY"] = new_val
                        owner = current_owners.get(pid, _UNOWNED)
                        if owner > _UNOWNED:
                            current_player_production[owner]["MONEY"] += (new_val - old_val)

                if "resource_production" in attrs:
                    _, new_rprod = attrs["resource_production"]
                    rtype = province_meta[pid]["resource_production_type"]
                    if new_rprod is not None and rtype:
                        old_val = province_production.get(pid, {}).get(rtype, 0.0)
                        new_val = float(int(new_rprod))
                        province_production.setdefault(pid, {})[rtype] = new_val
                        owner = current_owners.get(pid, _UNOWNED)
                        if owner > _UNOWNED:
                            current_player_production[owner][rtype] += (new_val - old_val)

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

            # Diplomacy — one event per tick when neighbor_relations changed;
            # extractor diffs old vs new to classify per-(sender, receiver) transitions.
            # Use .value comparisons: game state enums may come from a versioned module
            # (e.g. data_types.v210) while the extractor imports from data_types.newest —
            # different classes, so == fails even for identical members.
            _war_val = ForeignAffairRelationTypes.WAR.value
            _peace_val = ForeignAffairRelationTypes.PEACE.value
            _mutual_val = ForeignAffairRelationTypes.MUTUAL_PROTECTION.value
            _row_val = ForeignAffairRelationTypes.RIGHT_OF_WAY.value
            for fa_event in events.get(ReplayHookTag.ForeignAffairsRelationChanged, []):
                old_rel, new_rel = fa_event.attributes["neighbor_relations"]
                if old_rel is None or new_rel is None:
                    continue
                for s in set(old_rel) | set(new_rel):
                    prev_row = old_rel.get(s, {})
                    curr_row = new_rel.get(s, {})
                    for r in set(prev_row) | set(curr_row):
                        old_v = prev_row.get(r)
                        new_v = curr_row.get(r)
                        old_val = old_v.value if old_v is not None else _peace_val
                        new_val = new_v.value if new_v is not None else _peace_val
                        if old_val == new_val:
                            continue
                        sender_id = s + 1
                        if new_val == _war_val:
                            dp_wars[sender_id] += 1
                            game_wars += 1
                        elif old_val == _war_val and new_val >= _peace_val:
                            dp_peace[sender_id] += 1
                            game_peace += 1
                        if new_val == _mutual_val:
                            dp_alliances[sender_id] += 1
                            game_alliances += 1
                        elif old_val == _mutual_val:
                            dp_allianced[sender_id] += 1
                            game_allianced += 1
                        if new_val == _row_val:
                            dp_rows[sender_id] += 1
                            game_rows += 1

            # Snapshot player territory counts — O(players), not O(provinces)
            ct = replay.current_time
            pb = _pct_bucket((ct - start_time).total_seconds(), total_duration_seconds) if ct else 0
            db = _day_bucket((ct - start_time).total_seconds(), total_duration_seconds, game_days) if ct else 0

            # Integrate production over elapsed time and snapshot for averages/buckets
            if ct is not None:
                delta_days = (ct - prev_time).total_seconds() / 86400.0
                for player_id, rtypes in current_player_production.items():
                    for rtype, rprod in rtypes.items():
                        if rprod > 0:
                            player_total_prod[player_id][rtype] += rprod * delta_days
                prev_time = ct

            for player_id, rtypes in current_player_production.items():
                if not any(v > 0 for v in rtypes.values()):
                    continue
                player_prod_n[player_id] += 1
                for rtype, rprod in rtypes.items():
                    if rprod <= 0:
                        continue
                    player_prod_sum[player_id][rtype] += rprod
                    if rprod > player_peak_prod[player_id].get(rtype, 0.0):
                        player_peak_prod[player_id][rtype] = rprod
                    prod_pct_sum[player_id][rtype][pb] += rprod
                    prod_pct_n[player_id][rtype][pb] += 1
                    prod_day_sum[player_id][rtype][db] += rprod
                    prod_day_n[player_id][rtype][db] += 1

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
                pct_bucket_sum[player_id][pb] += cnt
                pct_bucket_n[player_id][pb] += 1
                day_bucket_sum[player_id][db] += cnt
                day_bucket_n[player_id][db] += 1

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
            n_prod = player_prod_n.get(player_id, 1)
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
                pct_buckets=_finalize_buckets(pct_bucket_sum[player_id], pct_bucket_n[player_id]),
                day_buckets=_finalize_buckets(day_bucket_sum[player_id], day_bucket_n[player_id]),
                wars_declared=dp_wars.get(player_id, 0),
                peace_treaties_signed=dp_peace.get(player_id, 0),
                alliances_formed=dp_alliances.get(player_id, 0),
                alliance_dissolutions=dp_allianced.get(player_id, 0),
                right_of_ways_signed=dp_rows.get(player_id, 0),
                avg_production_by_type={
                    rtype: player_prod_sum[player_id][rtype] / n_prod
                    for rtype in player_prod_sum.get(player_id, {})
                },
                total_production_by_type=dict(player_total_prod.get(player_id, {})),
                peak_production_by_type=dict(player_peak_prod.get(player_id, {})),
                production_pct_buckets={
                    rtype: _finalize_float_buckets(prod_pct_sum[player_id][rtype], prod_pct_n[player_id][rtype])
                    for rtype in prod_pct_sum.get(player_id, {})
                },
                production_day_buckets={
                    rtype: _finalize_float_buckets(prod_day_sum[player_id][rtype], prod_day_n[player_id][rtype])
                    for rtype in prod_day_sum.get(player_id, {})
                },
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

        game_total_prod: dict[str, float] = defaultdict(float)
        for player in players:
            for rtype, val in player.total_production_by_type.items():
                game_total_prod[rtype] += val

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
            total_wars_declared=game_wars,
            total_peace_treaties=game_peace,
            total_alliances_formed=game_alliances,
            total_alliance_dissolutions=game_allianced,
            total_right_of_ways=game_rows,
            game_total_production=dict(game_total_prod),
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
