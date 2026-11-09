"""
Hermes Agent Tool Definitions for CLI Bridge
Allows Hermes Agent to delegate tasks directly to Cursor, Codex, Antigravity, OpenCode, and Kimi.
"""

from typing import Dict, Any, Optional
import os
import sys

_dir = os.path.dirname(__file__)
if _dir not in sys.path:
    sys.path.insert(0, _dir)

try:
    from .bridge import run_client, check_status
except (ImportError, ValueError):
    from bridge import run_client, check_status

def cli_bridge(client: str, prompt: str, model: Optional[str] = None, workspace: Optional[str] = None) -> str:
    """
    Delegate execution to a specific local CLI coding agent.
    
    Args:
        client: The name of the client ('cursor', 'codex', 'antigravity', 'opencode', 'kimi').
        prompt: The task instruction or prompt to execute.
        model: Optional model override.
        workspace: Optional workspace directory.
    """
    return run_client(client=client, prompt=prompt, model=model, workspace=workspace)

def run_cursor(prompt: str, model: Optional[str] = None) -> str:
    """Run a prompt through the local Cursor Agent CLI."""
    return run_client(client="cursor", prompt=prompt, model=model)

def run_codex(prompt: str, model: Optional[str] = None) -> str:
    """Run a prompt through the local OpenAI Codex CLI."""
    return run_client(client="codex", prompt=prompt, model=model)

def run_antigravity(prompt: str, model: Optional[str] = None) -> str:
    """Run a prompt through the local Google Antigravity CLI."""
    return run_client(client="antigravity", prompt=prompt, model=model)

def run_opencode(prompt: str, model: Optional[str] = None) -> str:
    """Run a prompt through the local OpenCode CLI."""
    return run_client(client="opencode", prompt=prompt, model=model)

def run_kimi(prompt: str, model: Optional[str] = None) -> str:
    """Run a prompt through the local Kimi CLI."""
    return run_client(client="kimi", prompt=prompt, model=model)

def list_available_clients() -> Dict[str, Dict[str, Any]]:
    """List the detected local coding CLI clients and their availability status."""
    return check_status()
