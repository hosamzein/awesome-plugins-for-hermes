"""
Hermes Native Subscription Auth Manager
Manages OAuth and subscription session tokens directly inside ~/.hermes/auth.json
No external CLI tools, coding agents, or third-party binaries required.
"""

import json
import os
import sys
from typing import Dict, Optional

AUTH_FILE = os.path.expanduser(r"~\.hermes\auth.json")

def load_auth() -> Dict[str, dict]:
    if not os.path.exists(AUTH_FILE):
        return {}
    try:
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_auth(data: Dict[str, dict]):
    os.makedirs(os.path.dirname(AUTH_FILE), exist_ok=True)
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def set_provider_token(provider: str, token: str, refresh_token: Optional[str] = None, expires_at: Optional[int] = None):
    data = load_auth()
    data[provider] = {
        "access_token": token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
        "auth_type": "subscription"
    }
    save_auth(data)

def get_provider_token(provider: str) -> Optional[str]:
    data = load_auth()
    info = data.get(provider, {})
    return info.get("access_token")

def is_provider_authenticated(provider: str) -> bool:
    token = get_provider_token(provider)
    return bool(token and len(token) > 5)
