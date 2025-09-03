#!/usr/bin/env python3
import time
import hmac
import hashlib
import requests
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from config.settings import settings
from database.models import db

class APIRequest(BaseModel):
    endpoint: str = Field(..., description="API endpoint to call")
    method: str = Field(default="GET", description="HTTP method")
    payload: Optional[Dict] = None
    country_code: str = Field(default="SG", description="Country code for shop selection")

class APIResponse(BaseModel):
    data: Dict[str, Any]
    error: Optional[str] = None
    status_code: int = 200
    country: str
    execution_mode: str

class ShopeeAPI:
    def __init__(self):
        self.host = settings.SHOPEE_HOST
        self.partner_id = settings.SHOPEE_PARTNER_ID
        self.partner_key = settings.SHOPEE_PARTNER_KEY
        self.execution_mode = settings.EXECUTION_MODE
    
    def _sign_shop_api(self, path: str, ts: int, access_token: str, shop_id: str) -> str:
        """SHOP API signature generation with auto-critique and validation"""
        base_str = f"{self.partner_id}{path}{ts}{access_token}{shop_id}"
        key_bytes = self.partner_key.encode("utf-8")
        sig = hmac.new(key_bytes, base_str.encode("utf-8"), hashlib.sha256).hexdigest()
        
        # Auto-critique: Validate signature format
        if len(sig) != 64:
            raise ValueError("Invalid signature length")
        
        return sig
    
    def get_access_token(self, country_code: str = "SG") -> Optional[str]:
        """Get valid access token for specific country"""
        shop_id = settings.get_shop_id(country_code)
        return db.get_access_token(shop_id)
    
    def make_shop_api_call(self, endpoint: str, method: str = "GET", payload: Dict = None, country_code: str = "SG") -> Dict[str, Any]:
        """Make authenticated shop API call with production compatibility"""
        token = self.get_access_token(country_code)
        if not token:
            return {"data": {}, "error": "No access token available for this country"}
        
        shop_id = settings.get_shop_id(country_code)
        if not shop_id:
            return {"data": {}, "error": "No shop ID configured for this country"}
        
        try:
            ts = int(time.time())
            path = f"/api/v2{endpoint}"
            sig = self._sign_shop_api(path, ts, token, shop_id)
            
            params = {
                "partner_id": self.partner_id,
                "timestamp": ts,
                "shop_id": int(shop_id),
                "sign": sig,
                "access_token": token
            }
            
            print(f"📤 {method} {endpoint} request - Country: {country_code}")
            
            if method.upper() == "GET":
                response = requests.get(
                    f"{self.host}{path}",
                    params=params,
                    timeout=30,
                )
            else:
                response = requests.post(
                    f"{self.host}{path}",
                    params=params,
                    json=payload or {},
                    headers={"Content-Type": "application/json"},
                    timeout=30,
                )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        "data": data,
                        "error": None,
                        "status_code": 200,
                        "country": country_code,
                        "execution_mode": self.execution_mode
                    }
                except Exception:
                    return {
                        "data": {},
                        "error": "Failed to parse response",
                        "status_code": 500,
                        "country": country_code,
                        "execution_mode": self.execution_mode
                    }
            else:
                return {
                    "data": {},
                    "error": f"API returned {response.status_code}: {response.text}",
                    "status_code": response.status_code,
                    "country": country_code,
                    "execution_mode": self.execution_mode
                }
                
        except Exception as e:
            return {
                "data": {},
                "error": str(e),
                "status_code": 500,
                "country": country_code,
                "execution_mode": self.execution_mode
            }
    
    def get_shop_info(self, country_code: str = "SG") -> Dict[str, Any]:
        """Get shop information for specific country"""
        return self.make_shop_api_call("/shop/get_shop_info", country_code=country_code)
    
    def get_product_list(self, offset: int = 0, page_size: int = 10, country_code: str = "SG") -> Dict[str, Any]:
        """Get product list for specific country"""
        payload = {
            "offset": offset,
            "page_size": page_size
        }
        return self.make_shop_api_call("/product/get_item_list", "POST", payload, country_code)
    
    def get_order_list(self, order_status: str = "ALL", create_time_from: int = None, create_time_to: int = None, country_code: str = "SG") -> Dict[str, Any]:
        """Get order list for specific country"""
        payload = {
            "order_status": order_status,
            "create_time_from": create_time_from or int(time.time()) - 86400 * 7,  # Last 7 days
            "create_time_to": create_time_to or int(time.time())
        }
        return self.make_shop_api_call("/order/get_order_list", "POST", payload, country_code)
    
    def get_shop_category_list(self, country_code: str = "SG") -> Dict[str, Any]:
        """Get shop category list for specific country"""
        return self.make_shop_api_call("/shop_category/get_shop_category_list", country_code=country_code)
    
    def get_item_base_info(self, item_id_list: list, country_code: str = "SG") -> Dict[str, Any]:
        """Get item base info for specific country"""
        payload = {"item_id_list": item_id_list}
        return self.make_shop_api_call("/item/get_item_base_info", "POST", payload, country_code)

# Global API instance
shopee_api = ShopeeAPI()
