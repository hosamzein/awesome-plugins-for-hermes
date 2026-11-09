---
name: cli-bridge
description: >
  Delegate and execute coding, research, or automation tasks from Hermes Agent across local CLI clients:
  Cursor Agent, OpenAI Codex CLI, Google Antigravity (AGY), OpenCode CLI, and Moonshot Kimi.
metadata:
  target: hermes-agent
  version: "1.0.0"
---

# CLI Bridge for Hermes Agent

Universal execution bridge connecting **Hermes Agent** to existing local CLI coding engines:
- **Cursor** (`cursor-agent`)
- **Codex** (`codex exec`)
- **Antigravity** (`agy -p`)
- **OpenCode** (`opencode run`)
- **Kimi** (`kimi -p`)

## CLI Direct Invocation

Check client status:
```bash
py ~/.hermes/plugins/cli-bridge/bridge.py status
```

Execute on a client:
```bash
# Codex
py ~/.hermes/plugins/cli-bridge/bridge.py run codex "Write unit tests for auth module"

# Antigravity (Gemini)
py ~/.hermes/plugins/cli-bridge/bridge.py run antigravity "Analyze memory performance"

# Cursor
py ~/.hermes/plugins/cli-bridge/bridge.py run cursor "Refactor main.ts"

# OpenCode
py ~/.hermes/plugins/cli-bridge/bridge.py run opencode "Review recent git diff"

# Kimi
py ~/.hermes/plugins/cli-bridge/bridge.py run kimi "Summarize architecture"
```

## Python Integration in Hermes
```python
from tools import cli_bridge, run_codex, run_antigravity, run_cursor, run_opencode, run_kimi

# Run task
response = cli_bridge(client="codex", prompt="Create a unit test for auth.py")
```
