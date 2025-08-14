import time, hmac, hashlib, requests, os
from urllib.parse import urlencode

PARTNER_ID = int(os.getenv("SHOPEE_PARTNER_ID"))
PARTNER_KEY = os.getenv("SHOPEE_PARTNER_KEY").encode()
HOST = "https://partner.test-stable.shopeemobile.com"   # sandbox

def sign(path, ts, **extra):
    base = f"{PARTNER_ID}{path}{ts}" + "".join(str(v) for v in extra.values())
    return hmac.new(PARTNER_KEY, base.encode(), hashlib.sha256).hexdigest()

def get_order_detail(order_sn):
    ts = int(time.time())
    path = "/api/v2/order/get_order_detail"
    params = {"partner_id": PARTNER_ID, "timestamp": ts, "order_sn_list": f"[{order_sn}]"}
    params["sign"] = sign(path, ts)
    url = HOST + path + "?" + urlencode(params)
    return requests.get(url).json()
