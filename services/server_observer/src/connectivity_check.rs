use reqwest::Client;
use std::collections::HashMap;
use std::sync::Mutex;
use std::time::{Duration, SystemTime};

pub const FALLBACK_GAME_SERVER_URL: &str = "https://www.conflictnations.com";
const INTERNET_CHECK_URL: &str = "https://1.1.1.1";
const CHECK_TIMEOUT: Duration = Duration::from_secs(10);

pub struct GameServerStatus {
    pub reachable: bool,
    pub last_checked: SystemTime,
}

pub struct GameServerStatusMap {
    statuses: Mutex<HashMap<String, GameServerStatus>>,
    ttl: Duration,
}

impl GameServerStatusMap {
    pub fn new() -> Self {
        Self {
            statuses: Mutex::new(HashMap::new()),
            ttl: Duration::from_secs(300),
        }
    }

    /// Returns `Some(reachable)` if a fresh cached entry exists, `None` if unknown or TTL expired.
    pub fn get(&self, addr: &str) -> Option<bool> {
        let statuses = self
            .statuses
            .lock()
            .unwrap_or_else(|p| p.into_inner());
        let status = statuses.get(addr)?;
        if status.last_checked.elapsed().unwrap_or(self.ttl) >= self.ttl {
            return None;
        }
        Some(status.reachable)
    }

    pub fn update(&self, addr: &str, reachable: bool) {
        let mut statuses = self
            .statuses
            .lock()
            .unwrap_or_else(|p| p.into_inner());
        statuses.insert(
            addr.to_string(),
            GameServerStatus {
                reachable,
                last_checked: SystemTime::now(),
            },
        );
    }
}

#[derive(Debug)]
pub enum NetworkDiagnosis {
    /// Proxy server is dead — cannot reach the internet through it.
    ProxyDead,
    /// Proxy is alive but the game server ecosystem is globally unreachable.
    GameServerDown,
    /// Proxy is alive and game servers are up, but this proxy blocks the target.
    ProxyBlockingTarget,
    /// All checks passed — error was likely transient.
    Transient,
}

/// Returns `true` when the error text is a SOCKS5 "connection not allowed by ruleset" reply,
/// meaning the proxy server itself is reachable but has a filtering rule blocking the destination.
pub fn is_socks5_ruleset_error(message: &str) -> bool {
    message.contains("0x02") || message.contains("Connection not allowed by ruleset")
}

pub(crate) async fn check_direct(url: &str) -> bool {
    let client = match Client::builder()
        .no_proxy()
        .timeout(CHECK_TIMEOUT)
        .build()
    {
        Ok(c) => c,
        Err(_) => return false,
    };
    client.head(url).send().await.is_ok()
}

async fn check_via_proxy(proxy_url: &str, target_url: &str) -> bool {
    let proxy = match reqwest::Proxy::all(proxy_url) {
        Ok(p) => p,
        Err(_) => return false,
    };
    let client = match Client::builder()
        .proxy(proxy)
        .timeout(CHECK_TIMEOUT)
        .build()
    {
        Ok(c) => c,
        Err(_) => return false,
    };
    client.head(target_url).send().await.is_ok()
}

/// Verifies that the given proxy can reach the internet and the game server.
/// Used to validate a candidate replacement proxy before committing it.
pub async fn proxy_passes_checks(proxy_url: &str, game_server_url: &str) -> bool {
    if !check_via_proxy(proxy_url, INTERNET_CHECK_URL).await {
        return false;
    }
    check_via_proxy(proxy_url, game_server_url).await
}

/// Diagnoses the cause of a `NetworkError` for a session.
///
/// `game_server_url`: the session's last known game server address, or `None` to fall back to
/// `FALLBACK_GAME_SERVER_URL` (conflictnations.com).
pub async fn diagnose(
    proxy_url: &str,
    game_server_url: Option<&str>,
    error_message: &str,
    status_map: &GameServerStatusMap,
) -> NetworkDiagnosis {
    let target = game_server_url.unwrap_or(FALLBACK_GAME_SERVER_URL);

    // Fast path: SOCKS5 ruleset error means proxy is up but blocking this target.
    if is_socks5_ruleset_error(error_message) {
        tracing::info!(
            proxy_url,
            target,
            "fast-path SOCKS5 ruleset error — proxy blocking target"
        );
        return NetworkDiagnosis::ProxyBlockingTarget;
    }

    // Check [1]: proxy → internet
    if !check_via_proxy(proxy_url, INTERNET_CHECK_URL).await {
        tracing::warn!(proxy_url, "connectivity [1] failed: proxy cannot reach internet");
        return NetworkDiagnosis::ProxyDead;
    }

    // Check [2]: direct → game server (use cache to avoid redundant checks)
    let game_server_up = match status_map.get(target) {
        Some(cached) => {
            tracing::debug!(target, cached, "connectivity [2] using cached game-server status");
            cached
        }
        None => {
            let reachable = check_direct(target).await;
            status_map.update(target, reachable);
            tracing::info!(target, reachable, "connectivity [2] direct game-server check");
            reachable
        }
    };

    if !game_server_up {
        tracing::warn!(target, "connectivity [2] failed: game server unreachable directly");
        return NetworkDiagnosis::GameServerDown;
    }

    // Check [3]: proxy → game server
    if !check_via_proxy(proxy_url, target).await {
        tracing::warn!(
            proxy_url,
            target,
            "connectivity [3] failed: proxy cannot reach game server"
        );
        return NetworkDiagnosis::ProxyBlockingTarget;
    }

    tracing::debug!(proxy_url, target, "all connectivity checks passed — transient error");
    NetworkDiagnosis::Transient
}
