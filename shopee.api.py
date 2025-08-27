import time
import hmac
import hashlib
import requests
from typing import Dict, Any, Optional
from config.settings import settings
from database.models import db

class ShopeeAPI:
    def __init__(self):
        self.host = settings.SHOPEE_HOST
        self.partner_id = settings.SHOPEE_PARTNER_ID
        self.partner_key = settings.SHOPEE_PARTNER_KEY
        self.shop_id = settings.SHOP_ID
    
    def _sign_shop_api(self, path: str, ts: int, access_token: str, shop_id: str) -> str:
        """SHOP API signature generation"""
        base_str = f"{self.partner_id}{path}{ts}{access_token}{shop_id}"
        key_bytes = self.partner_key.encode("utf-8")
        sig = hmac.new(key_bytes, base_str.encode("utf-8"), hashlib.sha256).hexdigest()
        
        print(f"🧪 SHOP API SIGNATURE")
        print(f"🧪 Partner ID: {self.partner_id}")
        print(f"🧪 Path: {path}")
        print(f"🧪 Timestamp: {ts}")
        print(f"🧪 Access Token: {access_token[:10]}...")
        print(f"🧪 Shop ID: {shop_id}")
        print(f"🧪 Base string: {base_str}")
        print(f"🧪 Signature: {sig}")
        
        return sig
    
    def get_access_token(self) -> Optional[str]:
        """Get valid access token"""
        return db.get_access_token(self.shop_id)
    
    def make_shop_api_call(self, endpoint: str, method: str = "GET", payload: Dict = None) -> Dict[str, Any]:
        """Make authenticated shop API call"""
        token = self.get_access_token()
        if not token:
            return {"error": "No access token available"}
        
        try:
            ts = int(time.time())
            path = f"/api/v2{endpoint}"
            sig = self._sign_shop_api(path, ts, token, self.shop_id)
            
            params = {
                "partner_id": self.partner_id,
                "timestamp": ts,
                "shop_id": int(self.shop_id),
                "sign": sig,
                "access_token": token
            }
            
            print(f"📤 {method} {endpoint} request - Params: {params}")
            
            if method.upper() == "GET":
                response = requests.get(
                    f"{self.host}{path}",
                    params=params,
                    timeout=10,
                )
            else:
                if payload:
                    print(f"📤 Payload: {payload}")
                response = requests.post(
                    f"{self.host}{path}",
                    params=params,
                    json=payload or {},
                    headers={"Content-Type": "application/json"},
                    timeout=10,
                )
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response: {response.text}")
            
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    return {"error": "Failed to parse response"}
            else:
                return {"error": f"API returned {response.status_code}: {response.text}"}
                
        except Exception as e:
            print(f"❌ API call error: {e}")
            return {"error": str(e)}
    
    def get_shop_info(self) -> Dict[str, Any]:
        """Get shop information"""
        return self.make_shop_api_call("/shop/get_shop_info")
    
    def get_product_list(self, offset: int = 0, page_size: int = 10) -> Dict[str, Any]:
        """Get product list"""
        payload = {
            "offset": offset,
            "page_size": page_size
        }
        return self.make_shop_api_call("/product/get_item_list", "POST", payload)

# Global API instance
shopee_api = ShopeeAPI()
