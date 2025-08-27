import time
import hmac
import hashlib
import requests
from typing import Dict, Any
from config.settings import settings
from database.models import db

class ShopeeAuth:
    def __init__(self):
        self.host = settings.SHOPEE_HOST
        self.partner_id = settings.SHOPEE_PARTNER_ID
        self.partner_key = settings.SHOPEE_PARTNER_KEY
        self.tunnel_url = settings.TUNNEL_URL
    
    def _sign_public_api(self, path: str, ts: int) -> str:
        """PUBLIC API signature generation"""
        base_str = f"{self.partner_id}{path}{ts}"
        key_bytes = self.partner_key.encode("utf-8")
        sig = hmac.new(key_bytes, base_str.encode("utf-8"), hashlib.sha256).hexdigest()
        
        print(f"🧪 PUBLIC API SIGNATURE")
        print(f"🧪 Partner ID: {self.partner_id}")
        print(f"🧪 Path: {path}")
        print(f"🧪 Timestamp: {ts}")
        print(f"🧪 Base string: {base_str}")
        print(f"🧪 Signature: {sig}")
        
        return sig
    
    def get_auth_url(self) -> Dict[str, Any]:
        """Get authentication URL"""
        ts = int(time.time())
        path = "/api/v2/shop/auth_partner"
        redirect_url = f"{self.tunnel_url}/shopee/callback"
        
        sig = self._sign_public_api(path, ts)
        
        auth_url = (
            f"{self.host}{path}"
            f"?partner_id={self.partner_id}"
            f"&timestamp={ts}"
            f"&sign={sig}"
            f"&redirect={redirect_url}"
        )
        
        print(f"🔗 Generated auth URL: {auth_url}")
        return {
            "auth_url": auth_url, 
            "timestamp": ts, 
            "signature": sig, 
            "status": "COMPLIANT_VERSION"
        }
    
    def exchange_token(self, code: str, shop_id: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        ts = int(time.time())
        path = "/api/v2/auth/token/get"
        
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
        
        print(f"🔄 Token request:")
        print(f"   URL: {self.host}{path}")
        print(f"   Query params: {query_params}")
        print(f"   JSON payload: {json_payload}")
        
        try:
            response = requests.post(
                f"{self.host}{path}",
                params=query_params,
                json=json_payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"📥 Token response: {data}")
            
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            
            if not access_token:
                print(f"❌ No access token found. Full response: {data}")
                return {"error": "No access token in response", "data": data}
            
            # Save tokens to database
            db.save_tokens(shop_id, access_token, refresh_token or "")
            
            print(f"✅ Tokens saved successfully!")
            print(f"   Shop ID: {shop_id}")
            print(f"   Access token: {access_token[:20]}...")
            print(f"   Refresh token: {refresh_token[:20] if refresh_token else 'None'}...")
            print(f"   Expires in: {data.get('expire_in', 'Unknown')} seconds")
            
            return {
                "success": True,
                "shop_id": shop_id,
                "access_token_preview": f"{access_token[:20]}...",
                "expires_in": data.get('expire_in', 'Unknown'),
                "message": "COMPLIANT Shopee Integration Activated!"
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return {"error": f"Unexpected error: {str(e)}"}

# Global auth instance
shopee_auth = ShopeeAuth()
