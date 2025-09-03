import time
import hmac
import hashlib
import requests
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from config.settings import settings
from database.models import db

class AuthRequest(BaseModel):
    country_code: str = Field(default="SG", description="Country code for shop selection")

class AuthResponse(BaseModel):
    auth_url: str
    timestamp: int
    signature: str
    status: str
    partner_id: int
    host: str
    execution_mode: str

class TokenResponse(BaseModel):
    success: bool
    shop_id: str
    access_token_preview: str
    expires_in: str
    message: str
    country: Optional[str] = None

class ShopeeAuth:
    def __init__(self):
        self.host = settings.SHOPEE_HOST
        self.partner_id = settings.SHOPEE_PARTNER_ID
        self.partner_key = settings.SHOPEE_PARTNER_KEY
        self.tunnel_url = settings.TUNNEL_URL
        self.execution_mode = settings.EXECUTION_MODE
    
    def _sign_public_api(self, path: str, ts: int) -> str:
        """PUBLIC API signature generation with auto-critique"""
        base_str = f"{self.partner_id}{path}{ts}"
        key_bytes = self.partner_key.encode("utf-8")
        sig = hmac.new(key_bytes, base_str.encode("utf-8"), hashlib.sha256).hexdigest()
        
        # Auto-critique: Validate signature format
        if len(sig) != 64:
            raise ValueError("Invalid signature length")
        
        return sig
    
    def get_auth_url(self, country_code: str = "SG") -> Dict[str, Any]:
        """Get authentication URL with country-specific shop selection"""
        ts = int(time.time())
        path = "/api/v2/shop/auth_partner"
        redirect_url = f"{self.tunnel_url}/shopee/callback"
        
        # Validate configuration
        if not self.partner_id or not self.partner_key:
            return {"data": {}, "error": "Invalid Shopee configuration"}
        
        sig = self._sign_public_api(path, ts)
        
        auth_url = (
            f"{self.host}{path}"
            f"?partner_id={self.partner_id}"
            f"&timestamp={ts}"
            f"&sign={sig}"
            f"&redirect={redirect_url}"
        )
        
        response_data = {
            "auth_url": auth_url,
            "timestamp": ts,
            "signature": sig,
            "status": "COMPLIANT_VERSION",
            "partner_id": self.partner_id,
            "host": self.host,
            "execution_mode": self.execution_mode,
            "country_code": country_code,
            "shop_id_hint": settings.get_shop_id(country_code)
        }
        
        return {"data": response_data, "error": None}
    
    def exchange_token(self, code: str, shop_id: str, country_code: str = "SG") -> Dict[str, Any]:
        """Exchange authorization code for access token with validation"""
        ts = int(time.time())
        path = "/api/v2/auth/token/get"
        
        # Validate inputs
        if not code or not shop_id:
            return {"data": {}, "error": "Invalid code or shop_id"}
        
        sig = self._sign_public_api(path, ts)
        
        query_params = {
            "partner_id": self.partner_id,
            "timestamp": ts,
            "sign": sig
        }
        
        json_payload = {
            "code": code,
            "shop_id": int(shop_id)
        }
        
        try:
            response = requests.post(
                f"{self.host}{path}",
                params=query_params,
                json=json_payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            
            if response.status_code != 200:
                return {"data": {}, "error": f"HTTP {response.status_code}: {response.text}"}
            
            data = response.json()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            
            if not access_token:
                return {"data": {}, "error": "No access token in response"}
            
            # Save tokens to database
            db.save_tokens(shop_id, access_token, refresh_token or "", country_code)
            
            response_data = {
                "success": True,
                "shop_id": shop_id,
                "access_token_preview": f"{access_token[:10]}...",
                "expires_in": str(data.get('expire_in', 'Unknown')),
                "message": "COMPLIANT Shopee Integration Activated!",
                "country": country_code,
                "execution_mode": self.execution_mode
            }
            
            return {"data": response_data, "error": None}
            
        except requests.exceptions.RequestException as e:
            return {"data": {}, "error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"data": {}, "error": f"Unexpected error: {str(e)}"}

# Global auth instance
shopee_auth = ShopeeAuth()
