import sqlite3

DB_FILE = "/config/api.db"


class KeyValueStore(dict):
    def __init__( self, invalidate_hours=24, readonly=True):
        self.invalidate_hours = invalidate_hours
        self.readonly = readonly
        if not readonly:
            self.conn = sqlite3.connect(DB_FILE)
            self.conn.execute("CREATE TABLE IF NOT EXISTS kv (key TEXT UNIQUE, value TEXT, updated_at TEXT)")
            self.conn.commit()
            self.conn.close()
    def __enter__(self):
        self.conn = sqlite3.connect(DB_FILE, uri=self.readonly)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.readonly:
            self.conn.commit()
        self.conn.close()
    def __contains__(self, key):
        return self.conn.execute(f"SELECT 1 FROM kv WHERE key = '{key}' AND updated_at >= DATETIME('now', '-{self.invalidate_hours} hours')").fetchone() is not None
    def __getitem__(self, key):
        item = self.conn.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
        return item[0] if item else None
    def __setitem__(self, key, value):
        self.conn.execute("REPLACE INTO kv (key, value, updated_at) VALUES (?,?, CURRENT_TIMESTAMP)", (key, value))
        self.conn.commit()
