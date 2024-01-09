// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
mod app;
mod sdk;
mod store;

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![app::greet, app::get_cookies])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
