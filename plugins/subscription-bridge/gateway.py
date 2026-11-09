import asyncio
import json
import logging
import os
import shutil
import sys
import time
import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

USER_HOME = os.path.expanduser("~")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("dsh-subscription-bridge")

app = FastAPI(title="DeepSeek Harness Subscription Bridge", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODELS = [
    {"id": "codex/default", "owned_by": "openai-subscription"},
    {"id": "codex/o3", "owned_by": "openai-subscription"},
    {"id": "codex/o3-mini", "owned_by": "openai-subscription"},
    {"id": "codex/gpt-4o", "owned_by": "openai-subscription"},
    {"id": "codex/gpt-5", "owned_by": "openai-subscription"},
    {"id": "antigravity/gemini-3.8-flash", "owned_by": "google-subscription"},
    {"id": "antigravity/gemini-3.8-pro", "owned_by": "google-subscription"},
    {"id": "claude/claude-sonnet-5", "owned_by": "anthropic-subscription"},
    {"id": "claude/claude-opus-4.8", "owned_by": "anthropic-subscription"},
    {"id": "cursor/composer-2.5", "owned_by": "cursor-subscription"},
    {"id": "kimi/kimi-code", "owned_by": "moonshot-subscription"},
    {"id": "opencode/default", "owned_by": "opencode-local"},
]

class ChatMessage(BaseModel):
    role: str
    content: Any

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None

def format_messages_for_prompt(messages: List[ChatMessage]) -> str:
    parts = []
    for msg in messages:
        role = msg.role.lower()
        content = msg.content
        if isinstance(content, list):
            text_items = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_items.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_items.append(item)
            content = "\n".join(text_items)
        else:
            content = str(content)
        
        if role == "system":
            parts.append(f"[System Instructions]\n{content}\n")
        elif role == "user":
            parts.append(f"User: {content}")
        elif role == "assistant":
            parts.append(f"Assistant: {content}")
    return "\n\n".join(parts)

async def run_codex(prompt: str, submodel: Optional[str] = None) -> str:
    exe = (
        shutil.which("codex")
        or os.path.join(USER_HOME, r"AppData\Roaming\npm\codex.cmd")
    )
    cmd = ["cmd.exe", "/c", exe, "exec", "--ephemeral", "--skip-git-repo-check", "--ignore-rules", "--dangerously-bypass-approvals-and-sandbox"]
    if submodel and submodel != "default":
        cmd.extend(["-m", submodel])
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate(input=prompt.encode("utf-8"))
    out_text = stdout.decode("utf-8", errors="replace").strip()
    if "tokens used" in out_text:
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
            if line in ["user", "codex"]:
                continue
            filtered.append(line)
        return "\n".join(filtered).strip()
    return out_text

async def run_antigravity(prompt: str, submodel: Optional[str] = None) -> str:
    exe = (
        shutil.which("agy")
        or os.path.join(USER_HOME, r"AppData\Local\agy\bin\agy.exe")
    )
    cmd = [exe, "-p", prompt, "--dangerously-skip-permissions"]
    if submodel and "flash" in submodel:
        cmd.extend(["--model", "gemini-3.8-flash"])
    elif submodel and "pro" in submodel:
        cmd.extend(["--model", "gemini-3.8-pro"])
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode("utf-8", errors="replace").strip()

async def run_kimi(prompt: str, submodel: Optional[str] = None) -> str:
    exe = (
        shutil.which("kimi")
        or os.path.join(USER_HOME, r".kimi-code\bin\kimi.exe")
    )
    cmd = [exe, "-p", prompt]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    out = stdout.decode("utf-8", errors="replace").strip()
    err = stderr.decode("utf-8", errors="replace").strip()
    return out or f"[Kimi Notice]: {err}"

async def run_claude(messages: List[ChatMessage], submodel: Optional[str] = None) -> str:
    claude_settings_path = os.path.expanduser(r"~\.claude\settings.json")
    base_url = "https://openrouter.ai/api"
    token = ""
    target_model = "anthropic/claude-sonnet-5"
    if os.path.exists(claude_settings_path):
        try:
            with open(claude_settings_path, "r", encoding="utf-8") as f:
                env = json.load(f).get("env", {})
                base_url = env.get("ANTHROPIC_BASE_URL", base_url)
                token = env.get("ANTHROPIC_AUTH_TOKEN", "")
                if submodel and "opus" in submodel:
                    target_model = env.get("ANTHROPIC_DEFAULT_OPUS_MODEL", "anthropic/claude-opus-4.8")
                else:
                    target_model = env.get("ANTHROPIC_DEFAULT_SONNET_MODEL", target_model)
        except Exception:
            pass
    url = f"{base_url.rstrip('/')}/chat/completions" if "/v1" in base_url else f"{base_url.rstrip('/')}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "model": target_model,
        "messages": [{"role": m.role, "content": m.content} for m in messages]
    }
    async with httpx.AsyncClient(timeout=90.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

async def run_cursor(prompt: str, submodel: Optional[str] = None) -> str:
    exe = (
        shutil.which("cursor-agent")
        or os.path.join(USER_HOME, r"AppData\Local\cursor-agent\cursor-agent.cmd")
    )
    cmd = ["cmd.exe", "/c", exe, "-p", "--force", "--sandbox", "disabled"]
    if submodel:
        cmd.extend(["--model", submodel])
    cmd.append(prompt)
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode("utf-8", errors="replace").strip()

@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": m["id"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": m["owned_by"],
            }
            for m in MODELS
        ]
    }

@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    model_name = request.model.lower()
    prompt_str = format_messages_for_prompt(request.messages)
    
    provider = "codex"
    submodel = None
    if "/" in model_name:
        provider, submodel = model_name.split("/", 1)
    elif "cursor" in model_name:
        provider = "cursor"
    elif "antigravity" in model_name or "gemini" in model_name:
        provider = "antigravity"
    elif "claude" in model_name:
        provider = "claude"
    elif "kimi" in model_name:
        provider = "kimi"
        
    try:
        if provider == "codex":
            content = await run_codex(prompt_str, submodel)
        elif provider == "antigravity":
            content = await run_antigravity(prompt_str, submodel)
        elif provider == "claude":
            content = await run_claude(request.messages, submodel)
        elif provider == "kimi":
            content = await run_kimi(prompt_str, submodel)
        elif provider == "cursor":
            content = await run_cursor(prompt_str, submodel)
        else:
            content = await run_codex(prompt_str, submodel)
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created_ts = int(time.time())
    
    if request.stream:
        async def event_generator() -> AsyncGenerator[str, None]:
            chunk_init = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created_ts,
                "model": request.model,
                "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}]
            }
            yield f"data: {json.dumps(chunk_init)}\n\n"
            words = content.split(" ")
            for i, word in enumerate(words):
                delta = word + (" " if i < len(words) - 1 else "")
                chunk = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created_ts,
                    "model": request.model,
                    "choices": [{"index": 0, "delta": {"content": delta}, "finish_reason": None}]
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.01)
            yield f"data: {json.dumps({'id': completion_id, 'object': 'chat.completion.chunk', 'created': created_ts, 'model': request.model, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(event_generator(), media_type="text/event-stream")

    return {
        "id": completion_id,
        "object": "chat.completion",
        "created": created_ts,
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": len(prompt_str) // 4,
            "completion_tokens": len(content) // 4,
            "total_tokens": (len(prompt_str) + len(content)) // 4
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5288, log_level="info")
