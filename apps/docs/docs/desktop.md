---
id: desktop
title: Desktop Client
---

# Conlyse Desktop — Quick Start

The Conlyse Desktop is a GUI for analyzing Conflict of Nations replay files.
You do **not** need to run the full backend stack to use it — all you need is a `.conrp`
replay file and its matching static map file.

When the backend **is** running, the desktop gains additional capabilities: browsing games
discovered by the ServerObserver, managing the recording list, accessing the replay library,
downloading replay files directly from storage, and automatic static map fetching.

## What You Need

- Python 3.12
- OpenGL 3.3+ capable GPU (any modern discrete or integrated GPU qualifies)
- A `.conrp` replay file

## Installation

From the repository root:

```bash
pip install -e apps/desktop
```

This installs the `conlyse` package and all dependencies, including `conflict-interface`.

## What to Download

### Demo replay file

Download the sample replay from the [GitHub Releases page](https://github.com/zdox/Conlyse/releases/latest):

**`replay_10635767.conrp`** — game 10731064, player 0

Place it anywhere on your machine — you will point the file picker to it when loading.
For the steps below it is assumed you place it in `app_data/replays/` inside your working directory:

```
<working-dir>/
└── app_data/
    └── replays/
        └── replay_10635767.conrp
```

### Static map file

When the Conlyse API is running the app fetches static map files automatically. In
standalone mode (no API) you must provide the file manually.

Download from the [GitHub Releases page](https://github.com/zdox/Conlyse/releases/latest):

**`5652_28.bin`** — static map data for the demo game's scenario

Place it in `app_data/static_maps/` inside the same working directory as the replay:

```
<working-dir>/
└── app_data/
    ├── replays/
    │   └── replay_10635767.conrp
    └── static_maps/
        └── 5652_28.bin
```

## Running the App

`app_data/` is read and written relative to your **working directory** at launch time.
The app creates it automatically on first run. Launch from whichever directory you placed
the `app_data/replays/` folder in:

```bash
python -m conlyse
```

## Opening the Demo Replay

1. The app opens on the **Replay List** screen.
2. Click the **Local Games** tab.
3. Click the folder icon in the top-right corner (or use the keybinding shown in Settings)
   to open the file picker.
4. Navigate to `app_data/replays/` and select `replay_10635767.conrp`.
5. The replay appears in the list on the left. Select it, then click **Analyze**.

A spinner is shown while the replay loads. Once complete, the interactive map view opens.

## Exploring the Replay

### Map Views

Switch between map views using the toolbar buttons at the top of the map:

| View | Shows |
|------|-------|
| Political | Province ownership coloured by player |
| Terrain | Terrain types across the map |
| Resource | Resource distribution |

### Timeline

The timeline at the bottom of the map controls playback position:

- **Drag** the slider to jump to any moment in the game.
- **Step buttons** advance or rewind one game patch at a time.

### Dock Panels

Dockable panels are accessible from the sidebar on the right:

- **Game Info** — current game day, speed, and player count
- **Province Info** — details for the province under the cursor (click any province)
- **City List** — sortable table of all cities with ownership and morale

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `D` | Toggle the navigation drawer |
| `P` | Toggle the performance overlay |
| `F11` | Toggle fullscreen |
| Mouse scroll | Zoom in / out |
| Click + drag | Pan the map |

## Settings

Click the gear icon (top-right of the Replay List screen) to open Settings:

- **Theme** — Dark or Light
- **Graphics** — frame rate cap, anti-aliasing, MSAA samples
- **API** — base URL for the Conlyse backend (leave as default for standalone use)
- **Keybindings** — rebind any key action

---

For scripted replay analysis without the GUI see [Replay Analysis](./conflict-interface/replay-analysis).
