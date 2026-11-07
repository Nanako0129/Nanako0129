//! Last-7-days token usage per model, as Syrtis's engine computes it.
//!
//! Prints tokscale-core's `ModelReport` as JSON (snake_case keys). Same window
//! as the upstream CLI's `--week`: today and the 6 days before it, local time.
//! Reads and writes the cache under TOKSCALE_CONFIG_DIR, which the caller
//! points at a copy (see update_readme.py).
//!
//! Not covered, unlike the Syrtis app: extra Claude accounts and Pi roots set
//! in Syrtis's settings, Cursor desktop sync files and the Cursor takeover
//! (the CLI's ~/.config/tokscale/cursor-cache is read as is), and an
//! OPENCODE_DB path from Syrtis's own environment. Those live in the app's
//! preferences or process, not in settings.json. settings.json `modelAliases`
//! is not applied either (empty on this Mac, 2026-11-08).

use chrono::{Duration, Local};
use tokscale_core::{get_model_report, scanner::ScannerSettings, GroupBy, ReportOptions};

/// Only `scanner.opencodeDbPaths`, as Syrtis takes it (tb_core_ffi
/// `user_scanner_settings`): extra and excluded scan paths belong to Syrtis's
/// root registry, so reading them from the file would scan other roots.
/// Paths are used as written: Syrtis expands relative and `~` entries, this
/// does not (the list is empty on this Mac, 2026-11-08).
fn scanner_settings(dir: &std::ffi::OsStr) -> ScannerSettings {
    let Ok(bytes) = std::fs::read(std::path::Path::new(dir).join("settings.json")) else {
        return ScannerSettings::default();
    };
    let paths = serde_json::from_slice::<serde_json::Value>(&bytes)
        .map_err(|e| e.to_string())
        .and_then(|v| match v.pointer("/scanner/opencodeDbPaths") {
            None => Ok(Vec::new()),
            Some(p) => serde_json::from_value(p.clone()).map_err(|e| e.to_string()),
        })
        .unwrap_or_else(|e| {
            eprintln!("syrtis-usage: settings.json opencodeDbPaths ignored: {e}");
            Vec::new()
        });
    ScannerSettings { opencode_db_paths: paths, ..Default::default() }
}

#[tokio::main(flavor = "current_thread")]
async fn main() {
    // Without it the engine falls back to the real ~/.config/tokscale and
    // writes Syrtis's cache, the cross-write this tool exists to avoid.
    let Some(dir) = std::env::var_os("TOKSCALE_CONFIG_DIR").filter(|d| !d.is_empty()) else {
        eprintln!("syrtis-usage: set TOKSCALE_CONFIG_DIR to a copy of the cache; update_readme.py does");
        std::process::exit(2);
    };
    let today = Local::now().date_naive();
    let options = ReportOptions {
        home_dir: None,
        use_env_roots: true,
        since: Some((today - Duration::days(6)).format("%Y-%m-%d").to_string()),
        until: Some(today.format("%Y-%m-%d").to_string()),
        group_by: GroupBy::Model,
        scanner_settings: scanner_settings(&dir),
        ..Default::default()
    };
    match get_model_report(options).await {
        Ok(report) => println!("{}", serde_json::to_string(&report).expect("serialize")),
        Err(e) => {
            eprintln!("syrtis-usage: {e}");
            std::process::exit(1);
        }
    }
}
