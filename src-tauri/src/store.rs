use anyhow::Result;
use sqlx::SqlitePool;

const DATABASE_URL: &str = "sqlite://db.sqlite?mode=rwc";

pub async fn init_store() -> Result<()> {
    let conn = SqlitePool::connect(DATABASE_URL).await?;
    sqlx::migrate!("./migrations").run(&conn).await?;
    Ok(())
}

pub async fn query() -> Result<()> {
    let conn = SqlitePool::connect(DATABASE_URL).await?;

    let r = sqlx::query("SELECT * FROM orders").execute(&conn).await?;

    println!("{:#?}", r);
    Ok(())
}
