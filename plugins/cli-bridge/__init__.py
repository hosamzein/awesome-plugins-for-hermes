"""
CLI Bridge Plugin for Hermes Agent
Enables seamless execution and delegation across Cursor, Codex, Antigravity, OpenCode, and Kimi.
"""

import inspect
import json
import os
import sys

# Ensure current plugin directory is in sys.path
_plugin_dir = os.path.dirname(__file__)
if _plugin_dir not in sys.path:
    sys.path.insert(0, _plugin_dir)

try:
    from .tools import (
        cli_bridge,
        run_cursor,
        run_codex,
        run_antigravity,
        run_opencode,
        run_kimi,
        list_available_clients,
    )
except ImportError:
    from tools import (
        cli_bridge,
        run_cursor,
        run_codex,
        run_antigravity,
        run_opencode,
        run_kimi,
        list_available_clients,
    )

SCHEMAS = {
    "cli_bridge": {
        "name": "cli_bridge",
        "description": "Delegate tasks directly to local Cursor, Codex, Antigravity, OpenCode, or Kimi CLI clients.",
        "parameters": {
            "type": "object",
            "properties": {
                "client": {
                    "type": "string",
                    "description": "Target client: 'cursor', 'codex', 'antigravity', 'opencode', or 'kimi'.",
                    "enum": ["cursor", "codex", "antigravity", "opencode", "kimi"],
                },
                "prompt": {
                    "type": "string",
                    "description": "Task prompt or instruction to execute in the client.",
                },
                "model": {
                    "type": "string",
                    "description": "Optional model override.",
                },
                "workspace": {
                    "type": "string",
                    "description": "Optional workspace directory path.",
                },
            },
            "required": ["client", "prompt"],
        },
    },
    "run_cursor": {
        "name": "run_cursor",
        "description": "Execute prompt using local Cursor Agent CLI.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt for Cursor Agent."},
                "model": {"type": "string", "description": "Optional model override."},
            },
            "required": ["prompt"],
        },
    },
    "run_codex": {
        "name": "run_codex",
        "description": "Execute prompt using local OpenAI Codex CLI.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt for Codex CLI."},
                "model": {"type": "string", "description": "Optional model override."},
            },
            "required": ["prompt"],
        },
    },
    "run_antigravity": {
        "name": "run_antigravity",
        "description": "Execute prompt using local Google Antigravity CLI.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt for Antigravity."},
                "model": {"type": "string", "description": "Optional model override."},
            },
            "required": ["prompt"],
        },
    },
    "run_opencode": {
        "name": "run_opencode",
        "description": "Execute prompt using local OpenCode CLI.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt for OpenCode."},
                "model": {"type": "string", "description": "Optional model override."},
            },
            "required": ["prompt"],
        },
    },
    "run_kimi": {
        "name": "run_kimi",
        "description": "Execute prompt using local Moonshot Kimi CLI.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt for Kimi CLI."},
                "model": {"type": "string", "description": "Optional model override."},
            },
            "required": ["prompt"],
        },
    },
    "list_available_clients": {
        "name": "list_available_clients",
        "description": "Check detected status and paths of local CLI engines (Cursor, Codex, Antigravity, OpenCode, Kimi).",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}

TOOLS = {
    "cli_bridge": cli_bridge,
    "run_cursor": run_cursor,
    "run_codex": run_codex,
    "run_antigravity": run_antigravity,
    "run_opencode": run_opencode,
    "run_kimi": run_kimi,
    "list_available_clients": list_available_clients,
}

def register(ctx=None):
    """Hermes Agent plugin registration entry point."""
    if not ctx or not hasattr(ctx, "register_tool"):
        return

    reg_fn = getattr(ctx, "register_tool")
    sig = inspect.signature(reg_fn)
    params = list(sig.parameters.keys())

    for tool_name, func in TOOLS.items():
        schema = SCHEMAS.get(tool_name)
        
        # Check if Hermes expects keyword arguments (schema, handler, toolset)
        if "schema" in params or "handler" in params:
            def make_handler(f):
                def handler(args=None, **kwargs):
                    if isinstance(args, dict):
                        return f(**args)
                    elif kwargs:
                        return f(**kwargs)
                    return f()
                return handler

            try:
                ctx.register_tool(
                    name=tool_name,
                    toolset="cli_bridge",
                    schema=schema,
                    handler=make_handler(func),
                )
                continue
            except TypeError:
                pass

        # Fallback to standard 2-argument signature: (name, function)
        try:
            ctx.register_tool(tool_name, func)
        except Exception:
            try:
                ctx.register_tool(name=tool_name, func=func)
            except Exception:
                pass
