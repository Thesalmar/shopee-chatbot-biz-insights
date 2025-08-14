#!/usr/bin/env python3
"""
Shopee-GPT-4o LINE buyer-bot – crash-proof + env fixed + updated OpenAI API
"""
import os
import re
import sqlite3
import time
import hmac
import hashlib
import requests
from pathlib import Path
from fastapi import FastAPI, Request
from linebot.v3.messaging import (
    MessagingApi, ApiClient, Configuration, TextMessage, ReplyMessageRequest
)
from dotenv import load_dotenv

# --------------------------------------------------
# 1️⃣  FORCE .env load
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"
load_dotenv(env_path)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SHOPEE_PARTNER_ID = int(os.getenv("SHOPEE_PARTNER_ID", 1281306))
SHOPEE_PARTNER_KEY = os.getenv("SHOPEE_PARTNER_KEY")
SHOP_NAME = os.getenv("SHOP_NAME", "ShopeeBuddy")

cfg = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
line = MessagingApi(ApiClient(cfg))
app = FastAPI()

# --------------------------------------------------
# 2️⃣  SQLITE HAND-OFF TABLE
# --------------------------------------------------
DB_PATH = BASE_DIR / "cache.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.execute(
    "CREATE TABLE IF NOT EXISTS handoff "
    "(user_id TEXT PRIMARY KEY, open BOOLEAN DEFAULT FALSE)"
)
conn.commit()

# --------------------------------------------------
# 3️⃣  SHOPEE HELPERS
# --------------------------------------------------
SHOPEE_HOST = "https://partner.test-stable.shopeemobile.com"

def _sign(path: str, ts: int, **extra) -> str:
    base = f"{SHOPEE_PARTNER_ID}{path}{ts}" + "".join(str(v) for v in extra.values())
    return hmac.new(
        SHOPEE_PARTNER_KEY.encode(), base.encode(), hashlib.sha256
    ).hexdigest()

def get_order_detail(order_sn: str):
    ts = int(time.time())
    path = "/api/v2/order/get_order_detail"
    params = {
        "partner_id": SHOPEE_PARTNER_ID,
        "timestamp": ts,
        "order_sn_list": f'["{order_sn}"]',
    }
    params["sign"] = _sign(path, ts, **params)
    url = SHOPEE_HOST + path + "?" + requests.compat.urlencode(params)
    try:
        response = requests.get(url, timeout=5).json()
        if response.get("error") == "order_not_found":
            return {"hint": "Order not found. Please check the order number."}
        return response.get("response", {})
    except Exception as e:
        print(f"❌ Shopee API error: {e}")
        return {"hint": "Failed to fetch order details. Please try again later."}

# --------------------------------------------------
# 4️⃣  GPT-4o HELPER
# --------------------------------------------------
import openai
openai.api_key = OPENAI_API_KEY

def friendly_reply(text: str, order_data=None) -> str:
    system = f"You are a casual buddy for {SHOP_NAME}. Emoji-light 😊📦✨. Reply in the user’s language (EN/中文). End with: Anything else I can help with?"
    user = f"{text}\norder_data={order_data}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            max_tokens=120
        )
        return response.choices[0].message.content
    except openai.APIError as e:
        if e.http_status == 429:
            return "⚠️ I’ve hit my usage limit for now. Please try again later!"
        return f"⚠️ GPT error: {e}"

# --------------------------------------------------
# 5️⃣  HAND-OFF SAFEGUARD
# --------------------------------------------------
def is_handoff(user_id: str) -> bool:
    cur = conn.execute(
        "SELECT open FROM handoff WHERE user_id = ?", (user_id,)
    )
    return bool(cur.fetchone())

# --------------------------------------------------
# 6️⃣  FASTAPI ROUTES
# --------------------------------------------------
@app.post("/webhook")
async def handle(request: Request):
    payload = await request.json()
    print("🔍 RAW:", payload)
    for ev in payload.get("events", []):
        print("🔍 EVENT:", ev)
        if ev["type"] != "message" or ev["message"]["type"] != "text":
            print("🔍 skipped (not text)")
            continue

        msg = ev["message"]["text"].strip()
        uid = ev["source"].get("user_id") or ev["source"].get("group_id") or ""
        print("🔍 uid:", uid, "msg:", msg)

        if is_handoff(uid):
            print("🔍 skipped (handoff active)")
            continue

        order_sn = re.search(r"#?\d{12,}", msg)
        order_data = None
        if re.search(r"\bwhere.*order\b|\btracking\b", msg.lower()):
            if order_sn:
                order_data = get_order_detail(order_sn.group())
            else:
                order_data = {"hint": "Please give the order number like #2025TW123456"}

        print("🔍 order_data:", order_data)
        reply = friendly_reply(msg, order_data)
        print("🔍 sending reply:", reply)
        try:
            line.reply_message(
                ReplyMessageRequest(
                    replyToken=ev["replyToken"],
                    messages=[TextMessage(text=reply)]
                )
            )
        except Exception as e:
            print("❌ LINE reply failed:", e)
    return "ok"

@app.post("/shopee/handoff")
async def shopee_handoff(request: Request):
    body = await request.json()
    action = body.get("action")
    buyer_id = body.get("buyer_id")
    if action == "open":
        conn.execute(
            "INSERT OR REPLACE INTO handoff(user_id, open) VALUES(?, TRUE)",
            (buyer_id,)
        )
    elif action == "close":
        conn.execute("DELETE FROM handoff WHERE user_id = ?", (buyer_id,))
    conn.commit()
    return {"status": "ok"}

@app.get("/")
def root():
    return {"status": "ok"}
