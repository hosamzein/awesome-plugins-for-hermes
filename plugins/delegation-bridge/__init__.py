"""
Delegation Bridge Plugin for Hermes Agent
Implements Review-First cross-agent delegation across Cursor, Codex, Antigravity, OpenCode, and Kimi.
"""

import inspect
import json
import os
import sys

_plugin_dir = os.path.dirname(__file__)
if _plugin_dir not in sys.path:
    sys.path.insert(0, _plugin_dir)

try:
    from .tools import (
        delegate_task,
        review_task,
        land_task,
        reject_task,
        list_supported_implementers,
    )
except ImportError:
    from tools import (
        delegate_task,
        review_task,
        land_task,
        reject_task,
        list_supported_implementers,
    )

SCHEMAS = {
    "delegate_task": {
        "name": "delegate_task",
        "description": "Dispatch self-contained task brief to implementer CLI (cursor, codex, antigravity, opencode, kimi) in isolated review-first mode.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent": {
                    "type": "string",
                    "description": "Target implementer agent: 'cursor', 'codex', 'antigravity', 'opencode', 'kimi'.",
                    "enum": ["cursor", "codex", "antigravity", "opencode", "kimi"],
                },
                "brief": {
                    "type": "string",
                    "description": "Comprehensive, self-contained instructions for the implementer.",
                },
                "cd": {
                    "type": "string",
                    "description": "Target workspace directory path (defaults to current dir).",
                },
                "model": {
                    "type": "string",
                    "description": "Optional model override.",
                },
                "read_only": {
                    "type": "boolean",
                    "description": "If True, runs in diagnosis/planning mode without making file modifications.",
                },
                "session": {
                    "type": "string",
                    "description": "Optional session ID to resume.",
                },
            },
            "required": ["agent", "brief"],
        },
    },
    "review_task": {
        "name": "review_task",
        "description": "Inspect git diff, modified status, and stats produced by delegated agent.",
        "parameters": {
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "Optional run ID from delegate_task.",
                },
                "workspace": {
                    "type": "string",
                    "description": "Target workspace directory to inspect.",
                },
            },
        },
    },
    "land_task": {
        "name": "land_task",
        "description": "Stage, approve, and commit verified code changes made by the implementer.",
        "parameters": {
            "type": "object",
            "properties": {
                "workspace": {
                    "type": "string",
                    "description": "Target workspace directory.",
                },
                "commit_message": {
                    "type": "string",
                    "description": "Git commit message.",
                },
            },
        },
    },
    "reject_task": {
        "name": "reject_task",
        "description": "Discard uncommitted modifications and restore working tree cleanly.",
        "parameters": {
            "type": "object",
            "properties": {
                "workspace": {
                    "type": "string",
                    "description": "Target workspace directory to restore.",
                },
            },
        },
    },
    "list_supported_implementers": {
        "name": "list_supported_implementers",
        "description": "List all supported implementer agent names for cross-agent delegation.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}

TOOLS = {
    "delegate_task": delegate_task,
    "review_task": review_task,
    "land_task": land_task,
    "reject_task": reject_task,
    "list_supported_implementers": list_supported_implementers,
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
                    toolset="delegation_bridge",
                    schema=schema,
                    handler=make_handler(func),
                )
                continue
            except TypeError:
                pass

        try:
            ctx.register_tool(tool_name, func)
        except Exception:
            try:
                ctx.register_tool(name=tool_name, func=func)
            except Exception:
                pass
