# CLI Bridge Plugin for Hermes Agent 🚀

Universal CLI execution bridge that connects **Hermes Agent** directly to local coding agent CLIs:
- **Cursor Agent** (`cursor-agent.cmd`)
- **OpenAI Codex** (`codex.cmd`)
- **Google Antigravity** (`agy.exe`)
- **OpenCode** (`opencode.cmd`)
- **Moonshot Kimi** (`kimi.exe`)

---

## 🛠️ Provided Tools

1. `cli_bridge(client, prompt, model, workspace)`: Execute any task against a specific CLI engine.
2. `run_cursor(prompt, model)`: Quick runner for Cursor Agent.
3. `run_codex(prompt, model)`: Quick runner for OpenAI Codex.
4. `run_antigravity(prompt, model)`: Quick runner for Google Antigravity.
5. `run_opencode(prompt, model)`: Quick runner for OpenCode.
6. `run_kimi(prompt, model)`: Quick runner for Moonshot Kimi.
7. `list_available_clients()`: Discover installed CLI clients and paths.

---

## 📦 Installation for Hermes

Copy into your Hermes plugins directory:
```bash
~/.hermes/plugins/cli-bridge/
```
Or run the Hermes installer:
```powershell
pwsh .\scripts\install-hermes.ps1
```
