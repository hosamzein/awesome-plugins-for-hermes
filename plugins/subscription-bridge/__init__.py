"""
Subscription Authorization Bridge Plugin for Hermes Agent
Registers Codex, Antigravity, Claude, and Kimi as zero-API-key model providers in Hermes Agent,
and exposes management tools.
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
        GATEWAY_PORT,
        GATEWAY_URL,
        is_gateway_running,
        start_subscription_gateway,
        get_subscription_gateway_status,
        list_subscription_models,
    )
except ImportError:
    from tools import (
        GATEWAY_PORT,
        GATEWAY_URL,
        is_gateway_running,
        start_subscription_gateway,
        get_subscription_gateway_status,
        list_subscription_models,
    )

# Auto-ensure gateway is running when plugin is loaded
start_subscription_gateway()

# Register native Hermes model providers if provider registry is present
try:
    from providers import register_provider
    from providers.base import ProviderProfile

    register_provider(
        ProviderProfile(
            id="codex",
            name="OpenAI Codex (Subscription Auth)",
            api_mode="chat_completions",
            base_url=GATEWAY_URL,
            env_vars=[],
            fallback_models=["codex/default", "codex/gpt-5", "codex/o3", "codex/o3-mini", "codex/gpt-4o"],
        )
    )

    register_provider(
        ProviderProfile(
            id="antigravity",
            name="Google Antigravity (Subscription Auth)",
            api_mode="chat_completions",
            base_url=GATEWAY_URL,
            env_vars=[],
            fallback_models=["antigravity/gemini-3.8-flash", "antigravity/gemini-3.8-pro"],
        )
    )

    register_provider(
        ProviderProfile(
            id="claude",
            name="Anthropic Claude (Subscription Auth)",
            api_mode="chat_completions",
            base_url=GATEWAY_URL,
            env_vars=[],
            fallback_models=["claude/claude-sonnet-5", "claude/claude-opus-4.8"],
        )
    )

    register_provider(
        ProviderProfile(
            id="kimi",
            name="Moonshot Kimi (Subscription Auth)",
            api_mode="chat_completions",
            base_url=GATEWAY_URL,
            env_vars=[],
            fallback_models=["kimi/kimi-code"],
        )
    )
except ImportError:
    pass

SCHEMAS = {
    "get_subscription_gateway_status": {
        "name": "get_subscription_gateway_status",
        "description": "Check if local zero-API-key subscription gateway is running and healthy on port 5288.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    "list_subscription_models": {
        "name": "list_subscription_models",
        "description": "List available zero-token subscription models (Codex, Antigravity, Claude, Kimi).",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    "start_subscription_gateway": {
        "name": "start_subscription_gateway",
        "description": "Start the background subscription authorization gateway daemon on port 5288.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}

TOOLS = {
    "get_subscription_gateway_status": get_subscription_gateway_status,
    "list_subscription_models": list_subscription_models,
    "start_subscription_gateway": start_subscription_gateway,
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
                    toolset="subscription_bridge",
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
