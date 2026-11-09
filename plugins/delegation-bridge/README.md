# Delegation Bridge Plugin for Hermes Agent 🛡️

Review-First delegation framework enabling **Hermes Agent** to delegate coding tasks safely to implementer CLIs (Cursor, Codex, Antigravity, OpenCode, Kimi).

---

## 🔄 The 5-Step Review-First Lifecycle

1. **Brief Formulation**: Hermes formats an explicit task brief.
2. **Dispatch Relay**: `delegate_task` dispatches the task into an isolated workspace.
3. **Diff Capture**: `review_task` inspects `git diff` and file modifications.
4. **Interactive Verification**: You verify code quality before committing.
5. **Landing / Rejection**:
   - `land_task`: Stages and commits changes cleanly.
   - `reject_task`: Rolls back uncommitted changes cleanly.

---

## 🛠️ Provided Tools

- `delegate_task(agent, brief, cd, model, read_only, session)`
- `review_task(run_id, workspace)`
- `land_task(workspace, commit_message)`
- `reject_task(workspace)`
- `list_supported_implementers()`

---

## 📦 Installation for Hermes

Copy into:
```bash
~/.hermes/plugins/delegation-bridge/
```
Or execute:
```powershell
pwsh .\scripts\install-hermes.ps1
```
