#!/usr/bin/env python3
"""
Shopee-GPT-4o LINE Seller Assistant – **PRODUCTION READY VERSION**
Supports both TEST and LIVE environments with country-specific shop management
"""
from fastapi import FastAPI, Request, Response, Query
from pydantic import BaseModel
from config.settings import settings
from shopee.auth import shopee_auth, AuthRequest, AuthResponse
from shopee.business_intelligence import shopee_bi
from line.webhook import line_webhook
from database.models import db

app = FastAPI(title="Shopee AI Seller Assistant", version="v12.0 - Production Ready")

# ----------------------------------------------------------------------------- 
# OAuth Endpoints
# -----------------------------------------------------------------------------
@app.get("/shopee/auth")
async def shopee_auth_endpoint(country: str = Query(default="SG", description="Country code for shop selection")):
    """Get Shopee authentication URL with country-specific shop selection"""
    auth_request = AuthRequest(country_code=country)
    return shopee_auth.get_auth_url(auth_request.country_code)

@app.get("/shopee/callback")
async def shopee_callback(code: str, shop_id: str, country: str = Query(default="SG", description="Country code")):
    """Handle Shopee OAuth callback with country context"""
    result = shopee_auth.exchange_token(code, shop_id, country)
    
    if result.get("error"):
        return {
            "data": {},
            "error": result["error"]
        }
    
    return {
        "data": result["data"],
        "error": None
    }

# ----------------------------------------------------------------------------- 
# LINE Webhook
# -----------------------------------------------------------------------------
@app.post("/webhook")
async def webhook(request: Request):
    """Handle LINE webhook with AI responses"""
    response = await line_webhook.handle_webhook(request)
    return {
        "data": response,
        "error": None
    }

# ----------------------------------------------------------------------------- 
# Business Intelligence API Endpoints
# -----------------------------------------------------------------------------
@app.get("/dashboard/shop")
async def dashboard_shop(country: str = Query(default="SG", description="Country code")):
    """Get shop information for specific country"""
    return shopee_bi.get_shop_info(country)

@app.get("/dashboard/orders")
async def dashboard_orders(
    days: int = Query(default=7, description="Number of days to analyze"),
    country: str = Query(default="SG", description="Country code")
):
    """Get order analytics for specific country"""
    return shopee_bi.get_order_analytics(days, country)

@app.get("/dashboard/products")
async def dashboard_products(country: str = Query(default="SG", description="Country code")):
    """Get product performance for specific country"""
    return shopee_bi.get_product_performance(country)

@app.get("/dashboard/comprehensive")
async def dashboard_comprehensive(country: str = Query(default="SG", description="Country code")):
    """Get comprehensive dashboard for specific country"""
    return shopee_bi.get_comprehensive_dashboard(country)

# ----------------------------------------------------------------------------- 
# Debug Endpoints
# -----------------------------------------------------------------------------
@app.get("/debug/check-tokens")
async def debug_check_tokens():
    """Check token status across all countries"""
    try:
        with db.get_connection() as conn:
            result = conn.execute("SELECT shop_id, access_token, refresh_token, country FROM tokens").fetchall()
        
        tokens = []
        for row in result:
            shop_id, access_token, refresh_token, country = row
            tokens.append({
                "shop_id": shop_id,
                "access_token_preview": f"{access_token[:10]}..." if access_token else "None",
                "refresh_token_preview": f"{refresh_token[:10] if refresh_token else 'None'}...",
                "access_token_length": len(access_token) if access_token else 0,
                "country": country
            })
        
        return {
            "data": {
                "tokens_in_database": len(tokens),
                "tokens": tokens,
                "execution_mode": settings.EXECUTION_MODE
            },
            "error": None
        }
    except Exception as e:
        return {
            "data": {},
            "error": str(e)
        }

@app.get("/debug/test-shop-info")
async def debug_test_shop_info(country: str = Query(default="SG", description="Country code")):
    """Test shop info API for specific country"""
    return shopee_bi.get_shop_info(country)

# ----------------------------------------------------------------------------- 
# Configuration Health Check
# -----------------------------------------------------------------------------
@app.get("/config")
async def get_config():
    """Get current configuration status (safe to expose - no secrets)"""
    return {
        "data": {
            "execution_mode": settings.EXECUTION_MODE,
            "host": settings.SHOPEE_HOST,
            "partner_id": settings.SHOPEE_PARTNER_ID,
            "tunnel_url": settings.TUNNEL_URL,
            "shop_name": settings.SHOP_NAME,
            "supported_countries": ["SG", "MY", "PH", "TH", "TW", "VN"]
        },
        "error": None
    }

# ----------------------------------------------------------------------------- 
# Health Check Endpoints
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    """Root endpoint with comprehensive system status"""
    return {
        "data": {
            "status": "ok",
            "service": "Shopee AI Seller Assistant",
            "version": "v12.0 - Production Ready",
            "environment": settings.EXECUTION_MODE,
            "host": settings.SHOPEE_HOST,
            "features": [
                "🤖 ChatGPT-powered responses",
                "🏗️ Multi-country architecture",
                "🏪 Shop information (working)",
                "📊 AI-enhanced business analytics", 
                "🛍️ Product performance tracking",
                "💬 Natural language processing",
                "✅ Production/Sandbox dual-mode",
                "🌍 Multi-country support"
            ],
            "ai_status": "🤖 ChatGPT Integration Active" if settings.OPENAI_API_KEY else "⚠️ OpenAI API Key Missing",
            "modules": [
                "config.settings",
                "database.models", 
                "ai.chatgpt",
                "shopee.auth",
                "shopee.api",
                "shopee.business_intelligence",
                "line.webhook",
                "line.messages"
            ]
        },
        "error": None
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "data": {
            "status": "healthy",
            "service": "Shopee AI Seller Assistant",
            "version": "v12.0",
            "ai_integration": "active" if settings.OPENAI_API_KEY else "missing_api_key",
            "environment": settings.EXECUTION_MODE,
            "architecture": "production_ready",
            "compliance_status": "FULLY_COMPLIANT"
        },
        "error": None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9191)
