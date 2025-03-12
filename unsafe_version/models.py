import sqlite3

DB_PATH = "db.sqlite"  # SQLite database path

def get_db_connection():
    """Establish a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access to query results
    return conn

def init_db():
    """Create database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,  -- ❌ Plaintext password storage, needs to be fixed later
            is_admin INTEGER DEFAULT 0  -- 0 = regular user, 1 = admin
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,  -- ❌ XSS vulnerability
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()