---
id: getting-started
title: Getting Started
sidebar_position: 1
---

# Getting Started with conflict-interface

`conflict-interface` is a Python library for interacting with [Conflict of Nations](https://www.conflictnations.com/) programmatically. It has two primary use cases:

- **Live game interaction** — authenticate, join a game, read its state, and perform actions (build, mobilize, command armies, research, trade).
- **Replay analysis** — load a recorded `.conrp` replay file and navigate through game state at any point in time.

## Prerequisites

- Python == 3.12
- For **live games**: a Conflict of Nations account
- For **replays**: a `.conrp` replay file and the matching `.bin` static map data file for that game's map

## Installation

From the repository root:

```bash
pip install -e libs/conflict_interface
```

To also compile the optional C++ extensions (required for the full replay system):

```bash
pip install -e "libs/conflict_interface[dev]"  # installs pybind11
pip install -e libs/conflict_interface          # builds extensions
```

## Interface Hierarchy

All three interfaces share a common base that provides game state queries:

```
GameInterface          ← shared query methods (provinces, armies, players, …)
├── OnlineInterface    ← live games: actions, update(), server communication
└── ReplayInterface    ← replay files: time travel, hook system
```

You never instantiate `GameInterface` directly. Instead:

- Use **`HubInterface`** to authenticate and then call `hub.join_game()`, which returns an **`OnlineInterface`**.
- Instantiate **`ReplayInterface`** directly with a file path.

## Quick Example: Live Game

```python
from conflict_interface.interface.hub_interface import HubInterface

hub = HubInterface()
hub.login("your_username", "your_password")

# Join as a guest — read-only, no country selection needed
game = hub.join_game(game_id=12345, guest=True)

info = game.get_game_info_state()
print(f"Day {info.day_of_game} — {len(game.get_players())} players")

province = next(iter(game.get_land_provinces().values()))
print(f"First province: {province.name} (owner {province.owner_id})")
```

## Quick Example: Replay Analysis

```python
from conflict_interface.interface.replay_interface import ReplayInterface
from pathlib import Path

replay = ReplayInterface(
    Path("game_12345.conrp"),
    static_map_data={"5652_28": Path("5652_28.bin")},
)
replay.open()

print(f"Replay spans {replay.start_time} → {replay.last_time}")
print(f"Total patches: {replay.get_total_patches()}")

replay.jump_to(replay.last_time)
armies = replay.get_armies()
print(f"Armies at game end: {len(armies)}")

replay.close()
```

## Next Steps

- [Live Games](./live-games) — authentication, game discovery, querying state, performing actions
- [Replay Analysis](./replay-analysis) — opening replays, time navigation, the event/hook system
