use std::collections::{HashMap, HashSet};
use std::sync::Mutex;

/// Tracks which game-server addresses are currently known-down and which
/// game sessions are frozen waiting for them to recover.
///
/// When a connectivity diagnosis returns `GameServerDown` for a specific
/// address (e.g. `congs16.c.bytro.com`), the circuit for that address is
/// opened. All sessions on that address are frozen — their retry budgets are
/// not decremented — until the recovery probe finds the server reachable again.
pub struct ServerOutageTracker {
    /// address → set of frozen game_ids
    down_servers: Mutex<HashMap<String, HashSet<i32>>>,
}

impl ServerOutageTracker {
    pub fn new() -> Self {
        Self {
            down_servers: Mutex::new(HashMap::new()),
        }
    }

    /// Returns `true` if `addr` currently has an open circuit.
    pub fn is_down(&self, addr: &str) -> bool {
        self.down_servers
            .lock()
            .unwrap_or_else(|p| {
                tracing::error!("outage tracker mutex poisoned; recovering");
                p.into_inner()
            })
            .contains_key(addr)
    }

    /// Opens the circuit for `addr` and records `game_id` as the first frozen session.
    ///
    /// Returns `true` if this was the first time `addr` was added (newly opened circuit),
    /// `false` if it was already open (duplicate open for same address).
    pub fn open(&self, addr: &str, game_id: i32) -> bool {
        let mut map = self
            .down_servers
            .lock()
            .unwrap_or_else(|p| {
                tracing::error!("outage tracker mutex poisoned; recovering");
                p.into_inner()
            });
        let newly_opened = !map.contains_key(addr);
        map.entry(addr.to_string()).or_default().insert(game_id);
        newly_opened
    }

    /// Adds `game_id` to the frozen set of an already-open circuit for `addr`.
    /// No-ops if `addr` is not currently down.
    pub fn freeze(&self, addr: &str, game_id: i32) {
        let mut map = self
            .down_servers
            .lock()
            .unwrap_or_else(|p| {
                tracing::error!("outage tracker mutex poisoned; recovering");
                p.into_inner()
            });
        if let Some(set) = map.get_mut(addr) {
            set.insert(game_id);
        }
    }

    /// Closes the circuit for `addr` and returns the full set of frozen game_ids.
    /// Returns an empty set if `addr` was not tracked.
    pub fn close(&self, addr: &str) -> HashSet<i32> {
        self.down_servers
            .lock()
            .unwrap_or_else(|p| {
                tracing::error!("outage tracker mutex poisoned; recovering");
                p.into_inner()
            })
            .remove(addr)
            .unwrap_or_default()
    }

    /// Returns all currently-down server addresses. Used by the recovery probe.
    pub fn down_addresses(&self) -> Vec<String> {
        self.down_servers
            .lock()
            .unwrap_or_else(|p| {
                tracing::error!("outage tracker mutex poisoned; recovering");
                p.into_inner()
            })
            .keys()
            .cloned()
            .collect()
    }

    /// Returns the number of currently-down server addresses.
    pub fn down_count(&self) -> i64 {
        self.down_servers
            .lock()
            .unwrap_or_else(|p| {
                tracing::error!("outage tracker mutex poisoned; recovering");
                p.into_inner()
            })
            .len() as i64
    }
}
