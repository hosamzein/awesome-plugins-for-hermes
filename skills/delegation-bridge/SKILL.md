---
name: delegation-bridge
description: >
  Review-First cross-agent delegation lifecycle for Hermes Agent.
  Dispatches tasks to Cursor, Codex, Antigravity, OpenCode, or Kimi,
  tracks git diffs, and enforces interactive approval before committing.
metadata:
  target: hermes-agent
  version: "1.0.0"
---

# Delegation Bridge for Hermes Agent 🛡️

Implements the **Review-First** delegation protocol inspired by `amElnagdy/delegate-skills`:
1. **Dispatch**: Send self-contained task brief to implementer CLI.
2. **Review**: Inspect output, status, and `git diff`.
3. **Decision**: Approve and land (`git commit`) or reject cleanly (`git restore`).

## Available Tools

- `delegate_task(agent, brief, cd, model, read_only, session)`
- `review_task(run_id, workspace)`
- `land_task(workspace, commit_message)`
- `reject_task(workspace)`
- `list_supported_implementers()`

## CLI Relay Runner
```bash
# Delegate to Codex in read-only mode
py ~/.hermes/plugins/delegation-bridge/scripts/relay.py --agent codex --brief "Audit security issues" --read-only

# Delegate to Antigravity
py ~/.hermes/plugins/delegation-bridge/scripts/relay.py --agent antigravity --brief "Optimize database queries"
```
