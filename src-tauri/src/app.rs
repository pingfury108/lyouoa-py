use super::store;

#[tauri::command]
pub async fn greet(name: &str) -> Result<String, String> {
    match store::init_store().await {
        Ok(s) => println!("init store: {:#?}", s),
        Err(e) => println!("init stroe: {:#?}", e),
    }
    match store::query().await {
        Ok(s) => println!("query: {:#?}", s),
        Err(e) => println!("query: {:#?}", e),
    }
    Ok(format!("Hello, {}! You've been greeted from Rust!", name))
}

#[tauri::command]
pub fn get_cookies(s: &str) -> String {
    println!("{}", s);
    s.to_string()
}
