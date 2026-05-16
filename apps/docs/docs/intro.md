---
sidebar_position: 0
---

# Conlyse Documentation

Conlyse is an unofficial full-stack system for recording, storing, and analyzing Conflict of Nations games.
It consists of an end-to-end replay pipeline (Observer → Converter → storage → API) plus the `ConflictInterface` library that powers time-travel replay playback.

## Where to start
:::tip Using the ConflictInterface library
Install the library and load your first replay or connect to a live game — start with **[Getting Started](./conflict-interface/getting-started)**.
:::

:::tip Deploying the full stack
Run Observer, Converter, API, and storage in one command with Docker Compose — start with the **[Deployment](./deployment)** guide.
:::

:::tip Using the Desktop Client
Analyze replay files interactively with the map viewer, timeline, and dock panels — start with the **[Desktop Client](./desktop)** guide.
:::

:::tip Learning how a service works
- [Server Observer](./server-observer) — captures live game state and publishes it to Redis
- [Server Converter](./server-converter) — processes responses into `.conrp` replay files
:::

:::tip Digging into internals
- [Replay System](./conflict-interface/replay-system) — patch-based format, bidirectional time-travel playback
- [Data Types](./conflict-interface/data-types) — type-safe game state objects
:::