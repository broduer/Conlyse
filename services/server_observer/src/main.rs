mod account_pool;
mod db;
mod game_finder;
mod hub_interface_wrapper;
mod metrics;
mod observation_api;
mod observation_package;
mod observation_session;
mod response_metadata;
mod recording_registry;
mod recording_storage;
mod redis_publisher;
mod s3_client;
mod scheduler;
mod server_observer;
mod static_map_cache;

use crate::hub_interface_wrapper::HubInterfaceWrapper;
use crate::metrics::MetricsServer;
use crate::server_observer::ServerObserver;
use config::{Config, File, FileFormat};
use std::env;
use std::sync::Arc;
use tokio::signal;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter, Layer};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let log_dir = env::var("LOG_DIR").unwrap_or_else(|_| "logs".to_string());
    let file_appender = tracing_appender::rolling::daily(&log_dir, "server_observer.log");
    let (non_blocking, _guard) = tracing_appender::non_blocking(file_appender);

    let file_layer = tracing_subscriber::fmt::layer()
        .json()
        .with_writer(non_blocking)
        .with_filter(EnvFilter::new("info"));

    let stdout_layer = tracing_subscriber::fmt::layer()
        .with_writer(std::io::stdout)
        .with_filter(EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info")));

    tracing_subscriber::registry()
        .with(file_layer)
        .with(stdout_layer)
        .init();

    let args: Vec<String> = env::args().collect();

    // CLI contract:
    //   arg1 (optional): path to TOML config file. Defaults to "config.toml".
    //   arg2 (optional): path to account_pool.json. Defaults to "account_pool.json".
    let config_file = args
        .get(1)
        .cloned()
        .unwrap_or_else(|| "config.toml".to_string());
    let account_pool_file = args
        .get(2)
        .cloned()
        .unwrap_or_else(|| "account_pool.json".to_string());

    tracing::info!(
        config_file = %config_file,
        account_pool_file = %account_pool_file,
        "starting server_observer process"
    );

    let settings = Config::builder()
        .add_source(File::new(&config_file, FileFormat::Toml))
        .build()?;

    let _metrics_server = match settings.get::<u16>("metrics_port") {
        Ok(port_u16) => {
            tracing::info!(metrics_port = port_u16, "metrics server enabled");
            Some(MetricsServer::run(port_u16).await?)
        }
        Err(_) => {
            tracing::info!("metrics server disabled");
            None
        }
    };

    let webshare_token = settings.get::<String>("webshare_api_token")?;

    let account_pool =
        account_pool::AccountPool::load_from_file(&account_pool_file, webshare_token).await?;
    let account_pool = Arc::new(tokio::sync::Mutex::new(account_pool));

    let observer = ServerObserver::new(&settings, Arc::clone(&account_pool)).await?;
    let mut run_task = {
        let observer = Arc::clone(&observer);
        tokio::spawn(async move { observer.run().await })
    };

    tokio::select! {
        _ = signal::ctrl_c() => {
            tracing::info!("Shutdown signal received, stopping observer...");
            observer.stop().await;
        }
        result = &mut run_task => {
            match result {
                Ok(success) => {
                    tracing::info!(success = success, "observer loop exited");
                }
                Err(err) => {
                    tracing::error!(?err, "observer task failed");
                }
            }
            HubInterfaceWrapper::shutdown_python();
            return Ok(());
        }
    }

    let _ = run_task.await;

    HubInterfaceWrapper::shutdown_python();
    Ok(())
}
