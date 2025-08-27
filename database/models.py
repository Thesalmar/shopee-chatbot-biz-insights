import sqlite3
from pathlib import Path
from config.settings import settings

class Database:
    def __init__(self):
        self.db_path = settings.DB_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS handoff(user_id TEXT PRIMARY KEY, open BOOLEAN DEFAULT FALSE);
            CREATE TABLE IF NOT EXISTS tokens(shop_id TEXT PRIMARY KEY, access_token TEXT, refresh_token TEXT);
            CREATE TABLE IF NOT EXISTS seller_queries(id INTEGER PRIMARY KEY, user_id TEXT, query TEXT, response TEXT, timestamp INTEGER);
            CREATE TABLE IF NOT EXISTS business_insights(id INTEGER PRIMARY KEY, insight_type TEXT, data TEXT, created_at INTEGER);
            CREATE TABLE IF NOT EXISTS chat_history(id INTEGER PRIMARY KEY, user_id TEXT, message TEXT, response TEXT, timestamp INTEGER);
        """)
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def save_chat_history(self, user_id: str, message: str, response: str, timestamp: int):
        """Save chat history"""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO chat_history(user_id, message, response, timestamp) VALUES(?,?,?,?)",
                (user_id, message, response, timestamp)
            )
            conn.commit()
    
    def get_chat_history(self, user_id: str, limit: int = 10):
        """Get recent chat history for context"""
        with self.get_connection() as conn:
            result = conn.execute(
                "SELECT message, response FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            return [(msg, resp) for msg, resp in reversed(result)]
    
    def save_seller_query(self, user_id: str, query: str, response: str, timestamp: int):
        """Save seller query"""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO seller_queries(user_id, query, response, timestamp) VALUES(?,?,?,?)",
                (user_id, query, response, timestamp)
            )
            conn.commit()
    
    def get_access_token(self, shop_id: str):
        """Get access token for shop"""
        with self.get_connection() as conn:
            result = conn.execute("SELECT access_token FROM tokens WHERE shop_id = ?", (shop_id,)).fetchone()
            return result[0] if result else None
    
    def save_tokens(self, shop_id: str, access_token: str, refresh_token: str = ""):
        """Save access tokens"""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tokens(shop_id, access_token, refresh_token) VALUES(?,?,?)",
                (shop_id, access_token, refresh_token)
            )
            conn.commit()

# Global database instance
db = Database()
