---
id: replay-analysis
title: Replay Analysis
sidebar_position: 3
---

# Replay Analysis

`ReplayInterface` lets you load a `.conrp` replay file and inspect the full game state at any point in time. It exposes the same query methods as `OnlineInterface` — `get_armies()`, `get_provinces()`, `get_players()`, etc. — but instead of talking to a live server, it reconstructs state by applying recorded patches.

## What You Need

- A `.conrp` replay file (produced by the Conlyse ServerConverter pipeline)
- A `.bin` static map data file for the map used in that game

If you don't know which map IDs a replay uses, open it in `read_metadata` mode first (see below).

## Opening a Replay

### Full mode

```python
from conflict_interface.interface.replay_interface import ReplayInterface
from pathlib import Path

replay = ReplayInterface(
    Path("game_12345.conrp"),
    static_map_data={"5652_28": Path("5652_28.bin")},
)
replay.open()

# ... work with the replay ...

replay.close()
```

The `static_map_data` argument maps each `map_id` string to the path of its `.bin` file. `open()` raises `ValueError` if a required map ID has no corresponding file.

### Metadata-only mode

Use this to inspect a replay's metadata without loading the full game state — useful for discovering which map files you need:

```python
replay = ReplayInterface(Path("game_12345.conrp"))
replay.open(mode='read_metadata')

print(replay.get_required_map_ids())    # e.g. {"5652_28"}
meta = replay.get_timeline_metadata()
print(meta.game_id, meta.day_of_game, meta.game_ended)

replay.close()
```

Always call `replay.close()` when finished. Use a `try/finally` block to guarantee cleanup:

```python
try:
    replay.open()
    # ...
finally:
    replay.close()
```

## Replay Metadata

Before navigating, you can inspect what the replay contains:

```python
# Timeline-level (whole file)
meta = replay.get_timeline_metadata()
# Fields: game_id, player_id, scenario_id, day_of_game, game_ended,
#         start_of_game, end_of_game, speed, segment_count

# Per-segment info
segs = replay.get_segments_metadata()
for seg_id, seg_meta in segs.items():
    print(seg_meta.version, seg_meta.map_id, seg_meta.current_patches)

print(f"Total patches: {replay.get_total_patches()}")
print(f"Map versions used: {replay.get_required_versions()}")
```

## Navigating Time

After `open()`, the replay is positioned at the start. All navigation calls update `replay.current_time` and rebuild `replay.game_state`.

### Timestamps

```python
timestamps = replay.get_timestamps()   # list[datetime], sorted ascending
print(replay.start_time)               # datetime — first timestamp
print(replay.last_time)                # datetime — last timestamp
print(replay.current_time)             # datetime — current position
```

### Jumping to a specific time

```python
replay.jump_to(timestamps[50])         # arbitrary timestamp
replay.jump_to(replay.last_time)       # shortcut: go to end
replay.jump_to_last_time()             # same as above
```

`jump_to()` uses Dijkstra over the patch graph and automatically creates consolidated "long patches" for large jumps to keep performance consistent.

### Step-by-step traversal

`jump_to_next_patch()` and `jump_to_previous_patch()` are O(1) and ideal for iterating through the entire replay:

```python
while replay.jump_to_next_patch():
    # replay.game_state and current_time are updated
    pass
```

Both methods return `False` when the boundary (start or end) is reached.

### Peeking at adjacent timestamps

```python
nxt  = replay.get_next_timestamp()     # datetime | None — doesn't move
prev = replay.get_previous_timestamp() # datetime | None — doesn't move
```

## Querying State

After any `jump_to*` call, all `GameInterface` query methods work identically to live games:

```python
replay.jump_to(timestamps[100])

# Provinces
provs = replay.get_provinces()
city  = replay.get_province_by_name("Berlin")

# Armies
armies    = replay.get_armies()
my_armies = replay.get_my_armies()   # filtered by replay's player_id

# Players
players = replay.get_players()
me      = replay.get_my_player()

# Game info
info = replay.get_game_info_state()
print(info.day_of_game)

# Resources, research, foreign affairs, etc.
amounts = replay.get_my_resource_amounts()
```

Direct access to the raw state tree is also available:

```python
state = replay.game_state.states
provinces = state.map_state.map.provinces
armies    = state.army_state.armies
```

## Event / Hook System

Rather than polling every field after each step, you can register hooks that fire automatically when specific attributes change. This is the efficient way to build analysis pipelines.

### Trigger-based hooks (poll after each step)

Register a trigger once, then step through the replay and poll accumulated events:

```python
from conflict_interface.hook_system.replay_hook_tag import ReplayHookTag

# Watch specific attributes
replay.register_province_trigger(attributes=["owner_id", "morale"])
replay.register_player_trigger(attributes=["defeated"])
replay.register_army_trigger()         # watch all army attributes
replay.register_game_info_trigger(attributes=["day_of_game"])

while replay.jump_to_next_patch():
    events = replay.poll_events()  # dict[ReplayHookTag, list[ReplayHookEvent]]

    for event in events.get(ReplayHookTag.ProvinceChanged, []):
        province = event.reference       # LandProvince object
        changes  = event.attributes      # {"owner_id": (old, new), ...}
        if "owner_id" in changes:
            old, new = changes["owner_id"]
            print(f"Day {replay.game_day()}: {province.name} flipped {old} → {new}")

    for event in events.get(ReplayHookTag.PlayerChanged, []):
        player = event.reference
        if "defeated" in event.attributes:
            print(f"{player.nation_name} was eliminated")
```

`poll_events()` clears the queue — call it once per step.

### Callback-style hooks (fire inline)

For code that should run immediately when a change occurs:

```python
def on_province_captured(province, changes):
    old_owner, new_owner = changes["owner_id"]
    print(f"{province.name}: {old_owner} → {new_owner}")

replay.on_province_attribute_change(
    callback=on_province_captured,
    attributes=["owner_id"],
)

# Callbacks fire automatically during each jump
replay.jump_to(replay.last_time)

# Remove when done
replay.remove_province_attribute_change_callback(on_province_captured)
```

### ReplayHookEvent fields

| Field | Type | Description |
|---|---|---|
| `tag` | `ReplayHookTag` | Which category changed |
| `reference` | object | The changed object (e.g. `LandProvince`, `Army`) |
| `attributes` | `dict[str, tuple]` | `{"field": (old_value, new_value)}` for each changed attribute |

### ReplayHookTag values

| Tag | Fired when |
|---|---|
| `ProvinceChanged` | A province attribute changed |
| `PlayerChanged` | A player attribute changed |
| `TeamChanged` | A team attribute changed |
| `ArmyChanged` | An army attribute changed |
| `GameInfoChanged` | A game-info attribute changed (e.g. day advanced) |
| `SegmentSwitch` | Playback crossed into a new replay segment |

### Cleanup

```python
replay.unregister_province_trigger()
replay.unregister_army_trigger()
replay.unregister_player_trigger()
replay.unregister_team_trigger()
replay.unregister_game_info_trigger()

# Or remove everything at once:
replay.unregister_all_hooks()
```

## Full Example: Ownership History

```python
from conflict_interface.interface.replay_interface import ReplayInterface
from conflict_interface.hook_system.replay_hook_tag import ReplayHookTag
from pathlib import Path
from collections import defaultdict

replay = ReplayInterface(
    Path("game_12345.conrp"),
    static_map_data={"5652_28": Path("5652_28.bin")},
)
replay.open()
replay.register_province_trigger(attributes=["owner_id"])

ownership_changes = defaultdict(list)

while replay.jump_to_next_patch():
    events = replay.poll_events()
    for event in events.get(ReplayHookTag.ProvinceChanged, []):
        if "owner_id" in event.attributes:
            province = event.reference
            old, new = event.attributes["owner_id"]
            ownership_changes[province.name].append({
                "time": replay.current_time,
                "day":  replay.game_day(),
                "from": old,
                "to":   new,
            })

replay.close()

for name, changes in ownership_changes.items():
    print(f"\n{name}: {len(changes)} ownership change(s)")
    for c in changes:
        print(f"  Day {c['day']}: player {c['from']} → {c['to']}")
```
