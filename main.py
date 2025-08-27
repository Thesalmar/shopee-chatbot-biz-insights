#!/usr/bin/env python3
"""
Shopee-GPT-4o LINE Seller Assistant – **MODULAR & AI-POWERED VERSION**
Clean architecture with ChatGPT integration
"""
from fastapi import FastAPI, Request, Response
from config.settings import settings
from shopee.auth import shopee_auth
from shopee.business_intelligence import shopee_bi
from line.webhook import line_webhook
from database.models import db

app = FastAPI(title="Shopee AI Seller Assistant", version="v11.0")

# -----------------------------------------------------------------------------
# OAuth Endpoints
# -----------------------------------------------------------------------------
@app.get("/shopee/auth")
async def shopee_auth_endpoint():
    """Get Shopee authentication URL"""
    return shopee_auth.get_auth_url()

@app.get("/shopee/callback")
async def shopee_callback(code: str, shop_id: str):
    """Handle Shopee OAuth callback"""
    result = shopee_auth.exchange_token(code, shop_id)
    
    if "error" in result:
        return Response(f"❌ Authentication failed: {result['error']}", status_code=400)
    
    return Response(
        f"✅ {result['message']}\n"
        f"Shop ID: {result['shop_id']}\n"
        f"Access Token: {result['access_token_preview']}\n"
        f"Token expires in: {result['expires_in']} seconds\n"
        f"You can close this tab.",
        status_code=200
    )

# -----------------------------------------------------------------------------
# LINE Webhook
# -----------------------------------------------------------------------------
@app.post("/webhook")
async def webhook(request: Request):
    """Handle LINE webhook with AI responses"""
    return await line_webhook.handle_webhook(request)

# -----------------------------------------------------------------------------
# Business Intelligence API Endpoints
# -----------------------------------------------------------------------------
@app.get("/dashboard/shop")
async def dashboard_shop():
    """Get shop information"""
    return shopee_bi.get_shop_info()

@app.get("/dashboard/orders")
async def dashboard_orders(days: int = 7):
    """Get order analytics"""
    return shopee_bi.get_order_analytics(days)

@app.get("/dashboard/products")
async def dashboard_products():
    """Get product performance"""
    return shopee_bi.get_product_performance()

@app.get("/dashboard/comprehensive")
async def dashboard_comprehensive():
    """Get comprehensive dashboard"""
    return shopee_bi.get_comprehensive_dashboard()

# -----------------------------------------------------------------------------
# Debug Endpoints
# -----------------------------------------------------------------------------
@app.get("/debug/check-tokens")
async def debug_check_tokens():
    """Check token status"""
    try:
        with db.get_connection() as conn:
            result = conn.execute("SELECT shop_id, access_token, refresh_token FROM tokens").fetchall()
        
        tokens = []
        for row in result:
            shop_id, access_token, refresh_token = row
            tokens.append({
                "shop_id": shop_id,
                "access_token_preview": f"{access_token[:20]}..." if access_token else "None",
                "refresh_token_preview": f"{refresh_token[:20]}..." if refresh_token else "None",
                "access_token_length": len(access_token) if access_token else 0
            })
        
        return {
            "tokens_in_database": len(tokens),
            "tokens": tokens,
            "expected_shop_id": settings.SHOP_ID
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/test-shop-info")
async def debug_test_shop_info():
    """Test shop info API"""
    return shopee_bi.get_shop_info()

# -----------------------------------------------------------------------------
# Health Check Endpoints
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Shopee AI Seller Assistant",
        "version": "v11.0 - Modular Architecture + ChatGPT Integration",
        "environment": "sandbox",
        "features": [
            "🤖 ChatGPT-powered responses",
            "🏗️ Modular architecture",
            "🏪 Shop information (working)",
            "📊 AI-enhanced business analytics",
            "🛍️ Product performance tracking",
            "💬 Natural language processing",
            "✅ Shopee policy compliant"
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
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Shopee AI Seller Assistant",
        "version": "v11.0",
        "ai_integration": "active" if settings.OPENAI_API_KEY else "missing_api_key",
        "environment": "sandbox_optimized",
        "architecture": "modular",
        "compliance_status": "FULLY_COMPLIANT"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9191)
