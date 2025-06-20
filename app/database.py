import sqlite3

class SQLiteDB:
    def __init__(self, db_path="insights.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_table()

    def _init_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                method TEXT,
                keywords TEXT,
                embedding BLOB,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

    def insert(self, url, method, keywords, embedding):
        self.conn.execute(
            "INSERT INTO insights (url, method, keywords, embedding) VALUES (?, ?, ?, ?)",
            (url, method, ",".join(keywords), embedding.tobytes())
        )
        self.conn.commit()

    def fetch_by_id(self, idx):
        return self.conn.execute("SELECT url, method, keywords FROM insights WHERE id=?", (idx + 1,)).fetchone()
