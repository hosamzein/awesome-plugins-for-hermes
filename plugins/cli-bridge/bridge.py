"""
Hermes Agent CLI Bridge Subprocess Runner
Executes prompts against local Cursor, Codex, Antigravity, OpenCode, and Kimi CLI engines.
"""

import os
import sys
import shutil
import subprocess
from typing import Dict, Any, Optional

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

USER_HOME = os.path.expanduser("~")

CLIENT_PATHS = {
    "cursor": os.path.join(USER_HOME, r"AppData\Local\cursor-agent\cursor-agent.cmd"),
    "codex": os.path.join(USER_HOME, r"AppData\Roaming\npm\codex.cmd"),
    "antigravity": os.path.join(USER_HOME, r"AppData\Local\agy\bin\agy.exe"),
    "opencode": os.path.join(USER_HOME, r"AppData\Roaming\npm\opencode.cmd"),
    "kimi": os.path.join(USER_HOME, r".kimi-code\bin\kimi.exe"),
}

def get_client_executable(client: str) -> Optional[str]:
    client = client.lower().strip()
    if client in CLIENT_PATHS and os.path.exists(CLIENT_PATHS[client]):
        return CLIENT_PATHS[client]
    which = shutil.which(client)
    if which:
        return which
    if client == "antigravity":
        return shutil.which("agy")
    if client == "cursor":
        return shutil.which("cursor-agent")
    if client == "kimi":
        return shutil.which("kimi")
    return None

def check_status() -> Dict[str, Dict[str, Any]]:
    results = {}
    for name in ["cursor", "codex", "antigravity", "opencode", "kimi"]:
        exe = get_client_executable(name)
        available = exe is not None and os.path.exists(exe)
        results[name] = {
            "available": available,
            "path": exe,
        }
    return results

def run_client(
    client: str,
    prompt: str,
    model: Optional[str] = None,
    workspace: Optional[str] = None,
    timeout: int = 120
) -> str:
    exe = get_client_executable(client)
    if not exe:
        raise FileNotFoundError(f"Client '{client}' is not installed or not found on host.")

    cwd = workspace or os.getcwd()
    cmd = []
    stdin_data = None

    client_key = client.lower().strip()
    if client_key == "cursor":
        cmd = ["cmd.exe", "/c", exe, "-p", "--force", "--sandbox", "disabled"]
        if model:
            cmd.extend(["--model", model])
        cmd.append(prompt)
    elif client_key == "codex":
        cmd = [
            "cmd.exe", "/c", exe, "exec",
            "--ephemeral",
            "--skip-git-repo-check",
            "--ignore-rules",
            "--dangerously-bypass-approvals-and-sandbox"
        ]
        if model:
            cmd.extend(["-m", model])
        stdin_data = prompt.encode("utf-8")
    elif client_key in ["antigravity", "agy"]:
        cmd = [exe, "-p", prompt, "--dangerously-skip-permissions"]
        if model:
            cmd.extend(["--model", model])
    elif client_key == "opencode":
        cmd = ["cmd.exe", "/c", exe, "run", "--auto"]
        if model:
            cmd.extend(["-m", model])
        cmd.append(prompt)
    elif client_key == "kimi":
        cmd = [exe, "-p", prompt]
        if model:
            cmd.extend(["-m", model])
    else:
        raise ValueError(f"Unknown client '{client}'. Supported: cursor, codex, antigravity, opencode, kimi")

    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdin=subprocess.PIPE if stdin_data else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = proc.communicate(input=stdin_data, timeout=timeout)
    out_text = stdout.decode("utf-8", errors="replace").strip()
    err_text = stderr.decode("utf-8", errors="replace").strip()

    if proc.returncode != 0 and not out_text:
        return f"[Error from {client} (exit {proc.returncode})]: {err_text}"

    if client_key == "codex" and "tokens used" in out_text:
        lines = out_text.splitlines()
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
            if line == "user" or line == "codex":
                continue
            filtered.append(line)
        return "\n".join(filtered).strip()

    return out_text
