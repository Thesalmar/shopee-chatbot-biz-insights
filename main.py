#!/usr/bin/env python3
"""
Shopee-GPT-4o LINE buyer-bot – ready for GET OAuth callbacks
"""
import os
import re
import sqlite3
import time
import hmac
import hashlib
import requests
from pathlib import Path
from fastapi import FastAPI, Request, Response
from linebot.v3.messaging import (
    MessagingApi, ApiClient, Configuration, TextMessage, ReplyMessageRequest
)
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY            = os.getenv("OPENAI_API_KEY")
SHOPEE_PARTNER_ID         = int(os.getenv("SHOPEE_PARTNER_ID", 0))
SHOPEE_PARTNER_KEY        = os.getenv("SHOPEE_PARTNER_KEY", "")
SHOP_ID                   = os.getenv("SHOP_ID", "")
COUNTRY                   = os.getenv("COUNTRY", "SG")
TUNNEL_URL                = os.getenv("TUNNEL_URL", "https://example.com")

cfg = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
line = MessagingApi(ApiClient(cfg))
app = FastAPI()

DB_PATH = BASE_DIR / "cache.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS handoff (user_id TEXT PRIMARY KEY, open BOOLEAN DEFAULT FALSE)")
conn.execute("CREATE TABLE IF NOT EXISTS tokens (shop_id TEXT PRIMARY KEY, access_token TEXT, refresh_token TEXT)")
conn.commit()

SHOPEE_HOST = "https://partner.test-stable.shopeemobile.com"

def _sign(path: str, ts: int, **extra) -> str:
    base = f"{SHOPEE_PARTNER_ID}{path}{ts}" + "".join(str(v) for v in extra.values())
    return hmac.new(SHOPEE_PARTNER_KEY.encode(), base.encode(), hashlib.sha256).hexdigest()

def get_access_token(shop_id: str) -> str | None:
    row = conn.execute("SELECT access_token FROM tokens WHERE shop_id = ?", (shop_id,)).fetchone()
    return row[0] if row else None

def get_order_detail(order_sn: str, shop_id: str) -> dict:
    token = get_access_token(shop_id)
    if not token:
        return {"hint": "Shop not authorised. Use /shopee/auth first."}
    ts = int(time.time())
    path = "/api/v2/order/get_order_detail"
    params = {"partner_id": SHOPEE_PARTNER_ID, "timestamp": ts, "shop_id": int(shop_id)}
    body = {"order_sn_list": [order_sn]}
    base = f"{SHOPEE_PARTNER_ID}{path}{ts}{token}{shop_id}"
    params["sign"] = hmac.new(SHOPEE_PARTNER_KEY.encode(), base.encode(), hashlib.sha256).hexdigest()
    url = SHOPEE_HOST + path + "?" + requests.compat.urlencode(params)
    try:
        r = requests.post(url, json=body, timeout=5).json()
        return r.get("response", {})
    except Exception as e:
        print("❌ Shopee API error:", e)
        return {"hint": "Could not fetch order."}

import openai
openai.api_key = OPENAI_API_KEY

def friendly_reply(text: str, order_data=None) -> str:
    system = f"You are a casual buddy for {SHOP_NAME} ({COUNTRY}). Emoji-light 😊📦✨. Reply in EN/中文. End with: Anything else I can help with?"
    user = f"{text}\norder_data={order_data}"
    try:
        resp = openai.ChatCompletion.create(model="gpt-4o", messages=[{"role": "system", "content": system}, {"role": "user", "content": user}], max_tokens=120)
        return resp.choices[0].message.content
    except openai.APIError as e:
        return f"⚠️ GPT error: {e}"

def is_handoff(user_id: str) -> bool:
    return bool(conn.execute("SELECT open FROM handoff WHERE user_id = ?", (user_id,)).fetchone())

@app.post("/webhook")
async def handle(request: Request):
    payload = await request.json()
    for ev in payload.get("events", []):
        if ev["type"] != "message" or ev["message"]["type"] != "text":
            continue
        msg = ev["message"]["text"].strip()
        uid = ev["source"].get("user_id", "")
        if not uid or is_handoff(uid):
            continue
        order_sn = re.search(r"#?\d{12,}", msg)
        order_data = None
        if re.search(r"\bwhere.*order\b|\btracking\b", msg.lower()):
            if order_sn:
                order_data = get_order_detail(order_sn.group(), SHOP_ID)
            else:
                order_data = {"hint": "Please give the order number like #2025TW123456"}
        reply = friendly_reply(msg, order_data)
        line.reply_message(ReplyMessageRequest(replyToken=ev["replyToken"], messages=[TextMessage(text=reply)]))
    return "ok"

@app.get("/shopee/auth")
async def shopee_auth():
    ts = int(time.time())
    sign = _sign("/api/v2/shop/auth_partner", ts)
    url = f"{SHOPEE_HOST}/api/v2/shop/auth_partner?partner_id={SHOPEE_PARTNER_ID}&timestamp={ts}&sign={sign}&redirect={TUNNEL_URL}/shopee/callback"
    return {"auth_url": url}

# Accept both GET (redirect) and POST (fallback)
@app.get("/shopee/callback")
async def shopee_callback_get(code: str, shop_id: str):
    return await exchange_and_store(code, shop_id)

@app.post("/shopee/callback")
async def shopee_callback_post(code: str, shop_id: str):
    return await exchange_and_store(code, shop_id)

async def exchange_and_store(code: str, shop_id: str):
    ts = int(time.time())
    sign = _sign("/api/v2/auth/token/get", ts, code=code, shop_id=shop_id)
    payload = {
        "partner_id": SHOPEE_PARTNER_ID,
        "code": code,
        "shop_id": int(shop_id),
        "timestamp": ts,
        "sign": sign,
    }
    try:
        r = requests.post(SHOPEE_HOST + "/api/v2/auth/token/get", json=payload, timeout=5).json()
        token = r.get("response", {})
        conn.execute(
            "INSERT OR REPLACE INTO tokens(shop_id, access_token, refresh_token) VALUES(?,?,?)",
            (shop_id, token["access_token"], token["refresh_token"])
        )
        conn.commit()
        return Response("✅ Authorised! You can close this tab.", status_code=200)
    except Exception as e:
        return Response(f"❌ OAuth failed: {e}", status_code=400)

@app.get("/")
def root():
    return {"status": "ok"}
