import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
import urllib.parse
import zipfile
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw

try:
    import google as google_namespace
except ImportError:
    google_namespace = None

try:
    from googlesearch import search as google_search
except ImportError:
    google_search = None


def _load_streamlit_secrets_to_env():
    keys = [
        "GROQ_API_KEY",
        "GROQ_API_KEYS",
        "COMETAPI_API_KEY",
        "HF_TOKEN",
        "HUGGINGFACE_TOKEN",
        "XAI_API_KEY",
        "XAI_API_TOKEN",
        "NVIDIA_API_KEY",
        "NVIDIA_NIM_API_KEY",
        "NVIDIA_NGC_API_KEY",
    ]
    try:
        secrets = st.secrets
    except Exception:
        return
    for key in keys:
        try:
            value = secrets.get(key)
        except Exception:
            value = None
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            value = ",".join(str(item) for item in value if item)
        value = str(value).strip()
        if value and not os.environ.get(key):
            os.environ[key] = value


_load_streamlit_secrets_to_env()

import lightsky_core as core


APP_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = APP_DIR / "downloads"
PLUGIN_DIR = APP_DIR / "github_plugins"
GENERATED_DIR = APP_DIR / "generated_images"
INTERTEST_DIR = APP_DIR / "intertest_runs"

for folder in (DOWNLOAD_DIR, PLUGIN_DIR, GENERATED_DIR, INTERTEST_DIR):
    folder.mkdir(exist_ok=True)


st.set_page_config(
    page_title="Lightsky AI pro by krivi",
    page_icon="\u2728",
    layout="wide",
    initial_sidebar_state="expanded",
)


CSS = """
<style>
:root {
  --bg: #f5f7fb;
  --panel: #ffffff;
  --soft: #eef2f8;
  --line: #dfe6f1;
  --text: #172033;
  --muted: #687386;
  --blue: #2563eb;
  --violet: #7c3aed;
  --pink: #db2777;
  --green: #16a34a;
  --gold: #ca8a04;
  --siri-gradient: linear-gradient(100deg, #67e8f9, #60a5fa, #a78bfa, #f472b6, #fb7185, #facc15, #4ade80, #67e8f9);
}
.stApp {
  background: radial-gradient(circle at 30% -10%, rgba(37,99,235,.10), transparent 34%),
              radial-gradient(circle at 90% 10%, rgba(219,39,119,.08), transparent 30%),
              var(--bg);
  color: var(--text);
}
[data-testid="stSidebar"] {
  position: relative;
  background: linear-gradient(180deg, #eef2f8 0%, #f8fafc 100%);
  border-right: 1px solid var(--line);
}
[data-testid="stSidebar"]::after {
  content: "";
  position: absolute;
  top: 18px;
  right: 0;
  bottom: 18px;
  width: 2px;
  border-radius: 999px;
  background: var(--siri-gradient);
  background-size: 320% 320%;
  animation: siriFlow 8s ease-in-out infinite;
  opacity: .8;
}
[data-testid="stSidebar"] * {
  font-family: "Segoe UI", system-ui, sans-serif;
}
.main .block-container {
  max-width: 1320px;
  padding-top: 1.2rem;
  padding-bottom: 4rem;
}
h1, h2, h3, p, label, span, div {
  font-family: "Segoe UI", system-ui, sans-serif;
}
.hero {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 18px 22px;
  border: 1px solid var(--line);
  border-radius: 28px;
  background: rgba(255,255,255,.82);
  box-shadow: 0 18px 46px rgba(17, 24, 39, .07);
  backdrop-filter: blur(14px);
}
.hero::after {
  content: "";
  position: absolute;
  left: 22px;
  right: 22px;
  bottom: 0;
  height: 2px;
  border-radius: 999px;
  background: var(--siri-gradient);
  background-size: 320% 320%;
  animation: siriFlow 9s ease-in-out infinite;
  opacity: .54;
}
.brand {
  display: flex;
  align-items: center;
  gap: 14px;
}
.logo {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  color: #111827;
  background: var(--siri-gradient);
  background-size: 320% 320%;
  animation: siriFlow 9s ease-in-out infinite;
  box-shadow: inset 0 0 0 1px #dbe3ef, 0 10px 24px rgba(37,99,235,.13);
  font-size: 25px;
}
.brand-title {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 760;
  letter-spacing: 0;
}
.brand-subtitle {
  color: var(--muted);
  margin-top: 2px;
  font-size: .92rem;
}
.status-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin: 14px 0 18px;
}
.status-card, .soft-card {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 22px;
  background: rgba(255,255,255,.88);
  box-shadow: 0 14px 34px rgba(17, 24, 39, .055);
}
.status-card {
  padding: 12px 14px;
}
.status-card::before, .soft-card::before {
  content: "";
  position: absolute;
  left: 12px;
  right: 12px;
  top: 0;
  height: 2px;
  border-radius: 999px;
  background: var(--siri-gradient);
  background-size: 320% 320%;
  animation: siriFlow 10s ease-in-out infinite;
  opacity: .58;
}
.status-label {
  color: var(--muted);
  font-size: .74rem;
  text-transform: uppercase;
  font-weight: 750;
  letter-spacing: .04em;
}
.status-value {
  margin-top: 4px;
  font-weight: 760;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.soft-card {
  padding: 18px;
  margin-bottom: 14px;
}
.siri-line {
  height: 0;
  border-radius: 999px;
  margin: 8px 0 2px;
}
@keyframes siriFlow {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes siriPulse {
  0%, 100% { opacity: .72; transform: scaleX(.96); }
  50% { opacity: 1; transform: scaleX(1); }
}
.stButton > button, .stDownloadButton > button {
  border-radius: 999px !important;
  border: 1px solid transparent !important;
  background: linear-gradient(#ffffff, #ffffff) padding-box, var(--siri-gradient) border-box !important;
  background-size: auto, 320% 320% !important;
  color: #172033 !important;
  font-weight: 700 !important;
  box-shadow: 0 8px 22px rgba(17, 24, 39, .055);
}
.stButton > button:hover, .stDownloadButton > button:hover {
  background: linear-gradient(#f8fbff, #f8fbff) padding-box, var(--siri-gradient) border-box !important;
  animation: siriFlow 6s ease-in-out infinite;
}
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  border-radius: 18px !important;
  border: 1px solid transparent !important;
  background: linear-gradient(#ffffff, #ffffff) padding-box, var(--siri-gradient) border-box !important;
  background-size: auto, 320% 320% !important;
  box-shadow: 0 8px 22px rgba(17, 24, 39, .045) !important;
}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  animation: siriFlow 7s ease-in-out infinite;
  box-shadow: 0 0 0 3px rgba(96,165,250,.12), 0 10px 28px rgba(17, 24, 39, .06) !important;
}
[data-testid="stChatMessage"] {
  position: relative;
  border-radius: 22px;
}
[data-testid="stChatMessage"]::before {
  content: "";
  position: absolute;
  left: 0;
  top: 14px;
  bottom: 14px;
  width: 3px;
  border-radius: 999px;
  background: var(--siri-gradient);
  background-size: 260% 260%;
  animation: siriFlow 10s ease-in-out infinite;
  opacity: .34;
}
[data-testid="stChatInput"] {
  position: relative;
  border-radius: 34px !important;
  padding: 2px !important;
  background: var(--siri-gradient);
  background-size: 320% 320%;
  animation: siriFlow 7s ease-in-out infinite;
  box-shadow: 0 18px 52px rgba(17, 24, 39, .10), 0 0 24px rgba(124, 58, 237, .14);
}
[data-testid="stChatInput"] > div {
  border-radius: 32px !important;
  background: rgba(255, 255, 255, .96) !important;
  overflow: hidden;
}
[data-testid="stChatInput"]::after {
  content: "";
  position: absolute;
  left: 24px;
  right: 78px;
  bottom: 7px;
  height: 3px;
  border-radius: 999px;
  pointer-events: none;
  background: linear-gradient(90deg, #67e8f9, #60a5fa, #a78bfa, #f472b6, #fb7185, #facc15, #4ade80);
  background-size: 260% 260%;
  animation: siriFlow 4s ease-in-out infinite, siriPulse 2.8s ease-in-out infinite;
  filter: saturate(1.14);
}
[data-testid="stChatInput"] textarea {
  min-height: 58px !important;
  border-radius: 32px !important;
  border: 0 !important;
  background: rgba(255,255,255,.96) !important;
  box-shadow: inset 0 0 0 1px rgba(216, 224, 236, .86) !important;
  padding-bottom: 17px !important;
}
[data-testid="stChatInput"] textarea:focus {
  box-shadow: inset 0 0 0 1px rgba(124, 58, 237, .24), 0 0 0 0 transparent !important;
  outline: none !important;
}
.source-item {
  color: var(--muted);
  font-size: .9rem;
  border-left: 3px solid #dbeafe;
  padding-left: 10px;
  margin: 8px 0;
}
.codebox {
  border-radius: 18px;
  border: 1px solid var(--line);
  background: #0f172a;
  color: #e5e7eb;
  padding: 14px;
  overflow-x: auto;
}
@media (max-width: 900px) {
  .status-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .hero { align-items: flex-start; flex-direction: column; }
}
</style>
"""


st.markdown(CSS, unsafe_allow_html=True)


def render_iframe(url, height=680, scrolling=True):
    if hasattr(st, "iframe"):
        st.iframe(url, height=height, scrolling=scrolling)
    else:
        components.iframe(url, height=height, scrolling=scrolling)


def provider_display(provider):
    return core.provider_display_name(provider)


def model_clean(display):
    return (
        display.replace("Groq / ", "")
        .replace("CometAPI / ", "")
        .replace("Hugging Face / ", "")
        .replace("xAI / ", "")
        .replace("NVIDIA / ", "")
    )


def route_from_display(display):
    config = core.MODEL_OPTIONS.get(display, core.DEFAULT_MODEL_CONFIG)
    return {
        "display": display,
        "provider": config.get("provider", "groq"),
        "model": config.get("model"),
        "system_prompt": config.get("system_prompt", "You are Lightsky AI pro by krivi, a helpful assistant."),
        "temperature": config.get("temperature", 0.7),
    }


def call_selected_model(prompt, route, max_tokens=700, web=True):
    sources = []
    model_prompt = prompt
    if web and core.lightsky_should_search_web(prompt):
        context, sources = core.lightsky_build_universal_web_context(prompt, max_results=core.LS51_MAX_WEB_CONTEXT_RESULTS)
        if context:
            model_prompt = (
                "Use this live web context directly and cite URLs when relevant.\n\n"
                f"{context}\n\nUser request:\n{prompt}"
            )

    response = core.get_provider_response(
        model_prompt,
        provider=route["provider"],
        model=route["model"],
        max_tokens=max_tokens,
        system_prompt=route.get("system_prompt"),
        temperature=route.get("temperature"),
    )
    return response, sources


def _python_command():
    return "py" if shutil.which("py") else sys.executable


def _normalize_args(value):
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item).strip()]
    try:
        return shlex.split(str(value))
    except Exception:
        return [str(value)]


def _safe_intertest_cwd(value=None):
    if not value:
        return APP_DIR
    try:
        candidate = Path(str(value)).expanduser().resolve()
        candidate.relative_to(APP_DIR)
        return candidate
    except Exception:
        return APP_DIR


def _blocked_intertest_command(command):
    lowered = (command or "").lower()
    blocked = [
        r"\bremove-item\b.*\b-recurse\b",
        r"\brm\s+-rf\b",
        r"\brmdir\s+/s\b",
        r"\bdel\s+/s\b",
        r"\bformat\b",
        r"\bshutdown\b",
        r"\brestart-computer\b",
        r"\bset-executionpolicy\b",
        r"\breg\s+(delete|add)\b",
        r"\binvoke-expression\b",
        r"\biex\b",
        r"\|\s*(sh|bash|powershell|pwsh|iex)\b",
    ]
    for pattern in blocked:
        if re.search(pattern, lowered):
            return f"Blocked risky command pattern: {pattern}"
    return ""


def _run_process(cmd, cwd=None, timeout=60):
    started = datetime.now().isoformat(timespec="seconds")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(_safe_intertest_cwd(cwd)),
            text=True,
            capture_output=True,
            timeout=max(1, min(int(timeout or 60), 180)),
        )
        return {
            "ok": result.returncode == 0,
            "exit_code": result.returncode,
            "cmd": cmd,
            "cwd": str(_safe_intertest_cwd(cwd)),
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
            "started": started,
            "finished": datetime.now().isoformat(timespec="seconds"),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "exit_code": "timeout",
            "cmd": cmd,
            "cwd": str(_safe_intertest_cwd(cwd)),
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or f"Timed out after {timeout} seconds.",
            "started": started,
            "finished": datetime.now().isoformat(timespec="seconds"),
        }
    except Exception as exc:
        return {
            "ok": False,
            "exit_code": "error",
            "cmd": cmd,
            "cwd": str(_safe_intertest_cwd(cwd)),
            "stdout": "",
            "stderr": str(exc),
            "started": started,
            "finished": datetime.now().isoformat(timespec="seconds"),
        }


def run_python_code_intertest(code, filename=None, args=None, timeout=60):
    if not (code or "").strip():
        return {"ok": False, "exit_code": "error", "stdout": "", "stderr": "No Python code was provided."}
    run_dir = INTERTEST_DIR / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    run_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", filename or "ai_intertest.py")
    if not safe_name.endswith(".py"):
        safe_name += ".py"
    script_path = run_dir / safe_name
    script_path.write_text(code, encoding="utf-8")
    cmd = [_python_command(), str(script_path)] + _normalize_args(args)
    result = _run_process(cmd, cwd=run_dir, timeout=timeout)
    result["script_path"] = str(script_path)
    result["action"] = "python_code"
    return result


def run_python_file_intertest(path, args=None, cwd=None, timeout=120):
    if not path:
        return {"ok": False, "exit_code": "error", "stdout": "", "stderr": "No Python file path was provided."}
    target = Path(str(path)).expanduser()
    if not target.is_absolute():
        target = _safe_intertest_cwd(cwd) / target
    cmd = [_python_command(), str(target)] + _normalize_args(args)
    result = _run_process(cmd, cwd=cwd, timeout=timeout)
    result["action"] = "python_file"
    return result


def run_command_intertest(command, cwd=None, timeout=60):
    if not (command or "").strip():
        return {"ok": False, "exit_code": "error", "stdout": "", "stderr": "No command was provided."}
    blocked = _blocked_intertest_command(command)
    if blocked:
        return {"ok": False, "exit_code": "blocked", "cmd": command, "stdout": "", "stderr": blocked, "action": "command"}
    if os.name == "nt":
        cmd = ["powershell", "-NoProfile", "-Command", command]
    else:
        cmd = ["bash", "-lc", command]
    result = _run_process(cmd, cwd=cwd, timeout=timeout)
    result["action"] = "command"
    return result


def run_intertest_tool_call(tool_call):
    action = str(tool_call.get("action") or tool_call.get("tool") or "").strip().lower()
    timeout = tool_call.get("timeout", 60)
    if action in {"python_code", "run_python_code", "intertest", "code"}:
        return run_python_code_intertest(
            tool_call.get("code") or tool_call.get("script") or "",
            filename=tool_call.get("filename"),
            args=tool_call.get("args"),
            timeout=timeout,
        )
    if action in {"python", "python_file", "run_python"}:
        return run_python_file_intertest(
            tool_call.get("path"),
            args=tool_call.get("args"),
            cwd=tool_call.get("cwd"),
            timeout=timeout,
        )
    if action in {"command", "powershell", "shell"}:
        return run_command_intertest(tool_call.get("command"), cwd=tool_call.get("cwd"), timeout=timeout)
    return {
        "ok": False,
        "exit_code": "unsupported",
        "stdout": "",
        "stderr": f"Unsupported Inter-Test action: {action or 'missing'}",
        "action": action or "missing",
    }


def extract_intertest_tool_call(text):
    if not text:
        return None
    patterns = [
        r"```ls_tool_call\s*(.*?)```",
        r"```json\s*(\{.*?\"action\".*?\})\s*```",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.I | re.S):
            body = match.group(1).strip()
            try:
                data = json.loads(body)
                if isinstance(data, dict) and (data.get("action") or data.get("tool")):
                    return data
            except Exception:
                continue
    return None


def strip_intertest_tool_blocks(text):
    text = re.sub(r"```ls_tool_call\s*.*?```", "", text or "", flags=re.I | re.S).strip()
    return text or "The selected model requested an Inter-Test run."


def format_intertest_result(result, max_chars=5000):
    stdout = (result.get("stdout") or "").strip()
    stderr = (result.get("stderr") or "").strip()
    output = []
    output.append(f"Action: {result.get('action', 'intertest')}")
    output.append(f"Exit code: {result.get('exit_code')}")
    if result.get("script_path"):
        output.append(f"Script: {result.get('script_path')}")
    if result.get("cmd"):
        cmd = result.get("cmd")
        if isinstance(cmd, (list, tuple)):
            output.append("Command: " + " ".join(str(part) for part in cmd))
        else:
            output.append("Command: " + str(cmd))
    if stdout:
        output.append("\nSTDOUT:\n" + stdout[:max_chars])
    if stderr:
        output.append("\nSTDERR:\n" + stderr[:max_chars])
    if not stdout and not stderr:
        output.append("\nNo output.")
    return "\n".join(output)


def run_model_with_intertest(prompt, route, max_tokens=900, web=True):
    response, sources = call_selected_model(prompt, route, max_tokens=max_tokens, web=web)
    tool_call = extract_intertest_tool_call(response)
    if not tool_call:
        return response, sources, None

    if not st.session_state.get("ai_intertest_enabled", True):
        notice = (
            strip_intertest_tool_blocks(response)
            + "\n\nInter-Test request detected, but AI Inter-Test access is turned off in the sidebar."
        )
        return notice, sources, None

    tool_result = run_intertest_tool_call(tool_call)
    st.session_state.intertest_runs.append(
        {
            "model": route.get("display"),
            "tool_call": tool_call,
            "result": tool_result,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
    )
    followup = f"""
The selected model requested an Inter-Test run. Here is the original request, your draft, and the actual tool output.

Original user request:
{prompt}

Model draft:
{strip_intertest_tool_blocks(response)}

Inter-Test result:
{format_intertest_result(tool_result)}

Now give the final answer. Use the test result directly. Do not request another tool call.
"""
    final_response, _ = call_selected_model(followup.strip(), route, max_tokens=max_tokens, web=False)
    return final_response or strip_intertest_tool_blocks(response), sources, tool_result


def status_cards(route):
    tool_status = "Inter-Test on" if st.session_state.get("ai_intertest_enabled", True) else "Inter-Test off"
    st.markdown(
        f"""
        <div class="status-grid">
          <div class="status-card"><div class="status-label">Model</div><div class="status-value">{model_clean(route['display'])}</div></div>
          <div class="status-card"><div class="status-label">Provider</div><div class="status-value">{provider_display(route['provider'])}</div></div>
          <div class="status-card"><div class="status-label">Web</div><div class="status-value">available to all models</div></div>
          <div class="status-card"><div class="status-label">Tools</div><div class="status-value">{tool_status}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header(route):
    st.markdown(
        f"""
        <div class="hero">
          <div class="brand">
            <div class="logo">&#10024;</div>
            <div>
              <div class="brand-title">Lightsky AI pro</div>
              <div class="brand-subtitle">by Krivi</div>
            </div>
          </div>
          <div style="color:#687386;font-weight:650;">{provider_display(route['provider'])} / {model_clean(route['display'])}</div>
        </div>
        <div class="siri-line"></div>
        """,
        unsafe_allow_html=True,
    )
    status_cards(route)


def init_state():
    st.session_state.setdefault("messages", [
        {
            "role": "assistant",
            "content": "Chat is ready. Pick any model and I will answer from exactly that selected model.",
            "source": "Lightsky AI pro",
            "sources": [],
        }
    ])
    st.session_state.setdefault("arena_log", [])
    st.session_state.setdefault("look_results", [])
    st.session_state.setdefault("look_details", "")
    st.session_state.setdefault("github_results", [])
    st.session_state.setdefault("last_download", None)
    st.session_state.setdefault("intertest_runs", [])
    st.session_state.setdefault("ai_intertest_enabled", True)


def append_sources(response, sources):
    if not sources:
        return response
    if any(src.get("url") and src["url"] in response for src in sources):
        return response
    lines = ["\n\nSources:"]
    for src in sources[:4]:
        lines.append(f"- {src.get('title', 'Source')} - {src.get('url', '')}")
    return response + "\n".join(lines)


def chat_screen(route):
    render_header(route)
    for item in st.session_state.messages:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
            if item.get("sources"):
                with st.expander("Sources"):
                    for src in item["sources"]:
                        st.markdown(f"<div class='source-item'><b>{src.get('title','Source')}</b><br>{src.get('url','')}</div>", unsafe_allow_html=True)
            if item.get("intertest"):
                with st.expander("Inter-Test run"):
                    st.code(format_intertest_result(item["intertest"]), language="text")

    prompt = st.chat_input("Ask for follow-up changes")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt, "source": "You", "sources": []})
        with st.spinner(f"\u2728 {provider_display(route['provider'])} / {model_clean(route['display'])} is thinking..."):
            response, sources, intertest_result = run_model_with_intertest(prompt, route, max_tokens=900, web=True)
            response = append_sources(response or "The selected model did not return a response.", sources)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "source": f"{provider_display(route['provider'])} / {model_clean(route['display'])}",
            "sources": sources,
            "intertest": intertest_result,
        })
        st.rerun()


def arena_screen(route):
    render_header(route)
    st.markdown("### Arena")
    left, right = st.columns([1, 1])
    with left:
        topic = st.text_input("Topic", value="Should LS 5.1 search the web before answering factual questions?")
        mode = st.selectbox("Debate mode", ["brainstorm", "adversarial debate", "consensus", "mentor panel"])
        rounds = st.slider("Rounds", 1, 5, 2)
    with right:
        agent_count = st.slider("Agents", 2, 5, 3)
        length = st.select_slider("Response length", options=["short", "medium", "long"], value="medium")
        interruption = st.text_area("Interruption / redirect", placeholder="Jump in mid-conversation and redirect all agents...")

    agents = ["Nova", "Orion", "Vega", "Atlas", "Mira"][:agent_count]
    token_map = {"short": 180, "medium": 320, "long": 520}
    if st.button("Start arena", type="primary"):
        st.session_state.arena_log = []
        shared_context = []
        with st.spinner("\u2728 Arena running..."):
            for round_index in range(1, rounds + 1):
                for agent in agents:
                    prior = "\n".join(shared_context[-10:])
                    prompt = f"""
You are {agent}, a distinct chatbot in Lightsky Arena.
Mode: {mode}
Topic: {topic}
Round: {round_index}/{rounds}
Shared context board:
{prior or 'No prior messages yet.'}
User interruption:
{interruption or 'None'}

Respond as {agent}. Cite or challenge prior messages when useful. Avoid repetition.
"""
                    answer, _ = call_selected_model(prompt.strip(), route, max_tokens=token_map[length], web=False)
                    message = {"agent": agent, "round": round_index, "content": answer}
                    st.session_state.arena_log.append(message)
                    shared_context.append(f"{agent}: {answer}")

    if st.session_state.arena_log:
        for item in st.session_state.arena_log:
            st.markdown(f"**Round {item['round']} / {item['agent']}**")
            st.markdown(item["content"])
            st.divider()
    else:
        st.info("Arena is ready. Agents will generate real model responses, not placeholders.")


def normalize_url(value):
    raw = (value or "").strip()
    if not raw:
        return "https://www.google.com"
    if re.match(r"^https?://", raw, re.I):
        return raw
    if "." in raw and " " not in raw:
        return "https://" + raw
    return "https://www.google.com/search?q=" + urllib.parse.quote(raw)


def browser_google_search(query, limit=6):
    if google_search is None:
        package_state = "installed" if google_namespace is not None else "missing"
        st.session_state.browser_status = (
            f"Google package is {package_state}, but the `googlesearch.search` helper is unavailable."
        )
        return []
    results = []
    seen = set()
    try:
        try:
            urls = google_search(
                query,
                num=limit,
                stop=limit,
                pause=1.0,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) LightskyAI/1.0",
            )
        except TypeError:
            urls = google_search(query, num_results=limit)
        for href in urls:
            href = str(href or "").strip()
            if not href.startswith("http"):
                continue
            key = href.lower().split("#", 1)[0]
            if key in seen:
                continue
            seen.add(key)
            page = core._ls51_fetch_page_summary(href, max_chars=420)
            parsed = urllib.parse.urlparse(href)
            title = (page or {}).get("title") or parsed.netloc or href
            snippet = (page or {}).get("summary") or ""
            results.append({"title": title, "url": href, "snippet": snippet})
            if len(results) >= limit:
                break
    except Exception as exc:
        st.session_state.browser_status = f"Google search failed: {exc}"
    return results


def browser_screen(route):
    render_header(route)
    st.markdown("### Browser")
    st.session_state.setdefault("browser_url", "https://www.google.com")
    st.session_state.setdefault("browser_results", [])
    st.session_state.setdefault("browser_status", "")

    target = st.text_input("URL or search", value=st.session_state.browser_url, key="browser_input")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("Preview / go", type="primary"):
            st.session_state.browser_url = normalize_url(target)
            st.session_state.browser_status = ""
    with c2:
        if st.button("Google search"):
            st.session_state.browser_status = "Searching with the installed google package..."
            results = browser_google_search(target, limit=6)
            st.session_state.browser_results = results
            if results:
                st.session_state.browser_url = results[0]["url"]
                st.session_state.browser_status = f"Found {len(results)} Google results."
            else:
                st.session_state.browser_url = normalize_url(target)
                if not st.session_state.browser_status:
                    st.session_state.browser_status = "No Google results returned; showing a normal search URL."
    with c3:
        if st.button("Google home"):
            st.session_state.browser_url = "https://www.google.com"
            st.session_state.browser_results = []
            st.session_state.browser_status = ""

    if st.session_state.browser_status:
        st.caption(st.session_state.browser_status)

    if st.session_state.browser_results:
        labels = [f"{i + 1}. {item['title']}" for i, item in enumerate(st.session_state.browser_results)]
        pick = st.selectbox("Google results", labels)
        selected = st.session_state.browser_results[labels.index(pick)]
        st.markdown(f"**{selected['title']}**  \n{selected['url']}")
        if selected.get("snippet"):
            st.caption(selected["snippet"][:500])
        a, b = st.columns([1, 1])
        with a:
            if st.button("Preview selected result"):
                st.session_state.browser_url = selected["url"]
                st.rerun()
        with b:
            st.link_button("Open selected in real browser", selected["url"])
    else:
        st.caption(
            "Google search uses the installed `google` package when available. "
            "Embedded browsing works only when the site allows iframes."
        )

    url = st.session_state.browser_url
    st.link_button("Open current page in real browser", url)
    render_iframe(url, height=680, scrolling=True)


FILE_EXTENSIONS = (".exe", ".msi", ".zip", ".pdf", ".whl", ".msix", ".apk", ".dmg", ".pkg", ".tar.gz", ".7z", ".rar")


def resolve_download_url(url):
    try:
        head = requests.head(url, allow_redirects=True, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        content_type = head.headers.get("content-type", "").lower()
        final = head.url
        if any(final.lower().split("?")[0].endswith(ext) for ext in FILE_EXTENSIONS) or "text/html" not in content_type:
            return final
    except Exception:
        pass
    response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    links = re.findall(r'href=["\']([^"\']+)["\']', response.text, flags=re.I)
    for link in links:
        absolute = urllib.parse.urljoin(url, link)
        if any(absolute.lower().split("?")[0].endswith(ext) for ext in FILE_EXTENSIONS):
            return absolute
    return url


def download_file(url):
    final_url = resolve_download_url(url)
    response = requests.get(final_url, stream=True, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    parsed = urllib.parse.urlparse(response.url)
    filename = os.path.basename(parsed.path) or "download.bin"
    filename = re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    dest = DOWNLOAD_DIR / filename
    total = 0
    with open(dest, "wb") as f:
        for chunk in response.iter_content(chunk_size=65536):
            if chunk:
                total += len(chunk)
                if total > 150 * 1024 * 1024:
                    raise RuntimeError("Blocked: file is larger than 150MB")
                f.write(chunk)
    return dest, total, response.url


def look_take_screen(route):
    render_header(route)
    st.markdown("### Look & Take")
    query = st.text_input("Search the web or paste a direct file/page link")
    col1, col2 = st.columns([1, 1])
    if col1.button("Search / inspect", type="primary"):
        if re.match(r"^https?://", query or "", re.I):
            try:
                page = core._ls51_fetch_page_summary(query, max_chars=2200)
                st.session_state.look_results = [{"title": page.get("title", "Page"), "url": query, "snippet": page.get("summary", "")}] if page else []
                st.session_state.look_details = json.dumps(st.session_state.look_results, indent=2)
            except Exception as e:
                st.session_state.look_details = f"Fetch failed: {e}"
        else:
            context, sources = core.lightsky_build_universal_web_context(query, max_results=6)
            st.session_state.look_results = sources
            st.session_state.look_details = context
    if col2.button("Clear"):
        st.session_state.look_results = []
        st.session_state.look_details = ""

    if st.session_state.look_results:
        labels = [f"{i+1}. {item.get('title','Source')}" for i, item in enumerate(st.session_state.look_results)]
        pick = st.selectbox("Result", labels)
        selected = st.session_state.look_results[labels.index(pick)]
        st.markdown(f"**URL:** {selected.get('url','')}")
        st.write(selected.get("snippet", ""))
        if st.button("Download selected link"):
            try:
                path, size, final_url = download_file(selected.get("url", ""))
                st.session_state.last_download = str(path)
                st.success(f"Downloaded {path.name} ({size:,} bytes)")
                st.caption(final_url)
            except Exception as e:
                st.error(f"Download failed: {e}")

    if st.session_state.last_download:
        st.info(f"Last download: {st.session_state.last_download}")
    with st.expander("Details", expanded=bool(st.session_state.look_details)):
        st.text(st.session_state.look_details or "No details yet.")


def fallback_image(prompt, width=1024, height=1024):
    image = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(image)
    colors = ["#67e8f9", "#7c9cff", "#c084fc", "#f472b6", "#facc15", "#4ade80"]
    for i, color in enumerate(colors):
        draw.rounded_rectangle([70 + i * 35, 90 + i * 34, width - 70 - i * 28, height - 120 + i * 8], radius=42, outline=color, width=7)
    draw.text((90, height - 190), "Lightsky Image Studio", fill="#172033")
    draw.text((90, height - 150), textwrap.shorten(prompt, width=80), fill="#667085")
    return image


def image_screen(route):
    render_header(route)
    st.markdown("### Image Studio")
    prompt = st.text_area("Prompt", height=130, placeholder="Complex image generation prompt...")
    model_name = st.selectbox("Image model", list(core.HUGGINGFACE_IMAGE_MODELS.keys()))
    size = st.select_slider("Size", options=[512, 768, 1024], value=1024)
    if st.button("Generate image", type="primary"):
        if not prompt.strip():
            st.warning("Enter an image prompt first.")
        else:
            with st.spinner("\u2728 Generating image..."):
                image = core.generate_huggingface_image(prompt, model=core.HUGGINGFACE_IMAGE_MODELS[model_name], width=size, height=size)
                if image is None:
                    image = fallback_image(prompt, size, size)
                out = GENERATED_DIR / f"lightsky_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                image.save(out)
                st.session_state.generated_image = str(out)
    if st.session_state.get("generated_image"):
        st.image(st.session_state.generated_image, use_container_width=True)
        with open(st.session_state.generated_image, "rb") as f:
            st.download_button("Download image", f.read(), file_name=Path(st.session_state.generated_image).name)


def installed_plugins():
    plugins = []
    for manifest in PLUGIN_DIR.glob("*/lightsky_plugin.json"):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["installed_path"] = str(manifest.parent)
            plugins.append(data)
        except Exception:
            pass
    return plugins


def search_github_repos(query):
    response = requests.get(
        "https://api.github.com/search/repositories",
        params={"q": query or "topic:mcp-server", "sort": "stars", "order": "desc", "per_page": 10},
        headers={"Accept": "application/vnd.github+json", "User-Agent": "LightskyAI"},
        timeout=25,
    )
    response.raise_for_status()
    return response.json().get("items", [])


def install_github_repo(repo):
    name = repo["full_name"].replace("/", "__")
    target = PLUGIN_DIR / name
    staging = Path(tempfile.mkdtemp(prefix="lightsky_plugin_"))
    try:
        zip_url = repo.get("zipball_url") or f"https://github.com/{repo['full_name']}/archive/refs/heads/{repo.get('default_branch','main')}.zip"
        response = requests.get(zip_url, timeout=60, headers={"User-Agent": "LightskyAI"})
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            archive.extractall(staging)
        extracted = next((p for p in staging.iterdir() if p.is_dir()), None)
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(extracted), str(target))
        manifest = {
            "name": repo.get("name"),
            "full_name": repo.get("full_name"),
            "source": "github",
            "source_url": repo.get("html_url"),
            "installed": True,
            "installed_path": str(target),
            "installed_at": datetime.now().isoformat(timespec="seconds"),
        }
        (target / "lightsky_plugin.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return target
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def plugins_screen(route):
    render_header(route)
    st.markdown("### Plugin Center")
    st.caption("User-facing plugins come only from GitHub repositories.")
    query = st.text_input("GitHub search", value="topic:mcp-server")
    if st.button("Search GitHub", type="primary"):
        try:
            st.session_state.github_results = search_github_repos(query)
        except Exception as e:
            st.error(f"GitHub search failed: {e}")
    if st.session_state.github_results:
        labels = [f"{repo['full_name']} ({repo.get('stargazers_count', 0)} stars)" for repo in st.session_state.github_results]
        pick = st.selectbox("Repository", labels)
        repo = st.session_state.github_results[labels.index(pick)]
        st.json({"name": repo["full_name"], "description": repo.get("description"), "url": repo.get("html_url")})
        if st.button("Install selected GitHub plugin"):
            try:
                path = install_github_repo(repo)
                st.success(f"Installed to {path}")
            except Exception as e:
                st.error(f"Install failed: {e}")

    st.markdown("#### Installed")
    current = installed_plugins()
    if current:
        for plugin in current:
            st.markdown(f"- **{plugin.get('full_name') or plugin.get('name')}**  \n  `{plugin.get('installed_path')}`")
    else:
        st.info("No GitHub plugins installed yet.")


def intertest_screen(route):
    render_header(route)
    st.markdown("### Inter-Test")
    st.caption(
        "Every provider can request `python_code`, `python_file`, or guarded `command` runs. "
        f"AI Inter-Test access is {'on' if st.session_state.get('ai_intertest_enabled', True) else 'off'} in the sidebar."
    )

    st.markdown("#### Ask the selected model to build and test code")
    ai_task = st.text_area(
        "AI Inter-Test request",
        placeholder="Example: Write a Python function that validates email addresses, run a few tests, and show the final code.",
        height=110,
    )
    if st.button("Ask model and run Inter-Test", type="primary"):
        if not ai_task.strip():
            st.warning("Enter what you want the model to build or test.")
        else:
            tool_prompt = f"""
Use Inter-Test if running code would help. If you need execution, return exactly one `ls_tool_call` block first.
Then, after the tool output is returned, produce final tested code and the result.

Request:
{ai_task}
"""
            with st.spinner(f"\u2728 {provider_display(route['provider'])} is using Inter-Test..."):
                response, sources, tool_result = run_model_with_intertest(tool_prompt.strip(), route, max_tokens=1100, web=False)
            st.markdown(response)
            if sources:
                with st.expander("Sources"):
                    for src in sources:
                        st.write(src)
            if tool_result:
                with st.expander("Inter-Test output", expanded=True):
                    st.code(format_intertest_result(tool_result), language="text")

    st.markdown("#### Manual runner")
    cwd = st.text_input("Working directory", value=str(APP_DIR))
    file_path = st.text_input("Python file to run with py")
    args = st.text_input("Args", value="")
    command = st.text_area("Or PowerShell command", height=110)
    if st.button("Run Python file"):
        if not file_path:
            st.warning("Enter a Python file path.")
        else:
            result = run_python_file_intertest(file_path, args=args, cwd=cwd, timeout=120)
            st.code(format_intertest_result(result), language="text")
    if st.button("Run command"):
        if not command.strip():
            st.warning("Enter a command.")
        else:
            result = run_command_intertest(command, cwd=cwd, timeout=120)
            st.code(format_intertest_result(result), language="text")

    st.markdown("#### Recent AI Inter-Test runs")
    if st.session_state.intertest_runs:
        for item in reversed(st.session_state.intertest_runs[-6:]):
            title = f"{item.get('created_at', '')} - {item.get('model', 'model')}"
            with st.expander(title):
                st.json(item.get("tool_call", {}))
                st.code(format_intertest_result(item.get("result", {})), language="text")
    else:
        st.info("No AI Inter-Test runs yet.")


SECURITY_PATTERNS = [
    ("A01 Broken Access Control", r"admin|is_admin|role|permission"),
    ("A02 Security Misconfiguration", r"debug\s*=\s*true|0\.0\.0\.0|allow_origins\s*=\s*\[?['\"]\*"),
    ("A03 Supply Chain", r"pip install|npm install|requirements|package-lock|setup.py"),
    ("A04 Cryptographic Failures", r"md5|sha1|DES|ECB|password\s*=|secret\s*="),
    ("A05 Injection", r"execute\(|exec\(|eval\(|raw\s+sql|SELECT .*\\+"),
    ("A08 Auth Failures", r"jwt|session|cookie|login|password"),
    ("A10 Exceptional Conditions", r"except\s*:|except Exception\s+as\s+e:\s*pass|pass\s*#"),
]


def debug_screen(route):
    render_header(route)
    st.markdown("### LS 5.1 Debug + Vulnerability")
    code = st.text_area("Paste code or error", height=280)
    if st.button("Scan locally"):
        findings = []
        for title, pattern in SECURITY_PATTERNS:
            if re.search(pattern, code or "", re.I | re.S):
                findings.append(title)
        if findings:
            st.warning("Potential issues found:")
            for item in findings:
                st.markdown(f"- {item}")
        else:
            st.success("No obvious local rule findings.")
    if st.button("Quick-fix with selected model", type="primary"):
        if not code.strip():
            st.warning("Paste code or an error first.")
        else:
            prompt = f"""
You are LS 5.1 debug and vulnerability engine.
Use OWASP 2026 categories and produce:
1. Findings
2. Risk
3. Fixed code in fenced code blocks
4. Verification steps

Input:
{code}
"""
            with st.spinner("\u2728 Running selected model quick-fix..."):
                response, sources = call_selected_model(prompt.strip(), route, max_tokens=1100, web=False)
            st.markdown(response)


def settings_screen(route):
    render_header(route)
    st.markdown("### Settings")
    st.write("Launch the Streamlit app locally with:")
    st.code("py -m streamlit run streamlit_app.py", language="powershell")
    st.markdown("#### Providers")
    rows = [
        ("Groq", True, len(core.MODELS)),
        ("CometAPI", bool(core.COMETAPI_KEY), len(core.COMET_MODELS)),
        ("Hugging Face", bool(core.HF_ACCESS_TOKEN), len(core.HUGGINGFACE_MODELS)),
        ("xAI Grok", bool(core.XAI_API_KEY), len(core.XAI_MODELS)),
        ("NVIDIA Nemotron", bool(core.NVIDIA_API_KEY), len(core.NVIDIA_NEMOTRON_MODELS)),
        ("LS 5.1", True, 1),
    ]
    st.dataframe(
        [{"Provider": name, "Configured": configured, "Models": count} for name, configured, count in rows],
        use_container_width=True,
        hide_index=True,
    )


def main():
    init_state()
    with st.sidebar:
        st.markdown("## \u2728 Lightsky AI")
        st.caption("pro by Krivi")
        model_names = list(core.MODEL_OPTIONS.keys())
        default_index = model_names.index(core.DEFAULT_MODEL_DISPLAY) if core.DEFAULT_MODEL_DISPLAY in model_names else 0
        selected_model = st.selectbox("Model", model_names, index=default_index)
        route = route_from_display(selected_model)
        nav = st.radio(
            "Workspace",
            ["Chat", "Arena", "Browser", "Look & Take", "Image Studio", "Plugin Center", "Inter-Test", "Debug LS 5.1", "Settings"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.toggle("AI Inter-Test access", key="ai_intertest_enabled")
        st.caption(f"Provider: {provider_display(route['provider'])}")
        st.caption(f"Model ID: {route['model']}")

    if nav == "Chat":
        chat_screen(route)
    elif nav == "Arena":
        arena_screen(route)
    elif nav == "Browser":
        browser_screen(route)
    elif nav == "Look & Take":
        look_take_screen(route)
    elif nav == "Image Studio":
        image_screen(route)
    elif nav == "Plugin Center":
        plugins_screen(route)
    elif nav == "Inter-Test":
        intertest_screen(route)
    elif nav == "Debug LS 5.1":
        debug_screen(route)
    else:
        settings_screen(route)


if __name__ == "__main__":
    main()
