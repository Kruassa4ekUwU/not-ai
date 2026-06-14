import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "bot.db")


class Database:
    def __init__(self):
        self.path = DB_PATH

    def init(self):
        with sqlite3.connect(self.path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    chat_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_message(self, text: str, chat_id: int):
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT INTO messages (text, chat_id) VALUES (?, ?)",
                (text, chat_id)
            )
            conn.commit()

    def get_all_messages(self) -> list:
        with sqlite3.connect(self.path) as conn:
            rows = conn.execute("SELECT text FROM messages").fetchall()
        return [r[0] for r in rows]

    def get_message_count(self) -> int:
        with sqlite3.connect(self.path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        return count
