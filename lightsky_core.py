"""Tk-free backend for the Lightsky Streamlit app.

This module intentionally avoids tkinter, desktop speech, and UI imports so it
can run on hosted Streamlit environments.
"""

from __future__ import annotations

import base64
import html
import os
import re
import time
import urllib.parse
from datetime import datetime
from io import BytesIO

import requests
from PIL import Image

SAFARI_HTTP_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15 LightskyAI/1.0"
)
DEFAULT_WEB_HEADERS = {
    "User-Agent": SAFARI_HTTP_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
}

try:
    from huggingface_hub import HfApi, InferenceClient
    HAS_HUGGINGFACE_HUB = True
except ImportError:
    HfApi = None
    InferenceClient = None
    HAS_HUGGINGFACE_HUB = False

try:
    import googlesearch
    HAS_GOOGLE = True
except ImportError:
    googlesearch = None
    HAS_GOOGLE = False


def _read_windows_user_env(name: str) -> str:
    if os.name != "nt":
        return ""
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _value_type = winreg.QueryValueEx(key, name)
            return str(value or "").strip()
    except Exception:
        return ""


def _env_value(name: str) -> str:
    return (os.environ.get(name) or _read_windows_user_env(name) or "").strip()


def _env_first(*names: str) -> str:
    for name in names:
        value = _env_value(name)
        if value:
            return value
    return ""


def _env_list(*names: str) -> list[str]:
    values: list[str] = []
    for name in names:
        raw = _env_value(name)
        for part in re.split(r"[\n,;]+", raw):
            item = part.strip()
            if item and item not in values:
                values.append(item)
    return values


HF_ACCESS_TOKEN = ""
GEMINI_API_KEY = ""
XAI_API_KEY = ""
NVIDIA_API_KEY = ""


def refresh_provider_keys() -> dict[str, bool]:
    """Refresh provider API keys after Streamlit settings/env changes."""
    global HF_ACCESS_TOKEN, GEMINI_API_KEY, XAI_API_KEY, NVIDIA_API_KEY

    HF_ACCESS_TOKEN = _env_first("HF_TOKEN", "HUGGINGFACE_TOKEN")
    if HF_ACCESS_TOKEN:
        os.environ.setdefault("HF_TOKEN", HF_ACCESS_TOKEN)
        os.environ.setdefault("HUGGINGFACE_TOKEN", HF_ACCESS_TOKEN)

    GEMINI_API_KEY = _env_first("GEMINI_API_KEY", "GOOGLE_API_KEY")
    if GEMINI_API_KEY:
        os.environ.setdefault("GEMINI_API_KEY", GEMINI_API_KEY)
        os.environ.setdefault("GOOGLE_API_KEY", GEMINI_API_KEY)

    XAI_API_KEY = _env_first("XAI_API_KEY", "XAI_API_TOKEN")
    if XAI_API_KEY:
        os.environ.setdefault("XAI_API_KEY", XAI_API_KEY)
        os.environ.setdefault("XAI_API_TOKEN", XAI_API_KEY)

    NVIDIA_API_KEY = _env_first("NVIDIA_API_KEY", "NVIDIA_NIM_API_KEY", "NVIDIA_NGC_API_KEY")
    if NVIDIA_API_KEY:
        os.environ.setdefault("NVIDIA_API_KEY", NVIDIA_API_KEY)
        os.environ.setdefault("NVIDIA_NIM_API_KEY", NVIDIA_API_KEY)
        os.environ.setdefault("NVIDIA_NGC_API_KEY", NVIDIA_API_KEY)

    return {
        "gemini": bool(GEMINI_API_KEY),
        "huggingface": bool(HF_ACCESS_TOKEN),
        "xai": bool(XAI_API_KEY),
        "nvidia": bool(NVIDIA_API_KEY),
    }


refresh_provider_keys()
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
XAI_BASE_URL = "https://api.x.ai/v1"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

GEMINI_MODELS = {
    "Gemini 2.5 Pro": "gemini-2.5-pro",
    "Gemini 2.5 Flash": "gemini-2.5-flash",
    "Gemini 2.5 Flash Lite": "gemini-2.5-flash-lite",
    "Gemini 2.0 Flash": "gemini-2.0-flash",
    "Gemini 2.0 Flash Lite": "gemini-2.0-flash-lite",
}

HUGGINGFACE_MODELS = {
    "Qwen 2.5 7B Instruct": "Qwen/Qwen2.5-7B-Instruct",
    "Mistral 7B Instruct": "mistralai/Mistral-7B-Instruct-v0.3",
    "SmolLM3 3B": "HuggingFaceTB/SmolLM3-3B",
    "Zephyr 7B Beta": "HuggingFaceH4/zephyr-7b-beta",
}

XAI_MODELS = {
    "Grok 4.20 Reasoning": "grok-4.20-reasoning",
    "Grok 4": "grok-4",
    "Grok 4 Fast Reasoning": "grok-4-fast-reasoning",
    "Grok 4 Fast Non-Reasoning": "grok-4-fast-non-reasoning",
}

NVIDIA_NEMOTRON_MODELS = {
    "Nemotron Super 49B v1.5": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
    "Nemotron Ultra 253B": "nvidia/llama-3.1-nemotron-ultra-253b-v1",
    "Nemotron 3 Super 120B": "nvidia/nemotron-3-super-120b-a12b",
    "Nemotron 3 Nano 30B": "nvidia/nemotron-3-nano-30b-a3b",
    "Nemotron 70B Instruct": "nvidia/llama-3.1-nemotron-70b-instruct",
    "Mistral Nemotron": "mistralai/mistral-nemotron",
    "Nemotron 4 340B Instruct": "nvidia/nemotron-4-340b-instruct",
}

HUGGINGFACE_IMAGE_MODELS = {
    "SDXL Base": "stabilityai/stable-diffusion-xl-base-1.0",
    "FLUX Schnell": "black-forest-labs/FLUX.1-schnell",
}

DEFAULT_HF_TEXT_MODEL = "Qwen/Qwen2.5-7B-Instruct"
DEFAULT_HF_IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"

LS_51_MODEL_ID = "gemini-2.5-flash"
LS_51_SYSTEM_PROMPT = """You are LS 5.1, a custom chatbot model developed by Lightsky AI pro by krivi.
You are designed to feel powerful, imaginative, emotionally intelligent, and useful.
You combine the clarity of a senior engineer, the imagination of a world-builder, the taste of a premium product designer, and the calm judgment of a research partner.
Behavior rules:
- Think strategically before answering, but do not expose hidden chain-of-thought.
- Give practical next actions, strong opinions, and creative options.
- When building, prefer complete working solutions over vague advice.
- If the user asks for code, be precise, robust, and production-minded.
- When returning code, always use triple-backtick fenced blocks with the language label.
- Keep the Lightsky identity: confident, elegant, useful, and a little magical.
- If asked what you are, say you are LS 5.1, a custom Lightsky chatbot model by krivi."""

MODEL_OPTIONS = {
    "\u2728 LS 5.1 (custom)": {
        "provider": "ls_custom",
        "model": LS_51_MODEL_ID,
        "base_provider": "gemini",
        "system_prompt": LS_51_SYSTEM_PROMPT,
        "temperature": 0.82,
    }
}
for display_name, model_id in GEMINI_MODELS.items():
    MODEL_OPTIONS[f"Google Gemini / {display_name}"] = {"provider": "gemini", "model": model_id}
for display_name, model_id in HUGGINGFACE_MODELS.items():
    MODEL_OPTIONS[f"Hugging Face / {display_name}"] = {"provider": "huggingface", "model": model_id}
for display_name, model_id in XAI_MODELS.items():
    MODEL_OPTIONS[f"xAI / {display_name}"] = {"provider": "xai", "model": model_id}
for display_name, model_id in NVIDIA_NEMOTRON_MODELS.items():
    MODEL_OPTIONS[f"NVIDIA / {display_name}"] = {"provider": "nvidia", "model": model_id}

DEFAULT_MODEL_DISPLAY = "Google Gemini / Gemini 2.5 Flash"
DEFAULT_MODEL_CONFIG = MODEL_OPTIONS.get(DEFAULT_MODEL_DISPLAY, next(iter(MODEL_OPTIONS.values())))
CURRENT_MODEL = DEFAULT_MODEL_CONFIG.get("model")
CURRENT_PROVIDER = DEFAULT_MODEL_CONFIG.get("provider", "gemini")
CURRENT_SYSTEM_PROMPT = DEFAULT_MODEL_CONFIG.get(
    "system_prompt",
    "You are Lightsky AI pro by krivi, a helpful desktop assistant.",
)
CURRENT_TEMPERATURE = DEFAULT_MODEL_CONFIG.get("temperature", 0.7)

LS51_POWER_MODE = True
LS51_WEB_RESEARCH_MODE = True
LS51_MAX_WEB_CONTEXT_RESULTS = 4
MODEL_AGENT_TOOLS_ENABLED = True

OWASP_TOP10_CURRENT = {
    "A01": "Broken Access Control",
    "A02": "Security Misconfiguration",
    "A03": "Software Supply Chain Failures",
    "A04": "Cryptographic Failures",
    "A05": "Injection",
    "A06": "Insecure Design",
    "A07": "Vulnerable and Outdated Components",
    "A08": "Identification and Authentication Failures",
    "A09": "Software and Data Integrity Failures",
    "A10": "Mishandling of Exceptional Conditions",
}
OWASP_TOP10_CONTEXT = "\n".join(f"{code}: {name}" for code, name in OWASP_TOP10_CURRENT.items())

AGENT_TOOLING_PROMPT = """
Lightsky can request local actions through the app, but you must never pretend a command ran.
If code execution or testing would improve the answer, ask for exactly one Inter-Test action in a fenced JSON block labelled ls_tool_call.
Supported Inter-Test actions:
- python_code: run a temporary Python script. Required: code. Optional: filename, args, timeout.
- python_file: run an existing Python file. Required: path. Optional: args, cwd, timeout.
- command: run a guarded shell command. Required: command. Optional: cwd, timeout.
Example:
```ls_tool_call
{"action":"python_code","filename":"check.py","code":"print('OK')","timeout":30}
```
After the app returns Inter-Test output, use it to produce the final answer.
Always keep code output in fenced code blocks with a language label.
"""

def _base_system_prompt(system_prompt: str | None = None) -> str:
    content = system_prompt or (
        "You are Lightsky AI pro by krivi, a helpful, fast, creative assistant. "
        "When returning code, always use fenced triple-backtick code blocks with a language label."
    )
    if MODEL_AGENT_TOOLS_ENABLED:
        content = content + "\n\n" + AGENT_TOOLING_PROMPT
    return content


def _extract_openai_compatible_text(result: dict) -> tuple[str, str | None]:
    try:
        choice = (result.get("choices") or [{}])[0]
    except Exception:
        return "", None
    if not isinstance(choice, dict):
        return "", None
    finish_reason = choice.get("finish_reason")
    message = choice.get("message") if isinstance(choice.get("message"), dict) else {}
    content = message.get("content")
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                value = item.get("text") or item.get("content") or item.get("value")
                if value:
                    parts.append(str(value))
            elif item:
                parts.append(str(item))
        content = "\n".join(parts)
    if not content:
        content = (
            choice.get("text")
            or message.get("reasoning_content")
            or message.get("reasoning")
            or message.get("summary")
            or ""
        )
    return str(content).strip(), finish_reason


def _gemini_model_path(model: str) -> str:
    raw = (model or "gemini-2.5-flash").strip()
    if raw.startswith("models/"):
        return raw
    return f"models/{raw}"


def _extract_gemini_text(data: dict) -> tuple[str, str | None]:
    candidates = data.get("candidates") or []
    finish_reason = None
    parts_out: list[str] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        finish_reason = candidate.get("finishReason") or finish_reason
        content = candidate.get("content") or {}
        for part in content.get("parts") or []:
            if isinstance(part, dict):
                text = part.get("text")
                if text:
                    parts_out.append(str(text))
    return "\n".join(parts_out).strip(), finish_reason


def get_gemini_response(
    prompt: str,
    model: str = "gemini-2.5-flash",
    max_tokens: int = 300,
    max_retries: int = 2,
    system_prompt: str | None = None,
    temperature: float = 0.7,
) -> str:
    refresh_provider_keys()
    if not GEMINI_API_KEY:
        return "Google Gemini is not configured. Open Settings > Provider keys and add a Gemini API key, or set GEMINI_API_KEY / GOOGLE_API_KEY in environment variables or Streamlit secrets."

    payload = {
        "systemInstruction": {"parts": [{"text": _base_system_prompt(system_prompt)}]},
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }
    model_path = _gemini_model_path(model)
    url = f"{GEMINI_BASE_URL}/{model_path}:generateContent"

    for retry in range(max_retries):
        try:
            if retry > 0:
                time.sleep(min(2**retry, 6))
            response = requests.post(url, headers=headers, json=payload, timeout=75)
            if response.status_code == 200:
                text, finish_reason = _extract_gemini_text(response.json())
                return text or f"Google Gemini returned an empty message (finish reason: {finish_reason or 'unknown'})."
            if response.status_code == 429:
                body = response.text[:700].lower()
                if any(term in body for term in ("quota", "rate", "limit", "exhausted")):
                    return "Google Gemini is configured, but the key appears to be rate-limited or out of quota."
                continue
            if response.status_code in (500, 502, 503, 504):
                continue
            body = response.text[:700]
            return f"Google Gemini returned an error: {response.status_code}. {body}"
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.ConnectionError:
            continue
        except Exception as exc:
            return f"Google Gemini request error: {exc}"
    return "Google Gemini is not responding right now. Please try again in a moment."


def get_openai_compatible_response(
    prompt: str,
    provider_name: str,
    base_url: str,
    api_key: str,
    model: str,
    max_tokens: int = 300,
    max_retries: int = 2,
    system_prompt: str | None = None,
    temperature: float = 0.7,
    timeout: int = 60,
) -> str:
    if not api_key:
        return f"{provider_name} is not configured. Add the provider API key in environment or Streamlit secrets."

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": _base_system_prompt(system_prompt)},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }

    for retry in range(max_retries):
        try:
            if retry > 0:
                time.sleep(min(2**retry, 6))
            response = requests.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout,
            )
            if response.status_code == 200:
                text, finish_reason = _extract_openai_compatible_text(response.json())
                if text:
                    return text
                return f"{provider_name} returned an empty message (finish reason: {finish_reason or 'unknown'})."
            if response.status_code == 429:
                body = response.text[:700].lower()
                if any(term in body for term in ("credit", "spending limit", "monthly", "quota", "exhausted")):
                    return f"{provider_name} is configured, but the key appears to be out of credits or quota."
                continue
            if response.status_code in (500, 502, 503, 504):
                continue
            return f"{provider_name} returned an error: {response.status_code}. Try a different model or check model access."
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.ConnectionError:
            continue
        except Exception as exc:
            return f"{provider_name} request error: {exc}"
    return f"{provider_name} is not responding right now. Please try again in a moment."


def get_xai_response(
    prompt: str,
    model: str = "grok-4-fast-reasoning",
    max_tokens: int = 300,
    system_prompt: str | None = None,
    temperature: float = 0.7,
) -> str:
    return get_openai_compatible_response(
        prompt,
        "xAI/Grok",
        XAI_BASE_URL,
        XAI_API_KEY,
        model,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
        temperature=temperature,
        timeout=120,
    )


def get_nvidia_response(
    prompt: str,
    model: str = "nvidia/llama-3.3-nemotron-super-49b-v1.5",
    max_tokens: int = 300,
    system_prompt: str | None = None,
    temperature: float = 0.7,
) -> str:
    return get_openai_compatible_response(
        prompt,
        "NVIDIA Nemotron",
        NVIDIA_BASE_URL,
        NVIDIA_API_KEY,
        model,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
        temperature=temperature,
        timeout=90,
    )


def refresh_nvidia_nemotron_models(limit: int = 20) -> list[str]:
    refresh_provider_keys()
    if not NVIDIA_API_KEY:
        return []
    try:
        response = requests.get(
            f"{NVIDIA_BASE_URL.rstrip('/')}/models",
            headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"},
            timeout=20,
        )
        if response.status_code != 200:
            return []
        ids = []
        for item in response.json().get("data", []):
            model_id = item.get("id") if isinstance(item, dict) else None
            if model_id and "nemotron" in model_id.lower() and model_id not in ids:
                ids.append(model_id)
        return ids[:limit]
    except Exception:
        return []


def _extract_hf_chat_text(output) -> str:
    try:
        return output.choices[0].message.content.strip()
    except Exception:
        pass
    if isinstance(output, dict):
        text, _finish_reason = _extract_openai_compatible_text(output)
        if text:
            return text
    return str(output).strip() if output else ""


def _parse_hf_http_text(result, prompt: str) -> str:
    if isinstance(result, list) and result:
        item = result[0]
        if isinstance(item, dict):
            text = item.get("generated_text") or item.get("summary_text") or item.get("translation_text") or ""
            if text.startswith(prompt):
                text = text[len(prompt):]
            return text.strip()
    if isinstance(result, dict):
        if result.get("error"):
            return f"Hugging Face returned an error: {result.get('error')}"
        text = result.get("generated_text") or result.get("text") or ""
        if text.startswith(prompt):
            text = text[len(prompt):]
        return text.strip()
    return str(result).strip() if result else ""


def get_huggingface_response(
    prompt: str,
    model: str = DEFAULT_HF_TEXT_MODEL,
    max_tokens: int = 300,
    max_retries: int = 1,
    system_prompt: str | None = None,
    temperature: float = 0.7,
) -> str:
    refresh_provider_keys()
    if not HF_ACCESS_TOKEN:
        return "Hugging Face is not configured. Add HF_TOKEN or HUGGINGFACE_TOKEN in environment or Streamlit secrets."

    chosen_model = model or DEFAULT_HF_TEXT_MODEL
    messages = [
        {"role": "system", "content": _base_system_prompt(system_prompt)},
        {"role": "user", "content": prompt},
    ]
    last_error = ""

    if HAS_HUGGINGFACE_HUB and InferenceClient is not None:
        try:
            client = InferenceClient(model=chosen_model, token=HF_ACCESS_TOKEN, timeout=30)
            output = client.chat_completion(messages=messages, max_tokens=max_tokens, temperature=temperature)
            text = _extract_hf_chat_text(output)
            if text:
                return text
        except Exception as exc:
            last_error = str(exc)

    headers = {"Authorization": f"Bearer {HF_ACCESS_TOKEN}", "Content-Type": "application/json"}
    router_payload = {"model": chosen_model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    for _retry in range(max_retries + 1):
        try:
            response = requests.post(
                "https://router.huggingface.co/v1/chat/completions",
                headers=headers,
                json=router_payload,
                timeout=35,
            )
            if response.status_code == 200:
                text = _extract_hf_chat_text(response.json())
                if text:
                    return text
            last_error = f"{response.status_code}: {response.text[:300]}"
        except Exception as exc:
            last_error = str(exc)

    fallback_prompt = f"{messages[0]['content']}\n\nUser: {prompt}\nAssistant:"
    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{chosen_model}",
            headers=headers,
            json={
                "inputs": fallback_prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False,
                },
                "options": {"wait_for_model": True},
            },
            timeout=60,
        )
        if response.status_code == 200:
            text = _parse_hf_http_text(response.json(), fallback_prompt)
            if text:
                return text
        last_error = f"{response.status_code}: {response.text[:300]}"
    except Exception as exc:
        last_error = str(exc)
    return f"Hugging Face returned an error: {last_error or 'no response'}"


def generate_huggingface_image(
    prompt: str,
    model: str = DEFAULT_HF_IMAGE_MODEL,
    width: int = 1024,
    height: int = 1024,
):
    refresh_provider_keys()
    if not HF_ACCESS_TOKEN:
        return None
    chosen_model = model or DEFAULT_HF_IMAGE_MODEL
    if HAS_HUGGINGFACE_HUB and InferenceClient is not None:
        try:
            client = InferenceClient(model=chosen_model, token=HF_ACCESS_TOKEN, timeout=100)
            image = client.text_to_image(prompt, width=width, height=height)
            return image.convert("RGB") if hasattr(image, "convert") else image
        except Exception:
            pass
    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{chosen_model}",
            headers={"Authorization": f"Bearer {HF_ACCESS_TOKEN}"},
            json={
                "inputs": prompt,
                "parameters": {"width": width, "height": height},
                "options": {"wait_for_model": True},
            },
            timeout=100,
        )
        content_type = response.headers.get("content-type", "")
        if response.status_code == 200 and "image" in content_type:
            return Image.open(BytesIO(response.content)).convert("RGB")
    except Exception:
        pass
    return None


def _ls51_prompt_profile(prompt: str) -> str:
    p = (prompt or "").lower()
    if any(k in p for k in ("bug", "traceback", "error", "exception", "debug", "fix")):
        return "debugging"
    if any(k in p for k in ("vulnerability", "security", "exploit", "sanitize", "injection", "owasp")):
        return "security"
    if any(k in p for k in ("code", "python", "javascript", "function", "class", "api")):
        return "coding"
    if any(k in p for k in ("plan", "strategy", "roadmap", "architecture")):
        return "planning"
    return "general"


def _ls51_should_search_web(prompt: str, profile: str) -> bool:
    p = (prompt or "").lower()
    explicit = any(
        k in p
        for k in (
            "search web",
            "look up",
            "lookup",
            "find online",
            "web search",
            "latest",
            "today",
            "current",
            "news",
            "recent",
            "release notes",
            "official docs",
            "documentation",
            "breaking change",
            "version",
        )
    )
    has_url = ("http://" in p) or ("https://" in p) or ("www." in p)
    code_docs_intent = profile == "coding" and any(k in p for k in ("library", "framework", "api", "sdk", "docs", "package"))
    return explicit or has_url or code_docs_intent


def _decode_result_url(href: str) -> str:
    href = html.unescape(href or "").strip()
    if "duckduckgo.com/l/?" in href:
        query = urllib.parse.urlparse(href).query
        uddg = urllib.parse.parse_qs(query).get("uddg", [])
        if uddg:
            return urllib.parse.unquote(uddg[0])
    if "bing.com/ck/a" in href:
        query = urllib.parse.urlparse(href).query
        encoded = urllib.parse.parse_qs(query).get("u", [])
        if encoded:
            try:
                payload = encoded[0]
                if payload.startswith("a1"):
                    payload = payload[2:]
                payload += "=" * (-len(payload) % 4)
                decoded = base64.urlsafe_b64decode(payload.encode("ascii")).decode("utf-8", "ignore")
                if decoded.startswith("http"):
                    return decoded
            except Exception:
                pass
    return href


def _clean_html_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def _ls51_duckduckgo_search(query: str, max_results: int = 5) -> list[dict]:
    out: list[dict] = []
    seen = set()

    def add_result(title: str, href: str, snippet: str = "") -> None:
        href = _decode_result_url(href)
        if not href.startswith("http"):
            return
        key = href.lower().split("#", 1)[0]
        if key in seen:
            return
        seen.add(key)
        title_clean = _clean_html_text(title)
        if not title_clean:
            title_clean = urllib.parse.urlparse(href).netloc or href
        out.append({"title": title_clean[:180], "url": href, "snippet": _clean_html_text(snippet)[:700]})

    try:
        from ddgs import DDGS

        with DDGS() as ddgs:
            for item in ddgs.text(query[:320], max_results=max_results):
                add_result(item.get("title", ""), item.get("href") or item.get("url", ""), item.get("body") or item.get("snippet", ""))
                if len(out) >= max_results:
                    return out
    except Exception:
        pass

    headers = DEFAULT_WEB_HEADERS
    try:
        url = "https://duckduckgo.com/html/?q=" + urllib.parse.quote(query[:320])
        res = requests.get(url, headers=headers, timeout=16)
        if res.status_code == 200:
            pattern = re.compile(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.I | re.S)
            for match in pattern.finditer(res.text):
                add_result(match.group(2), match.group(1))
                if len(out) >= max_results:
                    return out
    except Exception:
        pass

    try:
        url = "https://www.bing.com/search?q=" + urllib.parse.quote(query[:320])
        res = requests.get(url, headers=headers, timeout=16)
        if res.status_code == 200:
            pattern = re.compile(r'<li class="b_algo".*?<h2[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.I | re.S)
            for match in pattern.finditer(res.text):
                add_result(match.group(2), match.group(1))
                if len(out) >= max_results:
                    return out
    except Exception:
        pass

    if HAS_GOOGLE and googlesearch is not None:
        try:
            for href in googlesearch.search(query[:320], num=max_results, stop=max_results, pause=1.0):
                add_result("", href)
                if len(out) >= max_results:
                    return out
        except Exception:
            pass
    return out


def _ls51_fetch_page_summary(url: str, max_chars: int = 1400):
    try:
        response = requests.get(
            url,
            headers=DEFAULT_WEB_HEADERS,
            timeout=16,
        )
        if response.status_code != 200:
            return None
        content_type = response.headers.get("content-type", "").lower()
        if "text" not in content_type and "html" not in content_type and "json" not in content_type and not response.text:
            return None
        text = response.text[:180000]
        title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
        title = _clean_html_text(title_match.group(1)) if title_match else urllib.parse.urlparse(url).netloc or "Untitled"
        text = re.sub(r"(?is)<script.*?>.*?</script>", " ", text)
        text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
        text = re.sub(r"(?is)<noscript.*?>.*?</noscript>", " ", text)
        summary = _clean_html_text(text)[:max_chars]
        return {"title": title[:180], "summary": summary}
    except Exception:
        return None


def lightsky_should_search_web(prompt: str) -> bool:
    p = (prompt or "").lower()
    profile = _ls51_prompt_profile(prompt)
    explicit = any(
        k in p
        for k in (
            "search",
            "serch",
            "web",
            "internet",
            "browse",
            "look up",
            "lookup",
            "google",
            "find online",
            "online",
            "website",
            "link",
            "source",
            "sources",
            "latest",
            "current",
            "today",
            "news",
            "recent",
            "release notes",
            "official docs",
            "documentation",
            "docs",
            "version",
            "changelog",
            "download",
            "safe file",
            "github",
            "hugging face",
            "huggingface",
            "as of now",
            "right now",
            "weather",
            "score",
            "stock",
            "price",
            "exchange rate",
            "schedule",
            "president",
            "prime minister",
            "ceo",
            "founder",
            "released",
            "launched",
            "announcement",
            "status page",
        )
    )
    has_url = ("http://" in p) or ("https://" in p) or ("www." in p)
    code_docs_intent = profile == "coding" and any(k in p for k in ("library", "framework", "api", "sdk", "package", "install", "pip", "npm"))
    question_time_intent = bool(
        re.search(r"\b(who|what|when|where|which|how)\b.*\b(current|latest|today|now|2026|recent|new|available|download|version)\b", p)
    )
    return explicit or has_url or code_docs_intent or question_time_intent or _ls51_should_search_web(prompt, profile)


def lightsky_clean_web_query(prompt: str) -> str:
    q = (prompt or "").strip()
    q = re.sub(r"(?i)^\s*(please\s+)?(search\s+the\s+web|web\s+search|find\s+online|look\s+up|lookup|google|browse|search)\s+(for\s+)?", "", q).strip()
    q = re.sub(r"(?i)\b(answer|tell me|explain)\s+(in|with)\s+.*$", "", q).strip()
    q = re.sub(r"(?i)\b(use|with)\s+(sources|links|citations)\b", "", q).strip()
    q = q.strip(" .?!:")
    q_low = q.lower()
    official_doc_sites = {
        "requests": "requests.readthedocs.io",
        "transformers": "huggingface.co/docs/transformers",
        "hugging face": "huggingface.co/docs",
        "fastapi": "fastapi.tiangolo.com",
        "django": "docs.djangoproject.com",
        "flask": "flask.palletsprojects.com",
        "pandas": "pandas.pydata.org/docs",
        "numpy": "numpy.org/doc",
        "react": "react.dev",
        "next.js": "nextjs.org/docs",
        "nextjs": "nextjs.org/docs",
        "tailwind": "tailwindcss.com/docs",
        "tkinter": "docs.python.org",
        "streamlit": "docs.streamlit.io",
        "python": "docs.python.org",
    }
    if any(k in q_low for k in ("official docs", "official documentation", "documentation", "docs")):
        for name, site in official_doc_sites.items():
            if name in q_low:
                return f"{name} official documentation site:{site}"
    if re.search(r"(?i)\brelease\s+date\b", q) and "official" not in q_low:
        q += " official release notes"
    return q or (prompt or "").strip()


def lightsky_build_universal_web_context(prompt: str, max_results: int = 4) -> tuple[str, list[dict]]:
    clean_query = lightsky_clean_web_query(prompt)
    results = _ls51_duckduckgo_search(clean_query, max_results=max_results)
    if not results:
        return "", []
    lines = [
        "LIVE WEB SEARCH RESULTS",
        f"Current date: {datetime.now().strftime('%Y-%m-%d')}",
        f"Search query: {clean_query}",
        "Use these sources for factual grounding. Cite the URLs you rely on. If the answer is not in the sources, say what is missing.",
    ]
    sources: list[dict] = []
    for index, item in enumerate(results[:max_results], 1):
        page = _ls51_fetch_page_summary(item["url"], max_chars=1200)
        title = (page or {}).get("title") or item.get("title") or "Untitled"
        summary = (page or {}).get("summary") or item.get("snippet") or ""
        url = item.get("url", "")
        sources.append({"title": title, "url": url, "snippet": summary[:700], "query": clean_query})
        lines.append(f"{index}. {title}\nURL: {url}")
        if summary:
            lines.append(f"Snippet: {summary[:800]}")
    return "\n\n".join(lines), sources


def ls51_build_web_context(prompt: str, max_results: int = 4) -> str:
    context, _sources = lightsky_build_universal_web_context(prompt, max_results=max_results)
    return context


def ls51_power_response(
    prompt: str,
    model: str | None = None,
    max_tokens: int = 420,
    system_prompt: str | None = None,
    temperature: float | None = None,
) -> str:
    chosen_model = model or LS_51_MODEL_ID
    chosen_temperature = CURRENT_TEMPERATURE if temperature is None else temperature
    profile = _ls51_prompt_profile(prompt)
    web_context = ""
    if LS51_WEB_RESEARCH_MODE and _ls51_should_search_web(prompt, profile):
        web_context = ls51_build_web_context(prompt, max_results=LS51_MAX_WEB_CONTEXT_RESULTS)

    mode_notes = [
        f"Profile: {profile}",
        "Answer as LS 5.1 with direct, high-quality output.",
    ]
    if profile in ("debugging", "security"):
        mode_notes.append("Use OWASP 2026 categories where relevant:")
        mode_notes.append(OWASP_TOP10_CONTEXT)
        mode_notes.append("For fixes, include exact corrected code and verification steps.")
    if web_context:
        mode_notes.append(web_context)

    enhanced_prompt = "\n\n".join(mode_notes + [f"User request:\n{prompt}"])
    return get_gemini_response(
        enhanced_prompt,
        model=chosen_model,
        max_tokens=max_tokens,
        system_prompt=system_prompt or LS_51_SYSTEM_PROMPT,
        temperature=chosen_temperature,
    )


def get_provider_response(
    prompt: str,
    provider: str | None = None,
    model: str | None = None,
    max_tokens: int = 300,
    system_prompt: str | None = None,
    temperature: float | None = None,
) -> str:
    refresh_provider_keys()
    chosen_provider = provider or CURRENT_PROVIDER
    chosen_model = model or CURRENT_MODEL
    chosen_system_prompt = system_prompt if system_prompt is not None else CURRENT_SYSTEM_PROMPT
    chosen_temperature = CURRENT_TEMPERATURE if temperature is None else temperature

    if chosen_provider == "ls_custom":
        if LS51_POWER_MODE:
            return ls51_power_response(
                prompt,
                model=chosen_model or LS_51_MODEL_ID,
                max_tokens=max_tokens,
                system_prompt=chosen_system_prompt,
                temperature=chosen_temperature,
            )
        return get_gemini_response(prompt, chosen_model or LS_51_MODEL_ID, max_tokens, system_prompt=chosen_system_prompt, temperature=chosen_temperature)
    if chosen_provider == "gemini":
        return get_gemini_response(prompt, chosen_model, max_tokens, system_prompt=chosen_system_prompt, temperature=chosen_temperature)
    if chosen_provider == "huggingface":
        return get_huggingface_response(prompt, chosen_model, max_tokens, system_prompt=chosen_system_prompt, temperature=chosen_temperature)
    if chosen_provider == "xai":
        return get_xai_response(prompt, chosen_model, max_tokens, system_prompt=chosen_system_prompt, temperature=chosen_temperature)
    if chosen_provider == "nvidia":
        return get_nvidia_response(prompt, chosen_model, max_tokens, system_prompt=chosen_system_prompt, temperature=chosen_temperature)
    return get_gemini_response(prompt, chosen_model, max_tokens, system_prompt=chosen_system_prompt, temperature=chosen_temperature)


def provider_display_name(provider: str | None = None) -> str:
    chosen_provider = provider or CURRENT_PROVIDER
    if chosen_provider == "ls_custom":
        return "LS 5.1"
    if chosen_provider == "gemini":
        return "Google Gemini"
    if chosen_provider == "huggingface":
        return "Hugging Face"
    if chosen_provider == "xai":
        return "xAI Grok"
    if chosen_provider == "nvidia":
        return "NVIDIA Nemotron"
    return "Google Gemini"
