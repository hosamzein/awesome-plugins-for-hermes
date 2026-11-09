# Subscription Bridge Plugin for Hermes Agent ⚡

Enables **Hermes Agent** to utilize local active subscriptions (Cursor Pro, OpenAI Codex, Google Antigravity, Anthropic Claude, Moonshot Kimi) at **$0.00 incremental token cost**.

---

## 🚀 How It Works

1. **Local Gateway**: Runs a lightweight OpenAI-compatible endpoint at `http://127.0.0.1:5288/v1`.
2. **Subscription Auth**: Reuses local authorized sessions (`~/.codex`, `~/.gemini`, `~/.claude`, `~/.kimi-code`).
3. **Hermes Integration**: Exposes model provider profiles and management tools:
   - `get_subscription_gateway_status()`
   - `list_subscription_models()`
   - `start_subscription_gateway()`

---

## 📦 Installation for Hermes

Copy into:
```bash
~/.hermes/plugins/subscription-bridge/
```
Or run:
```powershell
pwsh .\scripts\install-hermes.ps1
```
