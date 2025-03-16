import sqlite3
from datetime import datetime

DB_PATH = "db.sqlite"

def init_db():
    """Initialize the database with test users and messages."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 创建 Users 表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT 0
    );
    """)

    # 创建 Messages 表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 创建 Files 表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 插入用户数据（包括 1 个管理员）
    users = [
        ("admin", "admin123", True),
        ("alice", "password1", False),
        ("bob", "password2", False),
        ("charlie", "password3", False),
        ("dave", "password4", False),
        ("eve", "password5", False),
        ("frank", "password6", False),
        ("grace", "password7", False),
        ("heidi", "password8", False),
        ("ivan", "password9", False)
    ]

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:  # 仅当用户表为空时插入
        cursor.executemany("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", users)
        print("[+] Users added to the database.")

    # 获取所有用户 ID
    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]

    # 插入聊天消息
    messages = [
        (user_ids[1], "Hello everyone!"),
        (user_ids[2], "Hey Alice, how are you?"),
        (user_ids[3], "This Flask app is cool!"),
        (user_ids[4], "I love working on security projects."),
        (user_ids[5], "Anyone up for a code review?"),
        (user_ids[6], "Let's fix those SQL injections!"),
        (user_ids[7], "How do I hash passwords correctly?"),
        (user_ids[8], "Check out this new XSS exploit!"),
        (user_ids[9], "Flask sessions can be hijacked!"),
        (user_ids[0], "Admin: Please follow security guidelines.")
    ]

    cursor.execute("SELECT COUNT(*) FROM messages")
    if cursor.fetchone()[0] == 0:  # 仅当消息表为空时插入
        cursor.executemany("INSERT INTO messages (user_id, content) VALUES (?, ?)", messages)
        print("[+] Messages added to the database.")

    # 提交更改并关闭数据库连接
    conn.commit()
    conn.close()
    print("[✅] Database initialized successfully!")

if __name__ == "__main__":
    init_db()