import sqlite3
from pathlib import Path
from config.settings import settings

class Database:
    def __init__(self):
        self.db_path = settings.DB_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize database tables with production support"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        # Check if tables exist and handle schema updates
        cursor = conn.cursor()
        
        # Tokens table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                shop_id TEXT PRIMARY KEY,
                access_token TEXT NOT NULL,
                refresh_token TEXT,
                country_code TEXT DEFAULT 'SG',
                created_at INTEGER DEFAULT (strftime('%s', 'now')),
                updated_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        # Chat history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                country_code TEXT DEFAULT 'SG',
                timestamp INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        # Business insights table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shop_id TEXT,
                insight_type TEXT NOT NULL,
                data TEXT NOT NULL,
                country_code TEXT DEFAULT 'SG',
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        # Seller queries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seller_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                country_code TEXT DEFAULT 'SG',
                timestamp INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        # System configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_history_user_timestamp ON chat_history(user_id, timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_country ON tokens(country_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_business_insights_shop_country ON business_insights(shop_id, country_code)")
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def save_chat_history(self, user_id: str, message: str, response: str, country_code: str = "SG"):
        """Save chat history with country support"""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO chat_history(user_id, message, response, country_code, timestamp) VALUES(?,?,?,?,?)",
                (user_id, message, response, country_code, int(time.time()))
            )
            conn.commit()
    
    def get_chat_history(self, user_id: str, country_code: str = "SG", limit: int = 10):
        """Get recent chat history for context with country filtering"""
        with self.get_connection() as conn:
            result = conn.execute(
                """SELECT message, response FROM chat_history 
                   WHERE user_id = ? AND country_code = ? 
                   ORDER BY timestamp DESC LIMIT ?""",
                (user_id, country_code, limit)
            ).fetchall()
            return [(msg, resp) for msg, resp in reversed(result)]
    
    def save_seller_query(self, user_id: str, query: str, response: str, country_code: str = "SG"):
        """Save seller query with country support"""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO seller_queries(user_id, query, response, country_code, timestamp) VALUES(?,?,?,?,?)",
                (user_id, query, response, country_code, int(time.time()))
            )
            conn.commit()
    
    def save_business_insight(self, shop_id: str, insight_type: str, data: str, country_code: str = "SG"):
        """Save business insights with country support"""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO business_insights(shop_id, insight_type, data, country_code, created_at) VALUES(?,?,?,?,?)",
                (shop_id, insight_type, data, country_code, int(time.time()))
            )
            conn.commit()
    
    def get_business_insights(self, shop_id: str, country_code: str = "SG", limit: int = 50):
        """Get business insights with country filtering"""
        with self.get_connection() as conn:
            result = conn.execute(
                """SELECT insight_type, data, created_at FROM business_insights 
                   WHERE shop_id = ? AND country_code = ? 
                   ORDER BY created_at DESC LIMIT ?""",
                (shop_id, country_code, limit)
            ).fetchall()
            return [(insight_type, data, created_at) for insight_type, data, created_at in result]
    
    def get_access_token(self, shop_id: str, country_code: str = "SG"):
        """Get access token for shop with country support"""
        with self.get_connection() as conn:
            result = conn.execute(
                "SELECT access_token FROM tokens WHERE shop_id = ? AND country_code = ?",
                (shop_id, country_code)
            ).fetchone()
            return result[0] if result else None
    
    def save_tokens(self, shop_id: str, access_token: str, refresh_token: str = "", country_code: str = "SG"):
        """Save access tokens with country support"""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tokens(shop_id, access_token, refresh_token, country_code, updated_at) VALUES(?,?,?,?,?)",
                (shop_id, access_token, refresh_token, country_code, int(time.time()))
            )
            conn.commit()
    
    def get_tokens_by_country(self, country_code: str = "SG"):
        """Get all tokens for a specific country"""
        with self.get_connection() as conn:
            result = conn.execute(
                "SELECT shop_id, access_token, refresh_token FROM tokens WHERE country_code = ?",
                (country_code,)
            ).fetchall()
            return [(shop_id, access_token, refresh_token) for shop_id, access_token, refresh_token in result]
    
    def get_system_config(self, key: str):
        """Get system configuration value"""
        with self.get_connection() as conn:
            result = conn.execute("SELECT value FROM system_config WHERE key = ?", (key,)).fetchone()
            return result[0] if result else None
    
    def set_system_config(self, key: str, value: str):
        """Set system configuration value"""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO system_config(key, value, updated_at) VALUES(?,?,?)",
                (key, value, int(time.time()))
            )
            conn.commit()

# Global database instance
import time
db = Database()
