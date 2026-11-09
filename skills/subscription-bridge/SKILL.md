---
name: subscription-bridge
description: >
  Zero-API-key model provider bridge for Hermes Agent.
  Accesses Cursor Pro, OpenAI Codex, Google Antigravity, Anthropic Claude, and Moonshot Kimi
  via a local OpenAI-compatible endpoint on port 5288 at zero token billing.
metadata:
  target: hermes-agent
  version: "1.0.0"
---

# Subscription Bridge for Hermes Agent ⚡

Enables **Hermes Agent** to utilize active paid subscriptions at **$0.00 incremental token cost**.

## Available Tools

- `get_subscription_gateway_status()`: Health check for port 5288.
- `list_subscription_models()`: Discovers available zero-token model IDs.
- `start_subscription_gateway()`: Starts local gateway daemon if inactive.

## Gateway Endpoint
- **URL**: `http://127.0.0.1:5288/v1`
- **Models Endpoint**: `http://127.0.0.1:5288/v1/models`
- **Completions**: `http://127.0.0.1:5288/v1/chat/completions`
