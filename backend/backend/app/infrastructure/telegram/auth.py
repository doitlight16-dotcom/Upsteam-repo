import hashlib
import hmac
import urllib.parse
from operator import itemgetter

def verify_telegram_init_data(init_data: str, bot_token: str) -> bool:
    """
    Verifies the Telegram WebApp initData string using the bot token.
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    parsed_data = dict(urllib.parse.parse_qsl(init_data))
    
    if "hash" not in parsed_data:
        return False
        
    received_hash = parsed_data.pop("hash")
    
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items(), key=itemgetter(0))
    )
    
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    
    expected_hash = hmac.new(
        secret_key, data_check_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_hash, received_hash)

def parse_user_from_init_data(init_data: str) -> dict | None:
    import json
    parsed_data = dict(urllib.parse.parse_qsl(init_data))
    user_str = parsed_data.get("user")
    if not user_str:
        return None
    try:
        return json.loads(user_str)
    except json.JSONDecodeError:
        return None
