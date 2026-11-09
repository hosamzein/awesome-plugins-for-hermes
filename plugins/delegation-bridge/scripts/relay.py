#!/usr/bin/env python3
"""
Universal Delegation Relay Engine (inspired by amElnagdy/delegate-skills)
Supports: Cursor, Codex, Antigravity, OpenCode, Claude, Kimi
Implements the Review-First delegation lifecycle:
  1. Write Brief -> 2. Dispatch Relay -> 3. Capture Diff -> 4. Review -> 5. Land
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from typing import Dict, Any, Optional, List

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

USER_HOME = os.path.expanduser("~")

AGENTS = {
    "cursor": {
        "exe": os.path.join(USER_HOME, r"AppData\Local\cursor-agent\cursor-agent.cmd"),
        "cmd_builder": lambda exe, brief, model, ro, session: (
            ["cmd.exe", "/c", exe, "-p", "--mode", "ask" if ro else "plan" if ro else "code", "--force", "--sandbox", "disabled"] +
            (["--model", model] if model else []) +
            (["--resume", session] if session else []) +
            [brief]
        ),
        "pipe_stdin": False
    },
    "codex": {
        "exe": os.path.join(USER_HOME, r"AppData\Roaming\npm\codex.cmd"),
        "cmd_builder": lambda exe, brief, model, ro, session: (
            ["cmd.exe", "/c", exe, "exec", "--ephemeral", "--skip-git-repo-check", "--ignore-rules", "--dangerously-bypass-approvals-and-sandbox"] +
            (["--sandbox", "read-only"] if ro else []) +
            (["-m", model] if model else []) +
            (["resume", session] if session else [])
        ),
        "pipe_stdin": True
    },
    "antigravity": {
        "exe": os.path.join(USER_HOME, r"AppData\Local\agy\bin\agy.exe"),
        "cmd_builder": lambda exe, brief, model, ro, session: (
            [exe, "-p", brief, "--dangerously-skip-permissions"] +
            (["--mode", "plan"] if ro else []) +
            (["--model", model] if model else []) +
            (["--continue"] if session == "last" else ["--conversation", session] if session else [])
        ),
        "pipe_stdin": False
    },
    "opencode": {
        "exe": os.path.join(USER_HOME, r"AppData\Roaming\npm\opencode.cmd"),
        "cmd_builder": lambda exe, brief, model, ro, session: (
            ["cmd.exe", "/c", exe, "run", "--auto"] +
            (["-m", model] if model else []) +
            (["--session", session] if session else []) +
            [brief]
        ),
        "pipe_stdin": False
    },
    "kimi": {
        "exe": os.path.join(USER_HOME, r".kimi-code\bin\kimi.exe"),
        "cmd_builder": lambda exe, brief, model, ro, session: (
            [exe, "-p", brief] +
            (["-m", model] if model else []) +
            (["--session", session] if session else [])
        ),
        "pipe_stdin": False
    }
}

def resolve_agent_exe(agent_name: str) -> str:
    name = agent_name.lower().strip()
    if name in AGENTS and os.path.exists(AGENTS[name]["exe"]):
        return AGENTS[name]["exe"]
    which = shutil.which(name)
    if which:
        return which
    if name == "antigravity":
        which_agy = shutil.which("agy")
        if which_agy:
            return which_agy
    if name == "cursor":
        which_cursor = shutil.which("cursor-agent")
        if which_cursor:
            return which_cursor
    if name in AGENTS:
        return AGENTS[name]["exe"]
    raise ValueError(f"Unknown agent '{agent_name}'. Supported: {list(AGENTS.keys())}")

def get_git_diff(cwd: str) -> str:
    try:
        res = subprocess.run(["git", "diff", "--stat"], cwd=cwd, capture_output=True, text=True, timeout=10)
        stat = res.stdout.strip()
        res_full = subprocess.run(["git", "diff"], cwd=cwd, capture_output=True, text=True, timeout=10)
        full = res_full.stdout.strip()
        return stat if not full else f"{stat}\n\n{full}"
    except Exception:
        return ""

def run_relay(agent: str, brief: str, cd: Optional[str] = None, model: Optional[str] = None, read_only: bool = False, session: Optional[str] = None, timeout: int = 3600) -> Dict[str, Any]:
    cwd = os.path.abspath(cd) if cd else os.getcwd()
    agent_key = agent.lower().strip()
    if agent_key not in AGENTS:
        raise ValueError(f"Unknown agent '{agent}'. Choose from: {list(AGENTS.keys())}")

    exe = resolve_agent_exe(agent_key)
    agent_cfg = AGENTS[agent_key]
    run_id = f"relay-{agent_key}-{uuid.uuid4().hex[:8]}"
    start_time = time.time()

    diff_before = get_git_diff(cwd)

    cmd = agent_cfg["cmd_builder"](exe, brief, model, read_only, session)
    stdin_bytes = brief.encode("utf-8") if agent_cfg["pipe_stdin"] else None

    print(f"[{run_id}] Dispatching to {agent_key.upper()} in {cwd}...", file=sys.stderr)
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdin=subprocess.PIPE if agent_cfg["pipe_stdin"] else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        stdout, stderr = proc.communicate(input=stdin_bytes, timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        return {
            "ok": False,
            "run_id": run_id,
            "agent": agent_key,
            "error": f"Execution timed out after {timeout} seconds",
            "duration": time.time() - start_time
        }

    raw_out = stdout.decode("utf-8", errors="replace").strip()
    raw_err = stderr.decode("utf-8", errors="replace").strip()
    duration = time.time() - start_time
    diff_after = get_git_diff(cwd)

    # Clean Codex output preamble if present
    clean_out = raw_out
    if agent_key == "codex" and "tokens used" in raw_out:
        lines = raw_out.splitlines()
        filtered = []
        skip = False
        for line in lines:
            if line.startswith("tokens used"):
                skip = True
                continue
            if skip:
                skip = False
                continue
            if line.startswith("OpenAI Codex") or line.startswith("--------") or line.startswith("workdir:") or line.startswith("model:") or line.startswith("provider:") or line.startswith("session id:") or line.startswith("approval:") or line.startswith("sandbox:") or line.startswith("reasoning ") or line.startswith("warning:"):
                continue
            if line in ["user", "codex"]:
                continue
            filtered.append(line)
        clean_out = "\n".join(filtered).strip()

    result = {
        "ok": proc.returncode == 0,
        "run_id": run_id,
        "agent": agent_key,
        "exit_code": proc.returncode,
        "duration_seconds": round(duration, 2),
        "output": clean_out or raw_err,
        "diff_detected": bool(diff_after != diff_before),
        "diff_summary": diff_after,
        "workspace": cwd
    }

    # Save result.json to workspace or temp
    result_path = os.path.join(tempfile.gettempdir(), f"{run_id}-result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    result["result_file"] = result_path

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Delegation Relay")
    parser.add_argument("--agent", required=True, choices=list(AGENTS.keys()), help="Target implementer agent")
    parser.add_argument("--brief", help="Inline brief instructions")
    parser.add_argument("--brief-file", help="Path to brief file")
    parser.add_argument("--cd", default=".", help="Target workspace directory")
    parser.add_argument("--model", help="Model override")
    parser.add_argument("--read-only", action="store_true", help="Read-only mode (diagnosis/review)")
    parser.add_argument("--session", help="Session ID to continue")
    parser.add_argument("--timeout", type=int, default=3600, help="Timeout in seconds")

    args = parser.parse_args()
    brief_content = args.brief
    if args.brief_file and os.path.exists(args.brief_file):
        with open(args.brief_file, "r", encoding="utf-8") as f:
            brief_content = f.read()

    if not brief_content:
        print("Error: Either --brief or --brief-file must be provided.", file=sys.stderr)
        sys.exit(1)

    res = run_relay(
        agent=args.agent,
        brief=brief_content,
        cd=args.cd,
        model=args.model,
        read_only=args.read_only,
        session=args.session,
        timeout=args.timeout
    )
    print(json.dumps(res, indent=2))
