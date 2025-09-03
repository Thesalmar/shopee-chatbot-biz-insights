import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    # LINE Bot Configuration
    LINE_CHANNEL_ID = os.getenv("LINE_CHANNEL_ID", "").strip()
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "").strip()
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    
    # Execution Mode
    EXECUTION_MODE = os.getenv("EXECUTION_MODE", "TEST").strip().upper()
    
    # Shopee Configuration (Test)
    TEST_SHOPEE_PARTNER_ID = int(os.getenv("TEST_SHOPEE_PARTNER_ID", 0))
    TEST_SHOPEE_PARTNER_KEY = os.getenv("TEST_SHOPEE_PARTNER_KEY", "").strip()
    
    # Shopee Configuration (Live)
    LIVE_SHOPEE_PARTNER_ID = int(os.getenv("LIVE_SHOPEE_PARTNER_ID", 0))
    LIVE_SHOPEE_PARTNER_KEY = os.getenv("LIVE_SHOPEE_PARTNER_KEY", "").strip()
    
    # Shop IDs by country (Test)
    TEST_SHOP_ID_SG = os.getenv("TEST_SHOP_ID_SG", "").strip()
    TEST_SHOP_ID_MY = os.getenv("TEST_SHOP_ID_MY", "").strip()
    TEST_SHOP_ID_PH = os.getenv("TEST_SHOP_ID_PH", "").strip()
    TEST_SHOP_ID_TH = os.getenv("TEST_SHOP_ID_TH", "").strip()
    TEST_SHOP_ID_TW = os.getenv("TEST_SHOP_ID_TW", "").strip()
    TEST_SHOP_ID_VN = os.getenv("TEST_SHOP_ID_VN", "").strip()
    
    # Shop IDs by country (Live)
    LIVE_SHOP_ID_SG = os.getenv("LIVE_SHOP_ID_SG", "").strip()
    LIVE_SHOP_ID_MY = os.getenv("LIVE_SHOP_ID_MY", "").strip()
    LIVE_SHOP_ID_PH = os.getenv("LIVE_SHOP_ID_PH", "").strip()
    LIVE_SHOP_ID_TH = os.getenv("LIVE_SHOP_ID_TH", "").strip()
    LIVE_SHOP_ID_TW = os.getenv("LIVE_SHOP_ID_TW", "").strip()
    LIVE_SHOP_ID_VN = os.getenv("LIVE_SHOP_ID_VN", "").strip()
    
    # Server Configuration
    TUNNEL_URL = os.getenv("TUNNEL_URL", "https://shopee.lemargue.com").strip()
    SHOP_NAME = os.getenv("SHOP_NAME", "clemargue biz").strip()
    
    # API Configuration
    @property
    def SHOPEE_HOST(self):
        return "https://partner.shopeemobile.com" if self.EXECUTION_MODE == "LIVE" else "https://openplatform.sandbox.test-stable.shopee.sg"
    
    @property
    def SHOPEE_PARTNER_ID(self):
        return self.LIVE_SHOPEE_PARTNER_ID if self.EXECUTION_MODE == "LIVE" else self.TEST_SHOPEE_PARTNER_ID
    
    @property
    def SHOPEE_PARTNER_KEY(self):
        return self.LIVE_SHOPEE_PARTNER_KEY if self.EXECUTION_MODE == "LIVE" else self.TEST_SHOPEE_PARTNER_KEY
    
    def get_shop_id(self, country_code="SG"):
        """Get shop ID based on country and execution mode"""
        prefix = "LIVE" if self.EXECUTION_MODE == "LIVE" else "TEST"
        attr_name = f"{prefix}_SHOP_ID_{country_code}"
        return getattr(self, attr_name, "")
    
    # Database Configuration
    DB_PATH = BASE_DIR / "cache.db"
    
    # AI Configuration
    OPENAI_MODEL = "gpt-4o-mini"
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7

settings = Settings()
