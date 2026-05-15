# conflict-interface

A Python library providing programmatic access to [Conflict of Nations](https://www.conflictnations.com/) game state management, API interactions, and comprehensive replay functionality.

## Overview

`conflict-interface` is the core Python library for interacting with Conflict of Nations. It provides:

- **Game State Management**: Complete game state representation with type-safe data structures
- **Replay System**: Bidirectional replay recording and playback with efficient patch-based storage
- **API Wrapper**: Pythonic interface to Conflict of Nations API endpoints
- **Game Analysis**: Tools for analyzing game data, strategies, and state changes

## Installation

### From Source (library only)

If you only need the **Python library** (for example, to use `conflict-interface` as a dependency in another project), install it directly:

From the repository root:

```bash
pip install -e libs/conflict_interface
```

Or from within the library directory:

```bash
cd libs/conflict_interface
pip install -e .
```

## Quick Start

### Basic Game Interaction

```python
from conflict_interface.interface.hub_interface import HubInterface

# Login and join a game
hub = HubInterface()
hub.login("your_username", "your_password")
game = hub.join_game(game_id=12345)  # returns OnlineInterface

# Access game state
game_info = game.get_game_info_state()
print(f"Current game day: {game_info.day_of_game}")

# Build an upgrade in a city
city = game.get_province_by_name("Berlin")
arms_industry = game.get_upgrade_type_by_name_and_tier("Arms Industry", 1)
modable_upgrade = city.get_possible_upgrade(id=arms_industry.id)
if city.is_upgrade_buildable(modable_upgrade):
    city.build_upgrade(modable_upgrade)

# Mobilize a unit in a city
infantry = game.get_unit_type_by_name_and_tier("Motorized Infantry", 1)
city.mobilize_unit_by_id(infantry.id)

game.update()
```

### Working with Replays

```python
from conflict_interface.interface.replay_interface import ReplayInterface
from pathlib import Path

# Load a replay file (static_map_data maps map_id to the .bin file path)
replay = ReplayInterface(
    Path("my_game.conrp"),
    static_map_data={"5652_28": Path("5652_28.bin")},
)
replay.open()

# Navigate through time
timestamps = replay.get_timestamps()
replay.jump_to(timestamps[50])

# Access game state at any point in time
armies = replay.get_armies()
provinces = replay.game_state.states.map_state.map.provinces

replay.close()
```

## Package Structure

```
conflict_interface/
├── api/                    # API wrappers (game_api, hub_api)
├── data_types/             # Game state data structures
│   └── newest/            # Latest game state format
│       ├── map_state/     # Map and province data
│       ├── player_state/  # Player and team information
│       ├── army_state/    # Army and unit data
│       └── ...            # Other state modules
├── interface/              # Main interfaces
│   ├── game_interface.py  # Live game interaction
│   ├── replay_interface.py # Replay playback
│   └── hub_interface.py    # Hub API interaction
├── replay/                 # Replay system
│   ├── replay_builder.py  # Building replay files
│   ├── replay_patch.py    # Patch generation
│   └── ...                # Replay utilities
├── utils/                  # Utility modules
└── game_object/            # Game object parsing
```

## Key Features

### Game State Management

The library provides comprehensive type-safe data structures for all game state:

```python
from conflict_interface.interface.hub_interface import HubInterface

hub = HubInterface()
hub.login("your_username", "your_password")
game = hub.join_game(game_id=12345)

# Access typed game state
game_state = game.game_state
map_state = game_state.states.map_state
player_state = game_state.states.player_state

# Type-safe access to provinces, players, armies, etc.
province = next(iter(map_state.map.provinces.values()))
player = next(iter(player_state.players.values()))
```

### Replay System

Efficient bidirectional replay system with patch-based storage:

```python
from conflict_interface.interface.replay_interface import ReplayInterface
from pathlib import Path

replay = ReplayInterface(
    Path("replay.conrp"),
    static_map_data={"5652_28": Path("5652_28.bin")},
)
replay.open()

timestamps = replay.get_timestamps()

# Navigate through time
replay.jump_to_next_patch()      # Forward one step
replay.jump_to_previous_patch()  # Backward one step
replay.jump_to(timestamps[0])    # Jump to specific time

# Access state at any point
current_state = replay.game_state
replay.close()
```

### API Wrappers

Pythonic wrappers for Conflict of Nations APIs:

```python
from conflict_interface.interface.hub_interface import HubInterface

hub = HubInterface()
hub.login("your_username", "your_password")

# Browse available games
global_games = hub.get_global_games()
my_games = hub.get_my_games()

# Join as guest (read-only, no country selection required)
game = hub.join_game(game_id=12345, guest=True)
```

## Examples

See the `examples/` directory for comprehensive usage examples:

- `game_join.py` - Join a game session
- `start_of_game.py` - Inspect a fresh game's state
- `read_replay.py` - Load and navigate a replay file
- `replay_roundtrip.py` - Replay conversion verification tool
- `build_upgrade.py` - Build structures in a province
- `mobilize_unit.py` - Create military units
- `command_army.py` - Issue army commands
- `research.py` - Research technologies

## Development

### Building from Source

The library includes C++ extensions that need to be compiled:

```bash
cd libs/conflict_interface
pip install -e ".[dev]"  # Installs pybind11
pip install -e .         # Builds C++ extensions
```

By default, builds use portable optimization flags so wheels can be built across architectures (including macOS universal2).
If you want host-specific CPU tuning for local non-macOS builds, set `CONFLICT_INTERFACE_NATIVE_OPT=1` before install.

### Running Tests

```bash
cd libs/conflict_interface
python tests/run_tests.py
```


## Dependencies

Core dependencies:
- `requests` - HTTP client
- `numpy` - Numerical operations
- `shapely` - Geometric operations
- `msgpack`, `zstandard`, `lz4` - Compression
- `msgspec` - Fast serialization
- `pybind11` - C++ bindings

See `pyproject.toml` for the complete list.


## Authors

- zDox
- NikNam3

## Links

- **GitHub**: https://github.com/zDox/ConflictInterface
- **Documentation**: https://conflict-interface.readthedocs.io/
- **Game Website**: https://www.conflictnations.com/
