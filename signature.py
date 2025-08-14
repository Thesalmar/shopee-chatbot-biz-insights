import os
import time
import hmac
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SHOPEE_PARTNER_ID = int(os.getenv("SHOPEE_PARTNER_ID", 1281306))
SHOPEE_PARTNER_KEY = os.getenv("SHOPEE_PARTNER_KEY")

def _sign(path: str, ts: int, **extra) -> str:
    base = f"{SHOPEE_PARTNER_ID}{path}{ts}" + "".join(str(v) for v in extra.values())
    return hmac.new(
        SHOPEE_PARTNER_KEY.encode(), base.encode(), hashlib.sha256
    ).hexdigest()

# Example usage
path = "/api/v2/order/get_order_detail"
ts = int(time.time())
params = {
    "partner_id": SHOPEE_PARTNER_ID,
    "timestamp": ts,
    "order_sn_list": '["2025TW123456"]',
}
sign = _sign(path, ts, **params)
print(f"Generated sign: {sign}")
