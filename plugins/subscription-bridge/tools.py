"""
Subscription Bridge Tools for Hermes Agent
Provides status, model discovery, and lifecycle management for the zero-key subscription gateway.
"""

import os
import socket
import subprocess
import sys
from typing import Dict, Any, List
import httpx

GATEWAY_PORT = 5288
GATEWAY_URL = f"http://127.0.0.1:{GATEWAY_PORT}/v1"

def is_gateway_running(port: int = GATEWAY_PORT) -> bool:
    """Check if the local TCP port is accepting connections."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0

def start_subscription_gateway() -> Dict[str, Any]:
    """Launch the local zero-token subscription gateway in the background if not active."""
    if is_gateway_running():
        return {"running": True, "message": f"Gateway is already running on port {GATEWAY_PORT}.", "url": GATEWAY_URL}

    gateway_script = os.path.join(os.path.dirname(__file__), "gateway.py")
    if not os.path.exists(gateway_script):
        return {"running": False, "error": f"Gateway script not found: {gateway_script}"}

    try:
        subprocess.Popen(
            [sys.executable or "py", gateway_script],
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True
        )
        return {"running": True, "message": f"Launched gateway daemon on port {GATEWAY_PORT}.", "url": GATEWAY_URL}
    except Exception as e:
        return {"running": False, "error": str(e)}

def get_subscription_gateway_status() -> Dict[str, Any]:
    """Check health and live status of the Subscription Bridge gateway on port 5288."""
    try:
        r = httpx.get(f"{GATEWAY_URL}/models", timeout=3.0)
        if r.status_code == 200:
            data = r.json()
            models = [m.get("id") for m in data.get("data", [])]
            return {
                "running": True,
                "port": GATEWAY_PORT,
                "endpoint": GATEWAY_URL,
                "model_count": len(models),
                "models": models,
            }
        return {
            "running": False,
            "error": f"HTTP status {r.status_code}: {r.text}",
        }
    except Exception as e:
        return {
            "running": False,
            "error": str(e),
            "hint": "Start the gateway with start_subscription_gateway() or pwsh .\\start-gateway.ps1",
        }

def list_subscription_models() -> List[str]:
    """Return a list of available zero-token subscription model IDs."""
    status = get_subscription_gateway_status()
    if status.get("running"):
        return status.get("models", [])
    return []
