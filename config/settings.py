import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    # LINE Bot Configuration
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "").strip()
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    
    # Shopee Configuration
    SHOPEE_PARTNER_ID = int(os.getenv("SHOPEE_PARTNER_ID", 0))
    SHOPEE_PARTNER_KEY = os.getenv("SHOPEE_PARTNER_KEY", "").strip()
    SHOP_ID = os.getenv("SHOP_ID", "").strip()
    COUNTRY = os.getenv("COUNTRY", "SG").strip()
    TUNNEL_URL = os.getenv("TUNNEL_URL", "https://shopee.lemargue.com").strip()
    
    # API Configuration
    SHOPEE_HOST = "https://openplatform.sandbox.test-stable.shopee.sg"
    
    # Database Configuration
    DB_PATH = BASE_DIR / "cache.db"
    
    # AI Configuration
    OPENAI_MODEL = "gpt-4o-mini"  # Cost-effective model
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7

settings = Settings()
