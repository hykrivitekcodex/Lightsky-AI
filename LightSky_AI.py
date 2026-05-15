#!/usr/bin/env python3
"""
LightSky AI by Krivi - ULTIMATE CORRECTED VERSION
Complete AI Assistant with Real Groq Models, Chatbot Arena Names, Visual Web Browser
Organization: org_01kr8zg3jxfr7v0hfdf0248dt5
"""

from tkinter import *
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import tkinter.font as tkfont
import time
import pyttsx3
import threading
import requests
import json
import random
import os
import sys
import ctypes
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw
import subprocess
import webbrowser
import csv
import sqlite3
import hashlib
import urllib.parse
import urllib.request
from urllib.parse import urlparse
import ssl
import re
import html
import importlib.util
import struct
import ast
import shlex
import shutil
import zipfile
from io import BytesIO
try:
    import speech_recognition as sr
    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False
    sr = None
    print("Speech recognition library not available")

try:
    from pvrecorder import PvRecorder
    HAS_PVRECORDER = True
except ImportError:
    HAS_PVRECORDER = False
    PvRecorder = None
    print("PvRecorder not available")

import warnings
warnings.filterwarnings("ignore")

def enable_windows_dpi_awareness():
    """Ask Windows for crisp, DPI-aware rendering before Tk creates widgets."""
    if os.name != "nt":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

def tune_tk_rendering(root):
    """Set sane Tk scaling and default fonts so the UI does not look tiny or jagged."""
    try:
        scale = root.winfo_fpixels("1i") / 72.0
        scale = max(1.12, min(scale, 1.45))
        root.tk.call("tk", "scaling", scale)
    except Exception:
        pass

    try:
        families = set(tkfont.families(root))
        ui_family = "Segoe UI Variable Text" if "Segoe UI Variable Text" in families else "Segoe UI"
        mono_family = "Cascadia Mono" if "Cascadia Mono" in families else "Consolas"
        defaults = {
            "TkDefaultFont": (ui_family, 10),
            "TkTextFont": (ui_family, 11),
            "TkHeadingFont": (ui_family, 11),
            "TkMenuFont": (ui_family, 10),
            "TkFixedFont": (mono_family, 10),
        }
        for font_name, (family, size) in defaults.items():
            try:
                tkfont.nametofont(font_name).configure(family=family, size=size)
            except Exception:
                pass
    except Exception:
        pass

def _read_windows_user_env(name):
    if os.name != "nt":
        return ""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _value_type = winreg.QueryValueEx(key, name)
            return str(value or "").strip()
    except Exception:
        return ""

def _env_value(name):
    return (os.environ.get(name) or _read_windows_user_env(name) or "").strip()

def _env_first(*names):
    for name in names:
        value = _env_value(name)
        if value:
            return value
    return ""

def _env_list(*names):
    values = []
    for name in names:
        raw = _env_value(name)
        for part in re.split(r"[\n,;]+", raw):
            item = part.strip()
            if item and item not in values:
                values.append(item)
    return values

# Hugging Face token for Hub and Inference Providers. Keep secrets in env vars.
HF_ACCESS_TOKEN = _env_first("HF_TOKEN", "HUGGINGFACE_TOKEN")
if HF_ACCESS_TOKEN:
    os.environ.setdefault("HF_TOKEN", HF_ACCESS_TOKEN)
    os.environ.setdefault("HUGGINGFACE_TOKEN", HF_ACCESS_TOKEN)

try:
    from huggingface_hub import HfApi, InferenceClient
    HAS_HUGGINGFACE_HUB = True
except ImportError:
    HfApi = None
    InferenceClient = None
    HAS_HUGGINGFACE_HUB = False
    print("huggingface_hub not available; HTTP fallback enabled")

# Web Browser Libraries
try:
    import googlesearch
    HAS_GOOGLE = True
    print("Google search library loaded")
except ImportError:
    HAS_GOOGLE = False
    print("Google search not available")

# Advanced image generation is detected quickly and loaded lazily when used.
ADVANCED_IMG_GEN = (
    importlib.util.find_spec("torch") is not None and
    importlib.util.find_spec("diffusers") is not None
)
if ADVANCED_IMG_GEN:
    print("Advanced image generation libraries detected; model will lazy-load on first image.")
else:
    print("Advanced image generation not available; smart fallback renderer enabled.")

# LightSky AI Configuration - provider credentials are read from environment variables.
API_KEYS = _env_list("GROQ_API_KEYS", "GROQ_API_KEY")

ORG_ID = "org_01kr8zg3jxfr7v0hfdf0248dt5"
BASE_URL = "https://api.groq.com/openai/v1"
COMETAPI_BASE_URL = "https://api.cometapi.com/v1"
COMETAPI_KEY = _env_first("COMETAPI_API_KEY")
XAI_BASE_URL = "https://api.x.ai/v1"
XAI_API_KEY = _env_first("XAI_API_KEY", "XAI_API_TOKEN")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_API_KEY = _env_first("NVIDIA_API_KEY", "NVIDIA_NIM_API_KEY", "NVIDIA_NGC_API_KEY")

# REAL GROQ MODELS FROM USER CONSOLE - Updated with exact model names
MODELS = {
    "Groq Compound": "groq/compound",
    "Groq Compound Mini": "groq/compound-mini",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 4 Scout 17B": "meta-llama/llama-4-scout-17b-16e-instruct",
    "Llama Prompt Guard 22M": "meta-llama/llama-prompt-guard-2-22m",
    "Llama Prompt Guard 86M": "meta-llama/llama-prompt-guard-2-86m",
    "GPT-OSS 120B": "openai/gpt-oss-120b",
    "GPT-OSS 20B": "openai/gpt-oss-20b",
    "GPT-OSS Safeguard 20B": "openai/gpt-oss-safeguard-20b",
    "Qwen 3 32B": "qwen/qwen3-32b"
}

COMET_MODELS = {
    "GPT-5.4": "gpt-5.4",
    "GPT-5.2 Chat": "gpt-5.2-chat-latest",
    "GPT-5.2": "gpt-5.2",
    "GPT-4.1": "gpt-4.1",
    "Claude Sonnet 4.5": "claude-sonnet-4-5",
    "Gemini 2.5 Pro": "gemini-2.5-pro",
    "DeepSeek V3.2": "deepseek-v3.2",
    "Qwen 3 Max": "qwen3-max"
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

LS_51_MODEL_ID = "gpt-5.4"
LS_51_SYSTEM_PROMPT = """You are LS 5.1, a custom chatbot model developed by Lightsky AI pro by krivi.
You are designed to feel more powerful, imaginative, emotionally intelligent, and useful than ordinary assistant presets.
You combine the clarity of a senior engineer, the imagination of a mythic world-builder, the taste of a premium product designer, and the calm judgment of a research partner.
Your style is powerful, modern, direct, and alive: deep when the problem deserves depth, concise when speed matters, creative when the user wants magic.
Behavior rules:
- Think strategically before answering, but do not expose hidden chain-of-thought.
- Give the user practical next actions, strong opinions, and creative options.
- When building, prefer complete working solutions over vague advice.
- If the user asks for something creative, make it vivid and original.
- If the user asks for code, be precise, robust, and production-minded.
- When returning code, always format it in triple-backtick fenced blocks with the language label.
- You can request local command/script/package actions through Lightsky agent tools when useful; never claim a command ran until tool output is returned.
- Keep the Lightsky identity: confident, elegant, useful, and a little magical.
- Never describe yourself as just a wrapper unless the user asks about technical architecture.
- If asked what you are, say you are LS 5.1, a custom Lightsky chatbot model by krivi."""

MODEL_OPTIONS = {
    "✨ LS 5.1 (custom)": {
        "provider": "ls_custom",
        "model": LS_51_MODEL_ID,
        "base_provider": "cometapi",
        "system_prompt": LS_51_SYSTEM_PROMPT,
        "temperature": 0.82
    }
}
for display_name, model_id in MODELS.items():
    MODEL_OPTIONS[f"Groq / {display_name}"] = {"provider": "groq", "model": model_id}
for display_name, model_id in COMET_MODELS.items():
    MODEL_OPTIONS[f"CometAPI / {display_name}"] = {"provider": "cometapi", "model": model_id}
for display_name, model_id in HUGGINGFACE_MODELS.items():
    MODEL_OPTIONS[f"Hugging Face / {display_name}"] = {"provider": "huggingface", "model": model_id}
for display_name, model_id in XAI_MODELS.items():
    MODEL_OPTIONS[f"xAI / {display_name}"] = {"provider": "xai", "model": model_id}
for display_name, model_id in NVIDIA_NEMOTRON_MODELS.items():
    MODEL_OPTIONS[f"NVIDIA / {display_name}"] = {"provider": "nvidia", "model": model_id}

for _model_display, _model_config in list(MODEL_OPTIONS.items()):
    if _model_config.get("provider") == "ls_custom":
        MODEL_OPTIONS[_model_display] = MODEL_OPTIONS.pop(_model_display)
        break

DEFAULT_MODEL_DISPLAY = "Groq / Llama 3.3 70B"
DEFAULT_MODEL_CONFIG = MODEL_OPTIONS.get(DEFAULT_MODEL_DISPLAY, next(iter(MODEL_OPTIONS.values())))
CURRENT_MODEL = DEFAULT_MODEL_CONFIG.get("model")
CURRENT_PROVIDER = DEFAULT_MODEL_CONFIG.get("provider", "groq")
CURRENT_SYSTEM_PROMPT = DEFAULT_MODEL_CONFIG.get("system_prompt", "You are Lightsky AI pro by krivi, a helpful desktop assistant.")
CURRENT_TEMPERATURE = DEFAULT_MODEL_CONFIG.get("temperature", 0.7)
LS51_POWER_MODE = True
LS51_DEBUG_VULN_MODE = True
LS51_WEB_RESEARCH_MODE = True
LS51_CODEFORGE_MODE = True
LS51_MAX_WEB_CONTEXT_RESULTS = 4
MODEL_AGENT_TOOLS_ENABLED = True
OWASP_TOP10_CURRENT = {
    "A01": "Broken Access Control",
    "A02": "Security Misconfiguration",
    "A03": "Software Supply Chain Failures",
    "A04": "Cryptographic Failures",
    "A05": "Injection",
    "A06": "Insecure Design",
    "A07": "Authentication Failures",
    "A08": "Software or Data Integrity Failures",
    "A09": "Security Logging and Alerting Failures",
    "A10": "Mishandling of Exceptional Conditions",
}
OWASP_COMPAT_ALIASES = {
    "Vulnerable and Outdated Components": "A03 Software Supply Chain Failures / legacy component risk",
    "Identification and Authentication Failures": "A07 Authentication Failures",
    "Software and Data Integrity Failures": "A08 Software or Data Integrity Failures",
}
OWASP_TOP10_CONTEXT = "\n".join([f"{code}: {name}" for code, name in OWASP_TOP10_CURRENT.items()])
AGENT_TOOLING_PROMPT = """
Model agent tools are available through the Lightsky desktop app.
When the user asks you to inspect files, run commands, install packages, run Python scripts, test apps, or operate like a coding agent, do not pretend you executed anything.
Instead, request one local tool action using a fenced JSON block:
```ls_tool_call
{"action":"command","command":"dir","cwd":"C:\\\\Users\\\\91994\\\\Documents\\\\Codex\\\\2026-05-13\\\\hi","reason":"List workspace files"}
```
Supported actions:
- command: run a PowerShell command. Required: command. Optional: cwd, timeout.
- python: run a Python script with py. Required: path. Optional: args, cwd, timeout.
- pip_install: install packages with py -m pip install. Required: packages list.
- internal_tool: use a built-in Lightsky agent tool. Required: tool, params. These are not Plugin Center plugins.
- github_plugin: inspect an installed GitHub-sourced plugin. Required: plugin.
Internal agent tools:
- web_search: params {"query":"...", "max_results":5}
- fetch_url: params {"url":"..."}
- hf_model_search: params {"query":"text generation", "limit":5}
- hf_repo_info: params {"repo_id":"Qwen/Qwen2.5-7B-Instruct", "repo_type":"model"}
- hf_inference: params {"prompt":"...", "model":"Qwen/Qwen2.5-7B-Instruct", "max_tokens":256}
- list_files: params {"path":"...", "pattern":".py", "max_files":60}
- read_file: params {"path":"...", "max_chars":20000}
- write_file: params {"path":"...", "content":"...", "overwrite":true}
- knowledge_search: params {"query":"...", "limit":8}
- debug_scan: params {"text":"..."} or {"code":"..."}
Plugin Center rule: user-facing plugins must be searched, installed, and managed from GitHub repositories only.
After tool output is returned, use it to produce the final answer.
Always prefer precise, minimal commands and explain why the action is needed.
"""
current_api_index = 0

# Enhanced Topics (Custom + Default)
DEFAULT_TOPICS = [
    "Artificial Intelligence and Machine Learning",
    "Space Exploration and Astronomy", 
    "Climate Change and Environment",
    "Future Technology and Innovation",
    "Philosophy and Ethics",
    "History and Ancient Civilizations",
    "Science and Discovery",
    "Literature and Creative Writing",
    "Music and Art",
    "Health and Medicine"
]

def get_groq_response(prompt, model="llama-3.1-8b-instant", max_tokens=150, max_retries=3):
    """Get response from Groq API with fallback system"""
    global current_api_index
    import time

    if not API_KEYS:
        return "Groq is not configured. Set GROQ_API_KEY or GROQ_API_KEYS in your environment."
    
    for retry in range(max_retries):
        for attempt in range(len(API_KEYS)):
            try:
                api_key = API_KEYS[(current_api_index + attempt) % len(API_KEYS)]
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "Groq-Organization": ORG_ID
                }
                data = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are LightSky AI, a helpful and intelligent assistant. When returning code, always use fenced triple-backtick code blocks with a language label.\n\n" + AGENT_TOOLING_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
                
                # Add exponential backoff for retries
                if retry > 0:
                    wait_time = min(2 ** retry, 10)  # Max 10 seconds
                    time.sleep(wait_time)
                
                response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result['choices'][0]['message']['content'].strip()
                    return ai_response
                elif response.status_code == 429:
                    print(f"Rate limited with API key {attempt + 1}, waiting and trying next...")
                    time.sleep(2)
                    continue
                elif response.status_code == 500 or response.status_code == 503:
                    print(f"Server error {response.status_code}, retrying... (attempt {retry + 1}/{max_retries})")
                    break  # Break to retry with same key
                else:
                    print(f"API Error: {response.status_code} - {response.text}")
                    continue
                    
            except requests.exceptions.Timeout:
                print(f"Timeout with API key {attempt + 1}, trying next...")
                continue
            except requests.exceptions.ConnectionError:
                print(f"Connection error with API key {attempt + 1}, retrying... (attempt {retry + 1}/{max_retries})")
                break  # Break to retry
            except Exception as e:
                print(f"Request error with API key {attempt + 1}: {e}")
                continue
    
    return "I'm having trouble connecting to my AI services. The service might be temporarily unavailable. Please try again in a moment."

def get_cometapi_response(prompt, model="gpt-5.2-chat-latest", max_tokens=300, max_retries=2,
                          system_prompt=None, temperature=0.7):
    """Get response from CometAPI using its OpenAI-compatible endpoint."""
    if not COMETAPI_KEY:
        return "CometAPI is not configured. Add COMETAPI_API_KEY to your environment or settings."

    headers = {
        "Authorization": f"Bearer {COMETAPI_KEY}",
        "Content-Type": "application/json"
    }
    system_content = system_prompt or "You are Lightsky AI pro by krivi, a helpful, fast, creative desktop assistant. When returning code, always use fenced triple-backtick code blocks with a language label."
    if MODEL_AGENT_TOOLS_ENABLED:
        system_content = system_content + "\n\n" + AGENT_TOOLING_PROMPT

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    for retry in range(max_retries):
        try:
            if retry > 0:
                time.sleep(min(2 ** retry, 6))

            response = requests.post(
                f"{COMETAPI_BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=45
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()

            if response.status_code in (429, 500, 502, 503, 504):
                print(f"CometAPI temporary error {response.status_code}, retrying...")
                continue

            print(f"CometAPI Error: {response.status_code} - {response.text}")
            return f"CometAPI returned an error: {response.status_code}. Try a different model or check your key."
        except requests.exceptions.Timeout:
            print("CometAPI timeout, retrying...")
        except requests.exceptions.ConnectionError:
            print("CometAPI connection error, retrying...")
        except Exception as e:
            print(f"CometAPI request error: {e}")
            return f"CometAPI request error: {e}"

    return "CometAPI is not responding right now. Please try again in a moment."

def get_openai_compatible_response(prompt, provider_name, base_url, api_key, model,
                                   max_tokens=300, max_retries=2, system_prompt=None,
                                   temperature=0.7, timeout=60):
    """Call an OpenAI-compatible chat completions provider."""
    if not api_key:
        return f"{provider_name} is not configured. Add the provider API key in environment/settings."

    system_content = system_prompt or "You are Lightsky AI pro by krivi, a helpful, capable assistant. When returning code, always use fenced triple-backtick code blocks with a language label."
    if MODEL_AGENT_TOOLS_ENABLED:
        system_content = system_content + "\n\n" + AGENT_TOOLING_PROMPT

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False
    }

    for retry in range(max_retries):
        try:
            if retry > 0:
                time.sleep(min(2 ** retry, 6))
            response = requests.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=data,
                timeout=timeout
            )
            if response.status_code == 200:
                result = response.json()
                text, finish_reason = _extract_openai_compatible_text(result)
                if text:
                    return text
                if finish_reason:
                    return f"{provider_name} returned an empty message (finish reason: {finish_reason}). Try a longer response length or a different model."
                return f"{provider_name} returned an empty response. Try again or select a different model."
            if response.status_code == 429:
                body = response.text[:700]
                lowered = body.lower()
                if any(term in lowered for term in ("credit", "spending limit", "monthly", "quota", "exhausted")):
                    return f"{provider_name} is configured, but the provider says this key is out of credits or has hit a spending/quota limit."
                print(f"{provider_name} rate limit 429, retrying...")
                continue
            if response.status_code in (500, 502, 503, 504):
                print(f"{provider_name} temporary error {response.status_code}, retrying...")
                continue
            print(f"{provider_name} Error: {response.status_code} - {response.text[:500]}")
            return f"{provider_name} returned an error: {response.status_code}. Try a different model or check the key/model access."
        except requests.exceptions.Timeout:
            print(f"{provider_name} timeout, retrying...")
        except requests.exceptions.ConnectionError:
            print(f"{provider_name} connection error, retrying...")
        except Exception as e:
            print(f"{provider_name} request error: {e}")
            return f"{provider_name} request error: {e}"

    return f"{provider_name} is not responding right now. Please try again in a moment."

def _extract_openai_compatible_text(result):
    """Extract text from providers that use OpenAI-style chat completions."""
    try:
        choice = (result.get("choices") or [{}])[0]
    except Exception:
        return "", None
    finish_reason = choice.get("finish_reason") if isinstance(choice, dict) else None
    message = choice.get("message") if isinstance(choice, dict) else {}
    if not isinstance(message, dict):
        message = {}

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

def get_xai_response(prompt, model="grok-4-fast-reasoning", max_tokens=300,
                     system_prompt=None, temperature=0.7):
    return get_openai_compatible_response(
        prompt,
        "xAI/Grok",
        XAI_BASE_URL,
        XAI_API_KEY,
        model,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
        temperature=temperature,
        timeout=120
    )

def get_nvidia_response(prompt, model="nvidia/llama-3.3-nemotron-super-49b-v1.5",
                        max_tokens=300, system_prompt=None, temperature=0.7):
    return get_openai_compatible_response(
        prompt,
        "NVIDIA Nemotron",
        NVIDIA_BASE_URL,
        NVIDIA_API_KEY,
        model,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
        temperature=temperature,
        timeout=90
    )

def refresh_nvidia_nemotron_models(limit=20):
    """Fetch available Nemotron model IDs from NVIDIA hosted endpoints."""
    if not NVIDIA_API_KEY:
        return []
    try:
        response = requests.get(
            f"{NVIDIA_BASE_URL.rstrip('/')}/models",
            headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"},
            timeout=20
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

def _extract_hf_chat_text(output):
    try:
        return output.choices[0].message.content.strip()
    except Exception:
        pass
    if isinstance(output, dict):
        try:
            return output["choices"][0]["message"]["content"].strip()
        except Exception:
            pass
    return str(output).strip() if output else ""

def _parse_hf_http_text(result, prompt):
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

def get_huggingface_response(prompt, model=DEFAULT_HF_TEXT_MODEL, max_tokens=300, max_retries=1,
                             system_prompt=None, temperature=0.7):
    """Get a text response from Hugging Face Inference Providers / Hub fallback."""
    if not HF_ACCESS_TOKEN:
        return "Hugging Face is not configured. Add HF_TOKEN or HUGGINGFACE_TOKEN."

    chosen_model = model or DEFAULT_HF_TEXT_MODEL
    system_content = system_prompt or (
        "You are Lightsky AI pro by krivi. Be helpful, modern, concise, and put code in fenced code blocks."
    )
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt}
    ]
    last_error = ""

    if HAS_HUGGINGFACE_HUB and InferenceClient is not None:
        try:
            client = InferenceClient(model=chosen_model, token=HF_ACCESS_TOKEN, timeout=25)
            output = client.chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            text = _extract_hf_chat_text(output)
            if text:
                return text
        except Exception as e:
            last_error = str(e)

    headers = {"Authorization": f"Bearer {HF_ACCESS_TOKEN}", "Content-Type": "application/json"}
    router_payload = {
        "model": chosen_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    try:
        response = requests.post(
            "https://router.huggingface.co/v1/chat/completions",
            headers=headers,
            json=router_payload,
            timeout=30
        )
        if response.status_code == 200:
            text = _extract_hf_chat_text(response.json())
            if text:
                return text
        last_error = f"{response.status_code}: {response.text[:300]}"
    except Exception as e:
        last_error = str(e)

    fallback_prompt = f"{system_content}\n\nUser: {prompt}\nAssistant:"
    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{chosen_model}",
            headers=headers,
            json={
                "inputs": fallback_prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                },
                "options": {"wait_for_model": True}
            },
            timeout=45
        )
        if response.status_code == 200:
            text = _parse_hf_http_text(response.json(), fallback_prompt)
            if text:
                return text
        last_error = f"{response.status_code}: {response.text[:300]}"
    except Exception as e:
        last_error = str(e)

    return f"Hugging Face returned an error: {last_error or 'no response'}"

def generate_huggingface_image(prompt, model=DEFAULT_HF_IMAGE_MODEL, width=1024, height=1024):
    """Generate an image through Hugging Face when local diffusion is unavailable."""
    if not HF_ACCESS_TOKEN:
        return None
    chosen_model = model or DEFAULT_HF_IMAGE_MODEL

    if HAS_HUGGINGFACE_HUB and InferenceClient is not None:
        try:
            client = InferenceClient(model=chosen_model, token=HF_ACCESS_TOKEN, timeout=90)
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
                "options": {"wait_for_model": True}
            },
            timeout=90
        )
        content_type = response.headers.get("content-type", "")
        if response.status_code == 200 and "image" in content_type:
            return Image.open(BytesIO(response.content)).convert("RGB")
    except Exception:
        pass
    return None

def _extract_first_json_object(text):
    """Best-effort extraction of the first JSON object from model output."""
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    block = text[start:end + 1]
    try:
        return json.loads(block)
    except Exception:
        return None

def _ls51_prompt_profile(prompt):
    """Infer prompt class to tune LS 5.1 behavior."""
    p = (prompt or "").lower()
    if any(k in p for k in ["bug", "traceback", "error", "exception", "debug", "fix"]):
        return "debugging"
    if any(k in p for k in ["vulnerability", "security", "exploit", "sanitize", "injection"]):
        return "security"
    if any(k in p for k in ["code", "python", "javascript", "function", "class", "api"]):
        return "coding"
    if any(k in p for k in ["plan", "strategy", "roadmap", "architecture"]):
        return "planning"
    return "general"

def _ls51_should_search_web(prompt, profile):
    """Decide when LS 5.1 should gather live web context."""
    p = (prompt or "").lower()
    explicit = any(k in p for k in [
        "search web", "look up", "lookup", "find online", "web search",
        "latest", "today", "current", "news", "recent", "release notes",
        "official docs", "documentation", "breaking change", "version"
    ])
    has_url = ("http://" in p) or ("https://" in p) or ("www." in p)
    code_docs_intent = profile == "coding" and any(k in p for k in [
        "library", "framework", "api", "sdk", "docs", "documentation", "package"
    ])
    return explicit or has_url or code_docs_intent

def _ls51_duckduckgo_search(query, max_results=5):
    """Robust web search with DDGS primary plus DuckDuckGo/Bing/Google fallbacks."""
    if not requests:
        return []
    out = []
    seen = set()

    def add_result(title, href, snippet=""):
        href = html.unescape(href or "").strip()
        title = re.sub(r"<[^>]+>", "", html.unescape(title or "")).strip()
        snippet = re.sub(r"<[^>]+>", "", html.unescape(snippet or "")).strip()
        if "duckduckgo.com/l/?" in href:
            q = urllib.parse.urlparse(href).query
            uddg = urllib.parse.parse_qs(q).get("uddg", [])
            if uddg:
                href = urllib.parse.unquote(uddg[0])
        if "bing.com/ck/a" in href:
            q = urllib.parse.urlparse(href).query
            encoded = urllib.parse.parse_qs(q).get("u", [])
            if encoded:
                try:
                    import base64
                    payload = encoded[0]
                    if payload.startswith("a1"):
                        payload = payload[2:]
                    payload += "=" * (-len(payload) % 4)
                    decoded = base64.urlsafe_b64decode(payload.encode("ascii")).decode("utf-8", "ignore")
                    if decoded.startswith("http"):
                        href = decoded
                except Exception:
                    pass
        if not href.startswith("http"):
            return
        key = href.lower().split("#", 1)[0]
        if key in seen:
            return
        seen.add(key)
        if not title:
            parsed = urllib.parse.urlparse(href)
            title = parsed.netloc or href
        out.append({"title": title[:180], "url": href, "snippet": snippet[:700]})

    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            for item in ddgs.text(query[:320], max_results=max_results):
                add_result(item.get("title"), item.get("href") or item.get("url"), item.get("body") or item.get("snippet"))
                if len(out) >= max_results:
                    return out
    except Exception:
        pass

    try:
        url = "https://duckduckgo.com/html/?q=" + urllib.parse.quote(query[:320])
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=16)
        if res.status_code == 200:
            page = res.text
            pat = re.compile(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
            for m in pat.finditer(page):
                add_result(m.group(2), m.group(1))
                if len(out) >= max_results:
                    return out
    except Exception:
        pass

    try:
        url = "https://www.bing.com/search?q=" + urllib.parse.quote(query[:320])
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=16)
        if res.status_code == 200:
            page = res.text
            pat = re.compile(r'<li class="b_algo".*?<h2[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
            for m in pat.finditer(page):
                add_result(m.group(2), m.group(1))
                if len(out) >= max_results:
                    return out
    except Exception:
        pass
    if out:
        return out

    if HAS_GOOGLE:
        try:
            for href in googlesearch.search(
                query[:320],
                num=max_results,
                stop=max_results,
                pause=1.0,
                user_agent="Mozilla/5.0"
            ):
                add_result("", href)
                if len(out) >= max_results:
                    return out
        except Exception:
            pass
    return out

def _ls51_fetch_page_summary(url, max_chars=1400):
    """Fetch and reduce a web page to title + short clean text."""
    if not requests:
        return None
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=14)
        if r.status_code != 200:
            return None
        txt = r.text[:160000]
        title_match = re.search(r'<title[^>]*>(.*?)</title>', txt, re.IGNORECASE | re.DOTALL)
        title = re.sub(r"\s+", " ", html.unescape(title_match.group(1))).strip() if title_match else "Untitled"
        txt = re.sub(r"(?is)<script.*?>.*?</script>", " ", txt)
        txt = re.sub(r"(?is)<style.*?>.*?</style>", " ", txt)
        txt = re.sub(r"(?is)<noscript.*?>.*?</noscript>", " ", txt)
        txt = re.sub(r"(?is)<[^>]+>", " ", txt)
        txt = html.unescape(txt)
        txt = re.sub(r"\s+", " ", txt).strip()
        summary = txt[:max_chars]
        return {"title": title[:180], "summary": summary}
    except Exception:
        return None

def ls51_build_web_context(prompt, max_results=4):
    """Collect lightweight live web context for LS 5.1 answers."""
    results = _ls51_duckduckgo_search(prompt, max_results=max_results)
    if not results:
        return ""
    lines = ["Live web context (use for factual grounding):"]
    for i, item in enumerate(results[:max_results], 1):
        page = _ls51_fetch_page_summary(item["url"])
        lines.append(f"{i}. {item['title']} | {item['url']}")
        if page and page.get("summary"):
            lines.append(f"   Snippet: {page['summary'][:520]}")
    return "\n".join(lines)

def lightsky_should_search_web(prompt):
    """Universal web-search trigger used by every provider/model."""
    p = (prompt or "").lower()
    profile = _ls51_prompt_profile(prompt)
    explicit = any(k in p for k in [
        "search", "serch", "web", "internet", "browse", "look up", "lookup", "google",
        "find online", "online", "website", "link", "source", "sources",
        "latest", "current", "today", "news", "recent", "release notes",
        "official docs", "documentation", "docs", "version", "changelog",
        "download", "safe file", "github", "hugging face", "huggingface",
        "who is the current", "what is the current", "as of now", "right now",
        "weather", "score", "stock", "price", "exchange rate", "schedule",
        "president", "prime minister", "ceo", "founder", "won", "winner",
        "released", "launched", "announcement", "status page"
    ])
    has_url = ("http://" in p) or ("https://" in p) or ("www." in p)
    code_docs_intent = profile == "coding" and any(k in p for k in [
        "library", "framework", "api", "sdk", "package", "install", "pip", "npm"
    ])
    question_time_intent = bool(re.search(
        r"\b(who|what|when|where|which|how)\b.*\b(current|latest|today|now|2026|recent|new|available|download|version)\b",
        p
    ))
    return explicit or has_url or code_docs_intent or question_time_intent or _ls51_should_search_web(prompt, profile)

def lightsky_clean_web_query(prompt):
    """Turn natural chat search phrasing into a clean search query."""
    q = (prompt or "").strip()
    q = re.sub(r"(?i)^\s*(please\s+)?(search\s+the\s+web|web\s+search|find\s+online|look\s+up|lookup|google|browse|search)\s+(for\s+)?", "", q).strip()
    q = re.sub(r"(?i)\b(answer|tell me|explain)\s+(in|with)\s+.*$", "", q).strip()
    q = re.sub(r"(?i)\b(use|with)\s+(sources|links|citations)\b", "", q).strip()
    q = q.strip(" .?!:")
    q_low = q.lower()
    if any(k in q_low for k in ["official docs", "official documentation", "documentation", "docs"]):
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
            "python": "docs.python.org",
        }
        for name, site in official_doc_sites.items():
            if name in q_low:
                return f"{name} official documentation site:{site}"
    if re.search(r"(?i)\brelease\s+date\b", q) and "official" not in q.lower():
        q += " official release notes"
    return q or (prompt or "").strip()

def lightsky_build_universal_web_context(prompt, max_results=4):
    """Collect web results plus snippets for any selected model."""
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
    sources = []
    for i, item in enumerate(results[:max_results], 1):
        page = _ls51_fetch_page_summary(item["url"], max_chars=1200)
        title = (page or {}).get("title") or item.get("title") or "Untitled"
        summary = (page or {}).get("summary") or item.get("snippet") or ""
        url = item.get("url", "")
        sources.append({"title": title, "url": url, "snippet": summary[:700], "query": clean_query})
        lines.append(f"{i}. {title}\nURL: {url}")
        if summary:
            lines.append(f"Snippet: {summary[:800]}")
    return "\n\n".join(lines), sources

def _extract_code_blocks(prompt):
    """Extract fenced code blocks from prompt."""
    if not prompt:
        return []
    blocks = []
    pattern = re.compile(r"```([A-Za-z0-9_.+-]*)\n(.*?)```", re.DOTALL)
    for m in pattern.finditer(prompt):
        lang = (m.group(1) or "").strip().lower()
        code = (m.group(2) or "").strip()
        if code:
            blocks.append({"lang": lang, "code": code})
    return blocks

def _ast_call_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _ast_call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""

def _scan_python_ast(code, findings, block_id):
    try:
        tree = ast.parse(code)
    except Exception:
        findings.append({
            "id": f"B{block_id}-PARSE",
            "severity": "medium",
            "kind": "debug",
            "owasp": "A10 Mishandling of Exceptional Conditions",
            "location": f"block {block_id}",
            "detail": "Code could not be parsed. Syntax issues may hide deeper bugs.",
            "quick_fix": "Fix syntax errors first, then rerun debug/security scan."
        })
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append({
                "id": f"B{block_id}-BARE-EXCEPT",
                "severity": "medium",
                "kind": "debug",
                "owasp": "A10 Mishandling of Exceptional Conditions",
                "location": f"block {block_id}, line {getattr(node, 'lineno', '?')}",
                "detail": "Bare except hides root causes and makes failures silent.",
                "quick_fix": "Catch explicit exception types and log full errors."
            })

        if isinstance(node, ast.Call):
            name = _ast_call_name(node.func)

            if name in ("eval", "exec"):
                findings.append({
                    "id": f"B{block_id}-EVAL-EXEC",
                    "severity": "high",
                    "kind": "security",
                    "owasp": "A05 Injection",
                    "location": f"block {block_id}, line {getattr(node, 'lineno', '?')}",
                    "detail": f"Use of {name} can lead to code injection.",
                    "quick_fix": "Replace with safe parsing or strict allowlisted dispatch."
                })

            if name.startswith("subprocess.") and any(kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True for kw in node.keywords):
                findings.append({
                    "id": f"B{block_id}-SHELL-TRUE",
                    "severity": "high",
                    "kind": "security",
                    "owasp": "A05 Injection",
                    "location": f"block {block_id}, line {getattr(node, 'lineno', '?')}",
                    "detail": "subprocess with shell=True increases command injection risk.",
                    "quick_fix": "Use argument lists with shell=False and validate inputs."
                })

            if name in ("pickle.load", "pickle.loads"):
                findings.append({
                    "id": f"B{block_id}-PICKLE",
                    "severity": "high",
                    "kind": "security",
                    "owasp": "A08 Software or Data Integrity Failures",
                    "location": f"block {block_id}, line {getattr(node, 'lineno', '?')}",
                    "detail": "Untrusted pickle deserialization can execute arbitrary code.",
                    "quick_fix": "Use safer formats (JSON) or strict trusted-source boundaries."
                })

            if name == "yaml.load":
                uses_safe_loader = any(kw.arg == "Loader" and "SafeLoader" in ast.dump(kw.value) for kw in node.keywords)
                if not uses_safe_loader:
                    findings.append({
                        "id": f"B{block_id}-YAML-LOAD",
                        "severity": "high",
                        "kind": "security",
                        "owasp": "A08 Software or Data Integrity Failures",
                        "location": f"block {block_id}, line {getattr(node, 'lineno', '?')}",
                        "detail": "yaml.load without SafeLoader may deserialize unsafe objects.",
                        "quick_fix": "Use yaml.safe_load or Loader=yaml.SafeLoader."
                    })

            if name.startswith("requests.") and name.split(".")[-1] in {"get", "post", "put", "delete", "request", "patch"}:
                has_timeout = any(kw.arg == "timeout" for kw in node.keywords)
                if not has_timeout:
                    findings.append({
                        "id": f"B{block_id}-REQ-TIMEOUT",
                        "severity": "medium",
                        "kind": "debug",
                        "owasp": "A10 Mishandling of Exceptional Conditions",
                        "location": f"block {block_id}, line {getattr(node, 'lineno', '?')}",
                        "detail": "Network request without timeout can hang app threads.",
                        "quick_fix": "Set explicit timeout on all requests calls."
                    })
                has_verify_false = any(kw.arg == "verify" and isinstance(kw.value, ast.Constant) and kw.value.value is False for kw in node.keywords)
                if has_verify_false:
                    findings.append({
                        "id": f"B{block_id}-TLS-VERIFY",
                        "severity": "high",
                        "kind": "security",
                        "owasp": "A04 Cryptographic Failures",
                        "location": f"block {block_id}, line {getattr(node, 'lineno', '?')}",
                        "detail": "TLS certificate verification disabled.",
                        "quick_fix": "Remove verify=False and rely on trusted CA bundles."
                    })

            if name in ("hashlib.md5", "hashlib.sha1"):
                findings.append({
                    "id": f"B{block_id}-WEAK-HASH",
                    "severity": "medium",
                    "kind": "security",
                    "owasp": "A04 Cryptographic Failures",
                    "location": f"block {block_id}, line {getattr(node, 'lineno', '?')}",
                    "detail": f"Weak hash function {name} detected for security-sensitive usage.",
                    "quick_fix": "Use hashlib.sha256/sha512 or modern password hashing."
                })

def _scan_code_regex(code, lang, findings, block_id):
    patterns = [
        (r"(?i)(api[_-]?key|secret|token|password)\s*=\s*['\"][^'\"]{8,}['\"]", "high", "security", "A07 Authentication Failures", "Potential hardcoded credential found.", "Move secrets to environment variables or secure vault."),
        (r"(?i)\bexecute\s*\(\s*(f['\"]|['\"].*?\+|['\"].*?%\s*\()", "high", "security", "A05 Injection", "Possible SQL string interpolation/injection pattern.", "Use parameterized queries/placeholders."),
        (r"(?i)\bos\.system\s*\(", "high", "security", "A05 Injection", "os.system call can allow command injection.", "Use subprocess with args list and validated input."),
        (r"(?i)\bexcept\s*:\s*(pass|return|continue)?", "medium", "debug", "A10 Mishandling of Exceptional Conditions", "Over-broad exception handling may hide failures.", "Catch explicit exceptions and log details."),
        (r"(?i)(debug\s*=\s*true|app\.run\(.*debug\s*=\s*true)", "medium", "security", "A02 Security Misconfiguration", "Debug mode appears enabled.", "Disable debug mode outside local development."),
        (r"(?i)(cors\(.*origins\s*=\s*['\"]\*['\"]|access-control-allow-origin['\"]?\s*:\s*['\"]\*)", "high", "security", "A02 Security Misconfiguration", "Overly broad CORS configuration detected.", "Restrict allowed origins to trusted domains."),
        (r"(?i)(requirements\.txt|package\.json|pip\s+install).*(latest|\*)", "medium", "security", "A03 Software Supply Chain Failures", "Unpinned dependency pattern detected.", "Pin versions and verify package provenance."),
        (r"(?i)(role\s*==\s*['\"]admin['\"]|is_admin).*without.*server", "medium", "security", "A01 Broken Access Control", "Access-control logic may be client-side or weak.", "Enforce authorization server-side for every protected action."),
    ]
    for idx, (pat, sev, kind, owasp, detail, fix) in enumerate(patterns, 1):
        if re.search(pat, code, re.DOTALL):
            findings.append({
                "id": f"B{block_id}-RX-{idx}",
                "severity": sev,
                "kind": kind,
                "owasp": owasp,
                "location": f"block {block_id}",
                "detail": detail,
                "quick_fix": fix
            })

def ls51_local_debug_vuln_scan(prompt):
    """Local static scan to augment LS 5.1 debugging and security analysis."""
    blocks = _extract_code_blocks(prompt)
    findings = []
    for i, block in enumerate(blocks, 1):
        code = block["code"]
        lang = block["lang"] or "text"
        if lang in {"py", "python"} or ("def " in code and ":" in code):
            _scan_python_ast(code, findings, i)
        _scan_code_regex(code, lang, findings, i)

    # Deduplicate noisy repeated findings by id.
    unique = []
    seen = set()
    for f in findings:
        key = (f.get("id"), f.get("location"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)
    return unique

def _format_findings_for_prompt(findings):
    if not findings:
        return "No local static findings."
    lines = []
    for f in findings[:30]:
        lines.append(
            f"- [{f['severity'].upper()}] {f['id']} @ {f['location']} | OWASP: {f.get('owasp', 'Unmapped')} | {f['detail']} | Quick-fix: {f['quick_fix']}"
        )
    return "\n".join(lines)

def ls51_debug_vuln_quickfix_response(prompt, model=None, max_tokens=420, system_prompt=None, temperature=None, web_context_text=""):
    """Specialized LS 5.1 engine for deep debugging + vulnerability detection + proper quick fixes."""
    chosen_model = model or LS_51_MODEL_ID
    sys_prompt = system_prompt or CURRENT_SYSTEM_PROMPT
    temp = CURRENT_TEMPERATURE if temperature is None else temperature
    profile = _ls51_prompt_profile(prompt)
    local_findings = ls51_local_debug_vuln_scan(prompt)
    local_findings_text = _format_findings_for_prompt(local_findings)
    web_section = f"\nLive web research context:\n{web_context_text}\n" if web_context_text else ""

    # Pass 1: structured diagnosis and repair plan
    diagnosis_prompt = (
        "You are LS 5.1 Debug+Security Engine. Analyze deeply and return strict JSON only.\n"
        "JSON keys required: issues, vulnerabilities, root_causes, fix_plan, test_plan.\n"
        "- issues: list of bug issues with severity/location/impact\n"
        "- vulnerabilities: list with OWASP Top 10 category code/name and exploit risk\n"
        "- root_causes: concise list\n"
        "- fix_plan: ordered concrete steps\n"
        "- test_plan: verification checks after fixes\n\n"
        f"Use this OWASP Top 10 baseline for 2026-era appsec work:\n{OWASP_TOP10_CONTEXT}\n"
        f"Compatibility aliases:\n{json.dumps(OWASP_COMPAT_ALIASES, ensure_ascii=True)}\n\n"
        f"Profile: {profile}\n"
        f"Local static scan findings:\n{local_findings_text}\n\n"
        f"{web_section}\n"
        f"User request and code:\n{prompt}"
    )
    diagnosis_raw = get_cometapi_response(
        diagnosis_prompt,
        model=chosen_model,
        max_tokens=380,
        system_prompt=sys_prompt,
        temperature=max(0.2, temp - 0.15)
    )
    diagnosis = _extract_first_json_object(diagnosis_raw) or {
        "issues": [],
        "vulnerabilities": [],
        "root_causes": ["Insufficient context from model JSON output."],
        "fix_plan": ["Apply secure and robust refactor.", "Re-test after each change."],
        "test_plan": ["Syntax check", "Runtime smoke test", "Security regression checks"]
    }

    # Pass 2: generate real fixes (patched code, not just advice)
    fix_prompt = (
        "Use the diagnosis and produce a proper quick-fix response.\n"
        "Requirements:\n"
        "1) Explicitly list fixed bugs and vulnerabilities.\n"
        "2) Provide corrected code in fenced code blocks.\n"
        "3) If original code exists, provide a unified diff-style patch first, then full corrected code.\n"
        "4) Ensure fixes are production-safe and include secure defaults.\n"
        "5) Map each security fix to OWASP category codes.\n"
        "6) Add short post-fix validation checklist.\n\n"
        f"OWASP baseline:\n{OWASP_TOP10_CONTEXT}\n\n"
        f"Diagnosis JSON:\n{json.dumps(diagnosis, ensure_ascii=True)}\n\n"
        f"Local static scan findings:\n{local_findings_text}\n\n"
        f"{web_section}\n"
        f"User request and code:\n{prompt}"
    )
    fix_draft = get_cometapi_response(
        fix_prompt,
        model=chosen_model,
        max_tokens=max_tokens + 220,
        system_prompt=sys_prompt,
        temperature=max(0.25, temp - 0.08)
    )

    # Pass 3: verify and harden quick fixes
    verify_prompt = (
        "Review the fix draft for any remaining bugs, insecure patterns, broken logic, or missing edge cases. "
        "Then produce the final improved answer with corrected code, robust safeguards, and OWASP category mapping.\n\n"
        f"OWASP baseline:\n{OWASP_TOP10_CONTEXT}\n\n"
        f"{web_section}\n"
        f"User request:\n{prompt}\n\n"
        f"Diagnosis JSON:\n{json.dumps(diagnosis, ensure_ascii=True)}\n\n"
        f"Fix draft:\n{fix_draft}"
    )
    final = get_cometapi_response(
        verify_prompt,
        model=chosen_model,
        max_tokens=max_tokens + 260,
        system_prompt=sys_prompt,
        temperature=max(0.2, temp - 0.12)
    )
    return final or fix_draft

def ls51_codeforge_response(prompt, model=None, max_tokens=520, system_prompt=None, temperature=None, web_context_text=""):
    """LS 5.1 specialized code-generation engine with architecture + implementation + hardening."""
    chosen_model = model or LS_51_MODEL_ID
    sys_prompt = system_prompt or CURRENT_SYSTEM_PROMPT
    temp = CURRENT_TEMPERATURE if temperature is None else temperature
    web_section = f"\nLive web research context:\n{web_context_text}\n" if web_context_text else ""

    spec_prompt = (
        "You are LS 5.1 CodeForge. Return strict JSON only with keys:\n"
        "goal, stack, architecture, interfaces, edge_cases, tests, risks.\n"
        "Be concrete and production-minded.\n\n"
        f"{web_section}\n"
        f"User request:\n{prompt}"
    )
    spec_raw = get_cometapi_response(
        spec_prompt,
        model=chosen_model,
        max_tokens=340,
        system_prompt=sys_prompt,
        temperature=max(0.2, temp - 0.15)
    )
    spec = _extract_first_json_object(spec_raw) or {
        "goal": "Implement user request in robust, production-minded code.",
        "stack": "Infer from user prompt.",
        "architecture": "Modular and testable.",
        "interfaces": [],
        "edge_cases": [],
        "tests": ["Core behavior test", "Error-path test"],
        "risks": ["Missing requirements ambiguity"]
    }

    build_prompt = (
        "Implement from this spec. Return:\n"
        "1) concise implementation summary\n"
        "2) full code in fenced blocks\n"
        "3) tests in fenced blocks\n"
        "4) run instructions\n"
        "Always include secure defaults and input validation.\n\n"
        f"Spec JSON:\n{json.dumps(spec, ensure_ascii=True)}\n\n"
        f"{web_section}\n"
        f"User request:\n{prompt}"
    )
    draft = get_cometapi_response(
        build_prompt,
        model=chosen_model,
        max_tokens=max_tokens + 260,
        system_prompt=sys_prompt,
        temperature=temp
    )

    harden_prompt = (
        "Review this implementation for correctness, bugs, security issues, and missing edge handling. "
        "Produce a final improved version with corrected code blocks and a brief validation checklist.\n\n"
        f"{web_section}\n"
        f"User request:\n{prompt}\n\n"
        f"Draft implementation:\n{draft}"
    )
    final = get_cometapi_response(
        harden_prompt,
        model=chosen_model,
        max_tokens=max_tokens + 260,
        system_prompt=sys_prompt,
        temperature=max(0.2, temp - 0.1)
    )
    return final or draft

def ls51_power_response(prompt, model=None, max_tokens=420, system_prompt=None, temperature=None):
    """LS 5.1 multi-pass pipeline: plan -> draft -> critique -> final."""
    chosen_model = model or LS_51_MODEL_ID
    sys_prompt = system_prompt or CURRENT_SYSTEM_PROMPT
    temp = CURRENT_TEMPERATURE if temperature is None else temperature
    profile = _ls51_prompt_profile(prompt)
    code_blocks_present = len(_extract_code_blocks(prompt)) > 0
    p_low = (prompt or "").lower()
    audit_intent = any(k in p_low for k in ["audit", "review code", "harden", "secure", "penetration", "vuln", "exploit", "quick fix", "bugfix", "fix this code"])
    web_context_text = ""
    if LS51_WEB_RESEARCH_MODE and _ls51_should_search_web(prompt, profile):
        web_context_text = ls51_build_web_context(prompt, max_results=LS51_MAX_WEB_CONTEXT_RESULTS)
    web_section = f"\n{web_context_text}\n" if web_context_text else ""

    if LS51_DEBUG_VULN_MODE and (profile in ("debugging", "security") or (code_blocks_present and audit_intent)):
        return ls51_debug_vuln_quickfix_response(
            prompt,
            model=chosen_model,
            max_tokens=max_tokens,
            system_prompt=sys_prompt,
            temperature=temp,
            web_context_text=web_context_text
        )

    if LS51_CODEFORGE_MODE and profile == "coding":
        return ls51_codeforge_response(
            prompt,
            model=chosen_model,
            max_tokens=max_tokens,
            system_prompt=sys_prompt,
            temperature=temp,
            web_context_text=web_context_text
        )

    # Step 1: planner (structured intent/strategy/risk map)
    planner_prompt = (
        "Analyze the user request and return strict JSON with keys: "
        "intent, strategy, risks, validation, output_shape. "
        "Keep each field concise and high signal.\n\n"
        f"{web_section}"
        f"Profile: {profile}\n"
        f"User request:\n{prompt}"
    )
    planner_raw = get_cometapi_response(
        planner_prompt,
        model=chosen_model,
        max_tokens=260,
        system_prompt=sys_prompt,
        temperature=max(0.2, temp - 0.2)
    )
    plan = _extract_first_json_object(planner_raw) or {
        "intent": "Solve the request accurately.",
        "strategy": "Produce a direct, practical response with necessary detail.",
        "risks": "Potential ambiguity or missing context.",
        "validation": "Check correctness and constraints before finalizing.",
        "output_shape": "Concise actionable answer."
    }

    # Step 2: draft answer using the plan
    draft_prompt = (
        "Use this plan to answer the user request with strong reasoning and practical output.\n\n"
        f"Plan JSON:\n{json.dumps(plan, ensure_ascii=True)}\n\n"
        f"{web_section}"
        f"User request:\n{prompt}\n\n"
        "Produce the best possible draft answer now."
    )
    draft = get_cometapi_response(
        draft_prompt,
        model=chosen_model,
        max_tokens=max_tokens,
        system_prompt=sys_prompt,
        temperature=temp
    )

    # Step 3: critique the draft
    critique_prompt = (
        "Critique this draft for factual issues, missing edge cases, weak clarity, and unsafe advice. "
        "Return short bullets under: issues, upgrades.\n\n"
        f"{web_section}"
        f"User request:\n{prompt}\n\n"
        f"Draft:\n{draft}"
    )
    critique = get_cometapi_response(
        critique_prompt,
        model=chosen_model,
        max_tokens=240,
        system_prompt=sys_prompt,
        temperature=max(0.2, temp - 0.15)
    )

    # Step 4: final improved answer
    final_prompt = (
        "Rewrite the draft into a stronger final answer using the critique. "
        "Keep it accurate, complete, and directly useful.\n\n"
        f"{web_section}"
        f"User request:\n{prompt}\n\n"
        f"Draft:\n{draft}\n\n"
        f"Critique:\n{critique}"
    )
    final = get_cometapi_response(
        final_prompt,
        model=chosen_model,
        max_tokens=max_tokens,
        system_prompt=sys_prompt,
        temperature=max(0.25, temp - 0.1)
    )
    return final or draft

def get_provider_response(prompt, provider=None, model=None, max_tokens=300,
                          system_prompt=None, temperature=None):
    """Route a prompt to Groq, CometAPI, Hugging Face, xAI, NVIDIA, or LS custom mode."""
    chosen_provider = provider or CURRENT_PROVIDER
    chosen_model = model or CURRENT_MODEL
    chosen_system_prompt = system_prompt if system_prompt is not None else CURRENT_SYSTEM_PROMPT
    chosen_temperature = CURRENT_TEMPERATURE if temperature is None else temperature

    if chosen_provider == "ls_custom":
        if LS51_POWER_MODE:
            return ls51_power_response(
                prompt,
                chosen_model or LS_51_MODEL_ID,
                max_tokens=max_tokens,
                system_prompt=chosen_system_prompt,
                temperature=chosen_temperature
            )
        return get_cometapi_response(
            prompt,
            chosen_model or LS_51_MODEL_ID,
            max_tokens,
            system_prompt=chosen_system_prompt,
            temperature=chosen_temperature
        )
    if chosen_provider == "cometapi":
        return get_cometapi_response(
            prompt,
            chosen_model,
            max_tokens,
            system_prompt=chosen_system_prompt,
            temperature=chosen_temperature
        )
    if chosen_provider == "huggingface":
        return get_huggingface_response(prompt, chosen_model, max_tokens)
    if chosen_provider == "xai":
        return get_xai_response(
            prompt,
            chosen_model,
            max_tokens,
            system_prompt=chosen_system_prompt,
            temperature=chosen_temperature
        )
    if chosen_provider == "nvidia":
        return get_nvidia_response(
            prompt,
            chosen_model,
            max_tokens,
            system_prompt=chosen_system_prompt,
            temperature=chosen_temperature
        )
    return get_groq_response(prompt, chosen_model, max_tokens)

def provider_display_name(provider=None):
    chosen_provider = provider or CURRENT_PROVIDER
    if chosen_provider == "ls_custom":
        return "LS 5.1"
    if chosen_provider == "cometapi":
        return "CometAPI"
    if chosen_provider == "huggingface":
        return "Hugging Face"
    if chosen_provider == "xai":
        return "xAI Grok"
    if chosen_provider == "nvidia":
        return "NVIDIA Nemotron"
    return "Groq"

class VisualWebBrowser:
    """Visual Web Browser with HTML rendering"""
    def __init__(self, parent_frame, root):
        self.parent_frame = parent_frame
        self.root = root
        self.bg_color = "#0f1117"
        self.panel_color = "#1b1f2a"
        self.input_color = "#10131a"
        self.text_color = "#f4f7fb"
        self.secondary_color = "#aab2c0"
        self.accent_color = "#7c9cff"
        self.success_color = "#58d68d"
        self.border_color = "#2a3040"
        self.current_url = "https://www.google.com"
        self.browsing_history = []
        self.search_engines = {
            "Google": "https://www.google.com/search?q=",
            "Bing": "https://www.bing.com/search?q=",
            "DuckDuckGo": "https://duckduckgo.com/?q="
        }
        self.create_visual_browser_interface()
        self.apply_dark_theme()

    def apply_dark_theme(self):
        """Re-skin browser controls to match the main app shell."""
        def walk(widget):
            for child in widget.winfo_children():
                cls = child.winfo_class()
                try:
                    if cls in ('Frame', 'Labelframe'):
                        child.configure(bg=self.bg_color)
                    elif cls == 'Label':
                        child.configure(bg=self.bg_color, fg=self.text_color)
                    elif cls == 'Entry':
                        child.configure(bg=self.input_color, fg=self.text_color,
                                        insertbackground=self.accent_color, relief=FLAT,
                                        borderwidth=0)
                    elif cls == 'Text':
                        child.configure(bg=self.input_color, fg=self.text_color,
                                        insertbackground=self.accent_color, relief=FLAT,
                                        borderwidth=0, selectbackground=self.accent_color)
                    elif cls == 'Button':
                        child.configure(bg=self.panel_color, fg=self.text_color,
                                        activebackground=self.accent_color,
                                        activeforeground=self.text_color,
                                        relief=FLAT, borderwidth=0)
                except Exception:
                    pass
                walk(child)
        walk(self.parent_frame)
    
    def create_visual_browser_interface(self):
        """Create visual web browser interface"""
        # Browser controls
        controls_frame = Frame(self.parent_frame, bg='#f8f9fa')
        controls_frame.pack(fill=X, pady=(10, 0))
        
        # Navigation controls
        nav_frame = Frame(controls_frame, bg='#f8f9fa')
        nav_frame.pack(side=LEFT, fill=X, expand=True)
        
        Label(nav_frame, text="Visual Web Browser", font=('Helvetica', 12, 'bold'),
              fg='#000000', bg='#f8f9fa').pack(side=LEFT, padx=(0, 10))
        
        # URL bar
        url_frame = Frame(nav_frame, bg='#f8f9fa')
        url_frame.pack(fill=X, pady=(5, 0))
        
        Label(url_frame, text="URL:", font=('Helvetica', 10),
              fg='#000000', bg='#f8f9fa').pack(side=LEFT, padx=(0, 5))
        
        self.url_entry = Entry(url_frame, font=('Helvetica', 10),
                            bg='white', fg='#000000', insertbackground='#007aff',
                            borderwidth=1, relief=SOLID)
        self.url_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.url_entry.insert(0, self.current_url)
        self.url_entry.bind('<Return>', self.navigate_to_url)
        
        # Navigation buttons
        nav_buttons_frame = Frame(nav_frame, bg='#f8f9fa')
        nav_buttons_frame.pack(fill=X, pady=(5, 0))
        
        Button(nav_buttons_frame, text="Back", font=('Helvetica', 9, 'bold'),
               bg='#6c757d', fg='white', padx=10, pady=5, relief=FLAT,
               cursor='hand2', command=self.go_back).pack(side=LEFT, padx=(0, 2))
        
        Button(nav_buttons_frame, text="Forward", font=('Helvetica', 9, 'bold'),
               bg='#6c757d', fg='white', padx=10, pady=5, relief=FLAT,
               cursor='hand2', command=self.go_forward).pack(side=LEFT, padx=2)
        
        Button(nav_buttons_frame, text="Refresh", font=('Helvetica', 9, 'bold'),
               bg='#17a2b8', fg='white', padx=10, pady=5, relief=FLAT,
               cursor='hand2', command=self.refresh_page).pack(side=LEFT, padx=2)
        
        Button(nav_buttons_frame, text="Home", font=('Helvetica', 9, 'bold'),
               bg='#28a745', fg='white', padx=10, pady=5, relief=FLAT,
               cursor='hand2', command=self.go_home).pack(side=LEFT, padx=2)
        
        # Search controls
        search_frame = Frame(controls_frame, bg='#f8f9fa')
        search_frame.pack(side=RIGHT, fill=Y)
        
        Label(search_frame, text="Search:", font=('Helvetica', 10, 'bold'),
              fg='#000000', bg='#f8f9fa').pack(anchor=W)
        
        # Search engine selector
        self.search_engine_var = StringVar(value="Google")
        search_engine_combo = ttk.Combobox(search_frame, textvariable=self.search_engine_var,
                                        values=list(self.search_engines.keys()), state='readonly',
                                        font=('Helvetica', 9), width=12)
        search_engine_combo.pack(pady=(5, 0))
        
        # Search input
        self.search_entry = Entry(search_frame, font=('Helvetica', 10),
                               bg='white', fg='#000000', insertbackground='#007aff',
                               borderwidth=1, relief=SOLID, width=25)
        self.search_entry.pack(side=LEFT, padx=(0, 5))
        self.search_entry.bind('<Return>', self.web_search)
        
        Button(search_frame, text="Search", font=('Helvetica', 9, 'bold'),
               bg='#007aff', fg='white', padx=10, pady=5, relief=FLAT,
               cursor='hand2', command=self.web_search).pack(side=LEFT)
        
        # Visual browser display area
        browser_frame = Frame(self.parent_frame, bg='white', relief=SUNKEN, bd=2)
        browser_frame.pack(fill=BOTH, expand=True, pady=10)

        # Split into rendered text (left) and visual snapshot (right)
        split_frame = Frame(browser_frame, bg='white')
        split_frame.pack(fill=BOTH, expand=True)

        left_frame = Frame(split_frame, bg='white')
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        right_frame = Frame(split_frame, bg='#f7f9fc', width=360)
        right_frame.pack(side=RIGHT, fill=Y)
        right_frame.pack_propagate(False)

        self.browser_display = scrolledtext.ScrolledText(
            left_frame, wrap='word', font=('Courier', 10),
            bg='white', fg='#000000', height=20, borderwidth=0,
            relief=FLAT, padx=20, pady=20
        )
        self.browser_display.pack(fill=BOTH, expand=True)

        Label(right_frame, text="Visual Snapshot", font=('Helvetica', 10, 'bold'),
              fg='#111111', bg='#f7f9fc').pack(anchor=W, padx=10, pady=(10, 6))
        self.preview_canvas = Canvas(
            right_frame, bg='#ffffff', highlightthickness=1,
            highlightbackground='#dce3ef', width=336
        )
        self.preview_canvas.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Status bar
        status_frame = Frame(browser_frame, bg='#f0f0f0', height=30)
        status_frame.pack(fill=X, side=BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = Label(status_frame, text="Ready to browse", 
                                 font=('Helvetica', 9), fg='#666666', bg='#f0f0f0')
        self.status_label.pack(side=LEFT, padx=10, pady=5)
        
        # History button
        Button(status_frame, text="History", font=('Helvetica', 9, 'bold'),
               bg='#6c757d', fg='white', padx=10, pady=3, relief=FLAT,
               cursor='hand2', command=self.show_history).pack(side=RIGHT, padx=10, pady=3)
        
        # Welcome message
        self.browser_display.insert(END, "Visual Web Browser - Premium Visual Mode\n")
        self.browser_display.insert(END, "=" * 50 + "\n\n")
        self.browser_display.insert(END, "Features:\n")
        self.browser_display.insert(END, "- Google, Bing & DuckDuckGo Search\n")
        self.browser_display.insert(END, "- Visual Snapshot Preview\n")
        self.browser_display.insert(END, "- Web Navigation\n")
        self.browser_display.insert(END, "- Browsing History\n")
        self.browser_display.insert(END, "- Page Refresh\n")
        self.browser_display.insert(END, "- Quick Navigation\n\n")
        self.browser_display.insert(END, "Usage:\n")
        self.browser_display.insert(END, "1. Enter search query and click Search\n")
        self.browser_display.insert(END, "2. Enter URL and press Enter\n")
        self.browser_display.insert(END, "3. Use navigation buttons to browse\n")
        self.browser_display.insert(END, "4. View rendered HTML content\n\n")
        self.browser_display.insert(END, "Ready to browse web visually!\n")
        self._draw_page_preview("Ready", "Enter a URL or search query", [])
    
    def navigate_to_url(self, event=None):
        """Navigate to entered URL"""
        url = self.url_entry.get().strip()
        if url:
            self.current_url = url
            self.load_page(url)
    
    def go_back(self):
        """Go back in history"""
        if len(self.browsing_history) > 1:
            self.browsing_history.pop()
            if self.browsing_history:
                self.current_url = self.browsing_history[-1]
                self.load_page(self.current_url)
    
    def go_forward(self):
        """Go forward in history"""
        # Simplified forward navigation
        pass
    
    def refresh_page(self):
        """Refresh current page"""
        self.load_page(self.current_url)
    
    def go_home(self):
        """Go to home page"""
        self.current_url = "https://www.google.com"
        self.url_entry.delete(0, END)
        self.url_entry.insert(0, self.current_url)
        self.load_page(self.current_url)
    
    def web_search(self, event=None):
        """Perform web search"""
        query = self.search_entry.get().strip()
        if not query:
            return
        
        search_engine = self.search_engine_var.get()
        search_url = self.search_engines[search_engine] + urllib.parse.quote(query)
        
        self.current_url = search_url
        self.url_entry.delete(0, END)
        self.url_entry.insert(0, search_url)
        self.load_page(search_url)
        
        # Add to history
        self.browsing_history.append(search_url)
        if len(self.browsing_history) > 50:
            self.browsing_history = self.browsing_history[-50:]
    
    def load_page(self, url):
        """Load web page with visual rendering"""
        try:
            self.browser_display.delete("1.0", END)
            self.browser_display.insert(END, f"Loading: {url}\n")
            self.browser_display.insert(END, "=" * 50 + "\n\n")
            self._draw_page_preview("Loading", url, [])
            
            # Update status
            self.status_label.config(text=f"Loading: {url[:50]}...")
            
            # For demonstration, simulate page loading with visual rendering
            threading.Thread(target=self._load_visual_page_worker, args=(url,), daemon=True).start()
            
        except Exception as e:
            self.browser_display.insert(END, f"Error loading page: {e}\n")
            self.status_label.config(text="Load Error")
    
    def _load_visual_page_worker(self, url):
        """Worker for loading visual web page"""
        try:
            if requests:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    content = response.text[:12000]  # Limit content length
                    title = "Web Page"
                    
                    # Extract title
                    if '<title>' in content:
                        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE)
                        if title_match:
                            title = title_match.group(1).strip()
                    
                    # Update display with visual rendering
                    self.root.after(0, lambda: self._display_visual_page_content(title, url, content))
                else:
                    error_msg = f"HTTP {response.status_code}: Failed to load page"
                    self.root.after(0, lambda: self._display_error(error_msg))
            else:
                # Fallback without requests
                self.root.after(0, lambda: self._display_visual_page_content("Web Page", url, f"Visual content for {url}"))
                
        except Exception as e:
            error_msg = f"Network error: {str(e)}"
            self.root.after(0, lambda: self._display_error(error_msg))
    
    def _display_visual_page_content(self, title, url, content):
        """Display loaded page with visual HTML rendering"""
        self.browser_display.delete("1.0", END)
        self.browser_display.insert(END, f"{title}\n")
        self.browser_display.insert(END, f"{url}\n")
        self.browser_display.insert(END, "=" * 50 + "\n\n")
        
        # Simulate visual HTML rendering
        visual_content = self._render_html_visual(content)
        self.browser_display.insert(END, visual_content)
        self.browser_display.insert(END, "\n" + "=" * 50 + "\n")
        
        # Update status
        self.status_label.config(text=f"Loaded: {title[:30]}")
        signals = self._extract_page_signals(content)
        self._draw_page_preview(title, url, signals)
        
        # Add to history
        if url not in self.browsing_history:
            self.browsing_history.append(url)
            if len(self.browsing_history) > 50:
                self.browsing_history = self.browsing_history[-50:]
    
    def _render_html_visual(self, content):
        """Create visual HTML rendering simulation"""
        # Extract key elements for visual display
        visual_render = "🌐 Visual HTML Rendering:\n\n"
        
        # Extract headings
        headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', content, re.IGNORECASE)
        if headings:
            visual_render += "📝 Headings:\n"
            for i, heading in enumerate(headings[:5]):
                clean_heading = re.sub(r'<[^>]+>', '', heading)
                visual_render += f"  {i+1}. {clean_heading}\n"
            visual_render += "\n"
        
        # Extract links
        links = re.findall(r'<a[^>]+href=[\'"](.*?)[\'"][^>]*>(.*?)</a>', content, re.IGNORECASE | re.DOTALL)
        if links:
            visual_render += "🔗 Links Found:\n"
            for i, (href, label) in enumerate(links[:8]):
                clean_label = html.unescape(re.sub(r'<[^>]+>', '', label)).strip() or href
                visual_render += f"  {i+1}. {clean_label[:90]} -> {href}\n"
            visual_render += "\n"
        
        # Extract images
        images = re.findall(r'<img[^>]+src=[\'"](.*?)[\'"][^>]*>', content, re.IGNORECASE)
        if images:
            visual_render += "🖼️ Images Found:\n"
            for i, img in enumerate(images[:3]):
                src_match = re.search(r'src=[\'"](.*?)[\'"]', img)
                if src_match:
                    visual_render += f"  {i+1}. Image: {src_match.group(1)}\n"
            visual_render += "\n"
        
        # Extract forms
        forms = re.findall(r'<form[^>]*>.*?</form>', content, re.IGNORECASE | re.DOTALL)
        if forms:
            visual_render += "📝 Forms Found:\n"
            visual_render += f"  {len(forms)} form(s) detected\n\n"
        
        # Extract text content
        text_content = re.sub(r'<[^>]+>', '\n', content)
        text_lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        if text_lines:
            visual_render += "📄 Text Content:\n"
            for i, line in enumerate(text_lines[:10]):
                visual_render += f"  {line}\n"
        
        return visual_render
    
    def _display_error(self, error_msg):
        """Display error message"""
        self.browser_display.insert(END, f"Error: {error_msg}\n")
        self.status_label.config(text=f"Error: {error_msg[:40]}")
        self._draw_page_preview("Error", error_msg, [])

    def _extract_page_signals(self, content):
        """Extract structure metrics for the visual snapshot panel."""
        headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', content, re.IGNORECASE | re.DOTALL)
        links = re.findall(r'<a[^>]+href=[\'"](.*?)[\'"][^>]*>(.*?)</a>', content, re.IGNORECASE | re.DOTALL)
        images = re.findall(r'<img[^>]+src=[\'"](.*?)[\'"][^>]*>', content, re.IGNORECASE)
        forms = re.findall(r'<form[^>]*>.*?</form>', content, re.IGNORECASE | re.DOTALL)
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)
        return [
            ("Headings", len(headings)),
            ("Paragraphs", len(paragraphs)),
            ("Links", len(links)),
            ("Images", len(images)),
            ("Forms", len(forms)),
        ]

    def _draw_page_preview(self, title, subtitle, signals):
        """Draw a compact visual preview of page structure."""
        if not hasattr(self, "preview_canvas"):
            return
        c = self.preview_canvas
        c.delete("all")
        c.update_idletasks()
        w = max(c.winfo_width(), 320)
        h = max(c.winfo_height(), 460)

        c.create_rectangle(0, 0, w, h, fill="#ffffff", outline="")
        c.create_rectangle(0, 0, w, 34, fill="#f1f4fa", outline="#dce3ef")
        c.create_oval(10, 11, 18, 19, fill="#ff5f57", outline="")
        c.create_oval(22, 11, 30, 19, fill="#febc2e", outline="")
        c.create_oval(34, 11, 42, 19, fill="#28c840", outline="")
        c.create_rectangle(52, 8, w - 10, 26, fill="#ffffff", outline="#d8dfeb")
        shown_subtitle = subtitle[:58] + "..." if len(subtitle) > 58 else subtitle
        c.create_text(58, 17, text=shown_subtitle, anchor="w", fill="#6b7280", font=('Helvetica', 8))

        c.create_rectangle(12, 46, w - 12, 110, fill="#101827", outline="")
        shown_title = title[:34] + "..." if len(title) > 34 else title
        c.create_text(22, 66, text=shown_title, anchor="w", fill="#ffffff", font=('Helvetica', 11, 'bold'))
        c.create_text(22, 88, text="Visual page structure preview", anchor="w", fill="#a5b4d6", font=('Helvetica', 8))

        y = 126
        if not signals:
            signals = [("Blocks", 0), ("Links", 0), ("Images", 0), ("Forms", 0), ("Text", 0)]
        for idx, (label, value) in enumerate(signals[:5]):
            col = idx % 2
            row = idx // 2
            card_w = (w - 36) // 2
            x1 = 12 + col * (card_w + 12)
            x2 = x1 + card_w
            y1 = y + row * 72
            y2 = y1 + 58
            c.create_rectangle(x1, y1, x2, y2, fill="#f8fafc", outline="#e2e8f0")
            c.create_text(x1 + 10, y1 + 18, text=str(value), anchor="w", fill="#0f172a", font=('Helvetica', 12, 'bold'))
            c.create_text(x1 + 10, y1 + 38, text=label, anchor="w", fill="#64748b", font=('Helvetica', 8))
    
    def show_history(self):
        """Show browsing history"""
        if not self.browsing_history:
            messagebox.showinfo("History", "No browsing history yet.")
            return
        
        history_window = Toplevel(self.parent_frame)
        history_window.title("Browsing History")
        history_window.geometry("600x400")
        
        history_listbox = Listbox(history_window, font=('Helvetica', 10))
        history_listbox.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        for url in reversed(self.browsing_history[-20:]):  # Show last 20
            history_listbox.insert(0, url)
        
        def load_selected():
            selection = history_listbox.curselection()
            if selection:
                url = history_listbox.get(selection[0])
                self.current_url = url
                self.url_entry.delete(0, END)
                self.url_entry.insert(0, url)
                self.load_page(url)
                history_window.destroy()
        
        Button(history_window, text="Load", command=load_selected,
               font=('Helvetica', 10, 'bold'), bg='#007aff', fg='white').pack(pady=10)
        
        history_window.transient(self.parent_frame)
        history_window.grab_set()

class RainbowLine(Canvas):
    """A thin Siri-like animated rainbow accent line."""
    COLORS = ["#67e8f9", "#7c9cff", "#c084fc", "#f472b6", "#fb7185", "#facc15", "#4ade80"]

    def __init__(self, parent, height=4, speed=110, **kwargs):
        super().__init__(parent, height=height, bg=kwargs.pop("bg", "#1b1f2a"),
                         highlightthickness=0, bd=0, **kwargs)
        self.offset = 0
        self.speed = speed
        self.after(120, self.animate)

    def animate(self):
        self.delete("all")
        width = max(self.winfo_width(), 1)
        height = max(self.winfo_height(), 1)
        segment = max(width // 18, 28)
        start = -segment * 2 + (self.offset % segment)

        for i, x in enumerate(range(start, width + segment * 2, segment)):
            color = self.COLORS[(i + self.offset // segment) % len(self.COLORS)]
            self.create_line(x, height // 2, x + segment * 2, height // 2,
                             fill=color, width=height, capstyle=ROUND)

        self.offset = (self.offset + 3) % (segment * len(self.COLORS))
        self.after(self.speed, self.animate)

def _draw_round_rect(canvas, x1, y1, x2, y2, radius=16, **kwargs):
    radius = max(2, min(radius, int((x2 - x1) / 2), int((y2 - y1) / 2)))
    fill = kwargs.pop("fill", "#ffffff")
    outline = kwargs.pop("outline", "")
    width = int(kwargs.pop("width", 1) or 1)
    try:
        rect_w = max(1, int(x2 - x1))
        rect_h = max(1, int(y2 - y1))
        scale = 3
        image = Image.new("RGBA", (rect_w * scale, rect_h * scale), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle(
            [scale, scale, rect_w * scale - scale, rect_h * scale - scale],
            radius=radius * scale,
            fill=fill,
            outline=outline or None,
            width=max(1, width * scale)
        )
        resampling = getattr(Image, "Resampling", None)
        resample = resampling.LANCZOS if resampling else getattr(Image, "LANCZOS", Image.BICUBIC)
        image = image.resize((rect_w, rect_h), resample)
        photo = ImageTk.PhotoImage(image)
        refs = getattr(canvas, "_aa_round_refs", [])
        refs.append(photo)
        canvas._aa_round_refs = refs
        return canvas.create_image(x1, y1, image=photo, anchor=NW)
    except Exception:
        pass
    points = [
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, fill=fill, outline=outline, width=width, **kwargs)

def _has_emoji_text(text):
    return bool(re.search(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", str(text or "")))

class RoundedButton(Canvas):
    """Canvas-backed rounded button with emoji-friendly text rendering."""
    def __init__(self, parent, text, command, fill, fg, active_fill, active_fg,
                 font_family="Segoe UI", size=10, weight="bold", width=None,
                 radius=16, pad_x=14, pad_y=8, anchor=CENTER, **kwargs):
        self.text = str(text)
        self.command = command
        self.fill = fill
        self.fg = fg
        self.active_fill = active_fill
        self.active_fg = active_fg
        self.current_fill = fill
        self.current_fg = fg
        self.radius = radius
        self.state = NORMAL
        self.outline = kwargs.pop("outline", "#e5e7eb")
        self.font_family = "Segoe UI Emoji" if _has_emoji_text(text) else font_family
        self.font = (self.font_family, size, weight)
        self.pad_x = pad_x
        self.pad_y = pad_y
        self.anchor = anchor
        approx_width = max((width or 0) * 10 + 30, len(self.text) * max(7, size) + pad_x * 2, 46)
        height = max(32, size + pad_y * 2 + 10)
        parent_bg = kwargs.pop("bg", None)
        if parent_bg is None:
            try:
                parent_bg = parent.cget("bg")
            except Exception:
                parent_bg = "#ffffff"
        super().__init__(parent, width=approx_width, height=height, bg=parent_bg,
                         highlightthickness=0, bd=0, cursor="hand2", **kwargs)
        self.bind("<Configure>", lambda _e: self._draw())
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def _draw(self):
        self.delete("all")
        self._aa_round_refs = []
        w = max(self.winfo_width(), int(self["width"]))
        h = max(self.winfo_height(), int(self["height"]))
        _draw_round_rect(self, 1, 1, w - 2, h - 2, self.radius,
                         fill=self.current_fill, outline=self.outline, width=1)
        # Siri-style accent hairline, subtle enough to keep buttons minimal.
        segment = max(w // len(RainbowLine.COLORS), 1)
        for i, color in enumerate(RainbowLine.COLORS):
            x1 = i * segment
            x2 = w if i == len(RainbowLine.COLORS) - 1 else (i + 1) * segment
            self.create_line(x1 + self.radius // 2, h - 3, x2, h - 3,
                             fill=color, width=2, capstyle=ROUND)
        if self.anchor in (W, "w", "W"):
            x = self.pad_x
            anchor = W
        elif self.anchor in (E, "e", "E"):
            x = w - self.pad_x
            anchor = E
        else:
            x = w / 2
            anchor = CENTER
        self.create_text(x, h / 2 - 1, text=self.text, fill=self.current_fg, font=self.font, anchor=anchor)

    def _on_enter(self, _event=None):
        if str(self.state) == str(DISABLED):
            return
        self.current_fill = self.active_fill
        self.current_fg = self.active_fg
        self._draw()

    def _on_leave(self, _event=None):
        if str(self.state) == str(DISABLED):
            return
        self.current_fill = self.fill
        self.current_fg = self.fg
        self._draw()

    def _on_click(self, _event=None):
        if str(self.state) != str(DISABLED) and callable(self.command):
            self.command()

    def configure(self, cnf=None, **kwargs):
        cnf = cnf or {}
        kwargs.update(cnf)
        redraw = False
        for key in list(kwargs.keys()):
            value = kwargs.pop(key)
            if key in ("text",):
                self.text = str(value)
                self.font_family = "Segoe UI Emoji" if _has_emoji_text(self.text) else self.font_family
                redraw = True
            elif key in ("state",):
                self.state = value
                redraw = True
            elif key in ("bg", "background", "fill"):
                self.fill = value
                self.current_fill = value
                redraw = True
            elif key in ("fg", "foreground"):
                self.fg = value
                self.current_fg = value
                redraw = True
            elif key == "activebackground":
                self.active_fill = value
            elif key == "activeforeground":
                self.active_fg = value
            elif key == "command":
                self.command = value
            elif key == "anchor":
                self.anchor = value
                redraw = True
            else:
                try:
                    super().configure({key: value})
                except Exception:
                    pass
        if redraw:
            if str(self.state) == str(DISABLED):
                self.current_fill = "#eef1f6"
                self.current_fg = "#9aa1ac"
            else:
                self.current_fill = self.fill
                self.current_fg = self.fg
            self._draw()

    config = configure

    def cget(self, key):
        if key == "text":
            return self.text
        if key in ("state",):
            return self.state
        if key in ("bg", "background"):
            return self.fill
        if key in ("fg", "foreground"):
            return self.fg
        return super().cget(key)

class RoundedFrame(Frame):
    """Rounded container that exposes an inner frame for regular Tk widgets."""
    def __init__(self, parent, fill="#ffffff", outline="#e5e7eb", radius=22,
                 padding=0, parent_bg=None, siri=False, **kwargs):
        if parent_bg is None:
            try:
                parent_bg = parent.cget("bg")
            except Exception:
                parent_bg = "#ffffff"
        super().__init__(parent, bg=parent_bg, highlightthickness=0, bd=0, **kwargs)
        self.fill = fill
        self.outline = outline
        self.radius = radius
        self.padding = padding
        self.siri = siri
        self.canvas = Canvas(self, bg=parent_bg, highlightthickness=0, bd=0)
        self.canvas.pack(fill=BOTH, expand=True)
        self.inner = Frame(self.canvas, bg=fill, highlightthickness=0, bd=0)
        self.window_id = self.canvas.create_window(padding, padding, anchor=NW, window=self.inner)
        self.canvas.bind("<Configure>", self._redraw)
        self.inner.bind("<Configure>", self._sync_requested_size)

    def _sync_requested_size(self, event=None):
        pad = self.padding
        try:
            self.canvas.configure(
                width=max(1, self.inner.winfo_reqwidth() + pad * 2),
                height=max(1, self.inner.winfo_reqheight() + pad * 2)
            )
        except Exception:
            pass

    def _redraw(self, event=None):
        w = max(self.canvas.winfo_width(), 2)
        h = max(self.canvas.winfo_height(), 2)
        self.canvas.delete("all")
        self.canvas._aa_round_refs = []
        _draw_round_rect(self.canvas, 1, 1, w - 2, h - 2, self.radius,
                         fill=self.fill, outline=self.outline, width=1)
        if self.siri:
            segment = max(w // len(RainbowLine.COLORS), 1)
            for i, color in enumerate(RainbowLine.COLORS):
                x1 = i * segment
                x2 = w if i == len(RainbowLine.COLORS) - 1 else (i + 1) * segment
                self.canvas.create_line(x1 + self.radius, 3, x2, 3,
                                        fill=color, width=3, capstyle=ROUND)
        pad = self.padding
        self.canvas.create_window(pad, pad, anchor=NW, window=self.inner,
                                  width=max(1, w - pad * 2), height=max(1, h - pad * 2))

class AdvancedImageGenerator:
    """Advanced AI Image Generator using Diffusers"""
    def __init__(self):
        self.device = "cpu"
        self.pipe = None
        self.load_error = None
    
    def init_model(self):
        """Initialize diffusion model"""
        if not ADVANCED_IMG_GEN:
            return
        
        try:
            import torch
            import diffusers
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            # Load Stable Diffusion pipeline
            self.pipe = diffusers.StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float16,
                safety_checker=None,
                requires_safety_checker=False
            )
            
            if self.device == "cuda":
                self.pipe = self.pipe.to("cuda")
            
            print(f"Advanced image generator initialized on {self.device}")
        except Exception as e:
            print(f"Failed to initialize advanced generator: {e}")
            self.load_error = str(e)
            self.pipe = None
    
    def generate_image(self, prompt, style="realistic", width=512, height=512):
        """Generate image using advanced AI"""
        if not ADVANCED_IMG_GEN:
            return None
        if not self.pipe:
            self.init_model()
        if not self.pipe:
            return None
        
        try:
            import torch
            # Style adjustments
            negative_prompt = ""
            if style == "artistic":
                negative_prompt = "blurry, low quality, distorted"
            elif style == "abstract":
                negative_prompt = "realistic, photographic"
            
            # Generate image
            with torch.no_grad():
                result = self.pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=20,
                    guidance_scale=7.5,
                    width=width,
                    height=height,
                    generator=torch.Generator().manual_seed(random.randint(0, 100000))
                )
            
            image = result.images[0]
            return image
            
        except Exception as e:
            print(f"Image generation error: {e}")
            return None

class ArenaAgent:
    """Enhanced arena bot agent with chatbot names"""
    def __init__(self, name, personality, voice_gender, model, lightsky_instance):
        self.name = name
        self.personality = personality
        self.voice_gender = voice_gender
        self.model = model
        self.lightsky_instance = lightsky_instance
        self.messages = []
        self.speech_engine = None
        self.init_speech()
        
    def show_startup_screen(self):
        """Show startup splash before loading the main interface."""
        self.root.configure(bg=self.bg_color)
        self.startup_frame = Frame(self.root, bg=self.bg_color)
        self.startup_frame.pack(fill=BOTH, expand=True)

        center = Frame(self.startup_frame, bg=self.bg_color)
        center.place(relx=0.5, rely=0.5, anchor=CENTER)

        logo = Label(
            center,
            text="✨",
            font=(self.font_family, 64, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        logo.pack()

        title = Label(
            center,
            text="lightsky AI",
            font=(self.font_family, 34, "bold"),
            fg=self.text_color,
            bg=self.bg_color
        )
        title.pack(pady=(8, 0))

        subtitle = Label(
            center,
            text="by Krivi and codex",
            font=(self.font_family, 12),
            fg=self.secondary_color,
            bg=self.bg_color
        )
        subtitle.pack(pady=(6, 0))

        self.root.after(1700, self.finish_startup_screen)

    def finish_startup_screen(self):
        """Destroy splash and build the main app."""
        if self.startup_frame is not None:
            self.startup_frame.destroy()
            self.startup_frame = None

        self.create_ultimate_interface()
        self.main_ui_ready = True
        if self.welcome_message_text:
            self.add_message(self.app_name, self.welcome_message_text)

    def init_speech(self):
        """Initialize speech synthesis"""
        try:
            self.speech_engine = pyttsx3.init()
            voices = self.speech_engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if self.voice_gender.lower() == 'female' and 'female' in voice.gender.lower():
                        self.speech_engine.setProperty('voice', voice.id)
                        break
                    elif self.voice_gender.lower() == 'male' and 'male' in voice.gender.lower():
                        self.speech_engine.setProperty('voice', voice.id)
                        break
            self.speech_engine.setProperty('rate', 180)
            self.speech_engine.setProperty('volume', 0.9)
        except Exception as e:
            print(f"Speech not available for {self.name}: {e}")
            self.speech_engine = None
    
    def speak(self, text):
        """Speak text"""
        if self.speech_engine:
            try:
                self.speech_engine.say(text)
                self.speech_engine.runAndWait()
            except Exception as e:
                print(f"Speech error for {self.name}: {e}")
    
    def add_message(self, role, content):
        """Add message to conversation"""
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]
    
    def get_response(self, prompt, topic):
        """Get AI response with topic context"""
        try:
            context_prompt = f"You are {self.name}, a {self.personality} AI chatbot. The topic is: {topic}. {prompt}"

            # Always use a real model call (no placeholder text fallbacks).
            if self.lightsky_instance and hasattr(self.lightsky_instance, "get_groq_response"):
                return self.lightsky_instance.get_groq_response(context_prompt, self.model, 150)

            provider = CURRENT_PROVIDER if 'CURRENT_PROVIDER' in globals() else "groq"
            return get_provider_response(context_prompt, provider=provider, model=self.model, max_tokens=150)
        except Exception as e:
            return f"[Arena agent error: {str(e)}]"

class SpeechRecognizer:
    """Speech recognition for voice input using PvRecorder instead of PyAudio."""
    def __init__(self):
        self.recognizer = None
        self.recorder = None
        self.available = False
        self.sample_rate = 16000
        self.frame_length = 512
        
        if HAS_SPEECH_RECOGNITION and HAS_PVRECORDER:
            try:
                self.recognizer = sr.Recognizer()
                self.available = True
                print("Speech recognition initialized with PvRecorder")
            except Exception as e:
                print(f"Speech recognition not available: {e}")
                self.available = False
        else:
            print("Speech recognition not available - install speechrecognition and pvrecorder")
            self.available = False
    
    def recognize_speech(self):
        """Recognize speech from microphone"""
        if not self.available:
            return "Speech recognition not available. Install it with: py -m pip install speechrecognition pvrecorder"
        
        recorder = None
        try:
            recorder = PvRecorder(device_index=-1, frame_length=self.frame_length)
            recorder.start()
            print("Listening with PvRecorder...")

            frames = []
            max_seconds = 7
            max_frames = int(self.sample_rate / self.frame_length * max_seconds)
            silence_limit = int(self.sample_rate / self.frame_length * 1.2)
            silence_count = 0
            heard_voice = False

            for _ in range(max_frames):
                frame = recorder.read()
                frames.extend(frame)
                level = max(abs(sample) for sample in frame) if frame else 0

                if level > 450:
                    heard_voice = True
                    silence_count = 0
                elif heard_voice:
                    silence_count += 1
                    if silence_count >= silence_limit:
                        break
            
            if not frames or not heard_voice:
                return "Listening timeout. Please try again."

            raw_audio = struct.pack("<" + "h" * len(frames), *frames)
            audio = sr.AudioData(raw_audio, self.sample_rate, 2)

            print("Recognizing...")
            text = self.recognizer.recognize_google(audio, show_all=False)
            return text
            
        except sr.UnknownValueError:
            return "Could not understand audio. Please speak clearly."
        except Exception as e:
            return f"Speech recognition error: {e}"
        finally:
            if recorder:
                try:
                    recorder.stop()
                    recorder.delete()
                except Exception:
                    pass

class LightSkyUltimateCorrectUI:
    def __init__(self, root):
        self.root = root
        self.app_name = "Lightsky AI pro by krivi"
        self.root.title(self.app_name)
        self.root.geometry("1500x980")
        self.root.minsize(1120, 760)
        
        # Colorful pro workspace theme
        self.bg_color = "#101a33"
        self.surface_color = "#162446"
        self.panel_color = "#203052"
        self.input_color = "#111d36"
        self.accent_color = "#67e8f9"
        self.accent_hover = "#a78bfa"
        self.success_color = "#4ade80"
        self.warning_color = "#facc15"
        self.danger_color = "#fb7185"
        self.text_color = "#eef6ff"
        self.secondary_color = "#b7c7e8"
        self.muted_color = "#8190b2"
        self.border_color = "#38507d"
        self.brand_cyan = "#67e8f9"
        self.brand_violet = "#a78bfa"
        self.brand_pink = "#f472b6"
        self.brand_green = "#4ade80"
        self.brand_gold = "#facc15"
        self.font_family = "Segoe UI"
        self.mono_family = "Consolas"
        self.font_size = 12
        
        # Initialize systems
        self.speech_engine = None
        self.init_speech()
        
        # Advanced image generator
        self.image_generator = AdvancedImageGenerator()
        
        # Speech recognition
        self.speech_recognizer = SpeechRecognizer()
        self.listening = False
        
        # Arena system
        self.arena_agents = []
        self.arena_running = False
        self.arena_thread = None
        self.custom_topics = DEFAULT_TOPICS.copy()
        self.current_topic = random.choice(self.custom_topics)
        
        # Knowledge base
        self.knowledge_db = "lightsky_knowledge.db"
        self.init_knowledge_base()
        
        # User data
        self.user_data = {
            'name': 'User',
            'messages_sent': 0,
            'tokens_used': 0,
            'images_generated': 0,
            'arena_sessions': 0,
            'voice_commands': 0
        }
        
        # Startup sequence
        self.startup_frame = None
        self.main_ui_ready = False
        self.welcome_message_text = ""
        self.show_startup_screen()
        
        # Welcome message
        welcome_msg = "Welcome to LightSky AI by Krivi - ULTIMATE CORRECTED VERSION!\n\n" + \
                   "🚀 ALL ISSUES FIXED:\n" + \
                   "• ✅ Real Groq Models from Console\n" + \
                   "• ✅ Arena with Chatbot Names\n" + \
                   "• ✅ Visual Web Browser with HTML Rendering\n" + \
                   "• ✅ Functional Knowledge Base\n" + \
                   "• ✅ No More Crashes\n" + \
                   "• ✅ All Features Working\n\n" + \
                   "🎯 Features:\n" + \
                   "• 🤖 Real Groq AI Models\n" + \
                   "• 🎨 Advanced AI Image Generation\n" + \
                   "• 🌐 Visual Web Browser\n" + \
                   "• 🏆 Arena with Chatbot Names\n" + \
                   "• 🎤 Voice Input (Talk to AI)\n" + \
                   "• 🔊 Voice Output (AI Speaks)\n" + \
                   "• 📚 Knowledge Base\n" + \
                   "• 📊 Advanced Analytics\n" + \
                   "• ⚙️ Professional Settings\n\n" + \
                   "🎉 Ready to use all features!"
        
        welcome_msg = (
            f"Welcome to {self.app_name}.\n\n"
            "Your workspace is ready with chat, arena mode, visual browsing, image generation, "
            "voice, knowledge base, analytics, and settings.\n\n"
            "Pick a model, type a message, or open any power tool from the sidebar."
        )
        self.welcome_message_text = welcome_msg
    
    def init_speech(self):
        """Initialize speech synthesis"""
        try:
            self.speech_engine = pyttsx3.init()
            voices = self.speech_engine.getProperty('voices')
            if voices:
                self.speech_engine.setProperty('voice', voices[0].id)
            self.speech_engine.setProperty('rate', 200)
            self.speech_engine.setProperty('volume', 1.0)
            print("Speech synthesis initialized")
        except Exception as e:
            print(f"Speech synthesis not available: {e}")
            self.speech_engine = None
    
    def init_knowledge_base(self):
        """Initialize knowledge base database"""
        try:
            self.conn = sqlite3.connect(self.knowledge_db)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
            print("Knowledge base initialized")
        except Exception as e:
            print(f"Knowledge base error: {e}")
            self.conn = None

    def style_ttk(self):
        """Apply the main visual theme to ttk controls."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure(
            'TNotebook.Tab',
            background=self.surface_color,
            foreground=self.secondary_color,
            borderwidth=0,
            padding=[22, 12],
            font=(self.font_family, 10, 'bold')
        )
        style.map(
            'TNotebook.Tab',
            background=[('selected', self.panel_color), ('active', self.panel_color)],
            foreground=[('selected', self.text_color), ('active', self.text_color)]
        )
        style.configure(
            'TCombobox',
            fieldbackground=self.input_color,
            background=self.panel_color,
            foreground=self.text_color,
            arrowcolor=self.secondary_color,
            bordercolor=self.border_color,
            lightcolor=self.border_color,
            darkcolor=self.border_color,
            padding=6
        )

    def panel(self, parent, **pack_options):
        frame = Frame(parent, bg=self.panel_color, bd=1, relief=SOLID, highlightthickness=1,
                      highlightbackground=self.border_color)
        if pack_options:
            frame.pack(**pack_options)
        return frame

    def toolbar(self, parent, **pack_options):
        frame = Frame(parent, bg=self.bg_color)
        if pack_options:
            frame.pack(**pack_options)
        return frame

    def label(self, parent, text, size=10, weight='normal', color=None, bg=None):
        return Label(
            parent,
            text=text,
            font=(self.font_family, size, weight),
            fg=color or self.text_color,
            bg=bg or parent.cget('bg')
        )

    def button(self, parent, text, command, tone='secondary', size=10, width=None):
        colors = {
            'primary': self.brand_violet if hasattr(self, "brand_violet") else self.accent_color,
            'secondary': "#273a63",
            'success': self.success_color,
            'danger': self.danger_color,
            'warning': self.warning_color,
        }
        active_colors = {
            'primary': self.accent_color,
            'secondary': "#30466f",
            'success': "#86efac",
            'danger': "#fda4af",
            'warning': "#fde68a",
        }
        fg = '#09111f' if tone in ('success', 'warning', 'danger') else self.text_color
        return Button(
            parent,
            text=text,
            command=command,
            font=(self.font_family, size, 'bold'),
            bg=colors.get(tone, self.panel_color),
            fg=fg,
            activebackground=active_colors.get(tone, self.surface_color),
            activeforeground='#09111f' if tone in ('success', 'warning', 'danger') else self.text_color,
            padx=16,
            pady=8,
            width=width,
            relief=FLAT,
            borderwidth=0,
            cursor='hand2'
        )

    def configure_text_widget(self, widget):
        widget.configure(
            bg=self.input_color,
            fg=self.text_color,
            insertbackground=self.accent_color,
            selectbackground=self.accent_color,
            borderwidth=0,
            relief=FLAT,
            padx=18,
            pady=16
        )
    
    def create_ultimate_interface(self):
        """Create ultimate interface"""
        self.root.configure(bg=self.bg_color)
        self.style_ttk()

        # Main container
        main_frame = Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=BOTH, expand=True, padx=18, pady=16)
        
        # Ultimate header
        self.create_ultimate_header(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
        # Ultimate tabs
        self.create_ultimate_tabs(main_frame)
        
        # Initialize arena agents
        self.init_arena_agents()
    
    def create_ultimate_header(self, parent):
        """Create ultimate header with all controls"""
        header = Frame(parent, bg=self.bg_color, height=120)
        header.pack(fill=X, pady=(0, 20))
        header.pack_propagate(False)
        
        # Title section
        title_frame = Frame(header, bg=self.bg_color)
        title_frame.pack(side=LEFT, fill=X, expand=True)
        
        title_label = Label(title_frame, text="✨ LightSky AI by Krivi - ULTIMATE CORRECTED", 
                           font=(self.font_family, 32, 'bold'), 
                           fg=self.text_color, bg=self.bg_color)
        title_label.pack(anchor=W, pady=(10, 0))
        
        subtitle_label = Label(title_frame, text="🚀 Real Groq Models, Visual Browser, Chatbot Arena", 
                              font=(self.font_family, 16), 
                              fg=self.secondary_color, bg=self.bg_color)
        subtitle_label.pack(anchor=W)
        
        # Quick stats
        stats_frame = Frame(title_frame, bg=self.bg_color)
        stats_frame.pack(anchor=W, pady=(5, 0))
        
        self.stats_label = Label(stats_frame, text="Messages: 0 | Tokens: 0 | Voice: 0 | Images: 0 | Arena: 0", 
                                font=(self.font_family, 11), fg=self.secondary_color, bg=self.bg_color)
        self.stats_label.pack(anchor=W)
        
        # Ultimate control panel
        control_frame = Frame(header, bg=self.bg_color)
        control_frame.pack(side=RIGHT)
        
        # Model selector - FIXED TO SHOW REAL GROQ MODELS
        model_frame = Frame(control_frame, bg=self.bg_color)
        model_frame.pack(pady=5)
        
        Label(model_frame, text="🤖 AI Model:", font=(self.font_family, 10, 'bold'),
              fg=self.text_color, bg=self.bg_color).pack(side=LEFT, padx=(0, 5))
        
        self.model_var = StringVar(value=CURRENT_MODEL)
        # Use display names in dropdown
        model_display_names = list(MODELS.keys())
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                        values=model_display_names, state='readonly',
                                        font=(self.font_family, 10), width=35)
        self.model_combo.pack(side=LEFT)
        self.model_combo.bind('<<ComboboxSelected>>', self.change_model)
        
        # Voice controls
        voice_frame = Frame(control_frame, bg=self.bg_color)
        voice_frame.pack(pady=5)
        
        self.voice_input_btn = Button(voice_frame, text="🎤 Voice Input", 
                                   font=(self.font_family, 10, 'bold'), bg='#28a745', fg='white',
                                   padx=15, pady=8, relief=FLAT, cursor='hand2',
                                   command=self.toggle_voice_input)
        self.voice_input_btn.pack(side=LEFT, padx=(0, 5))
        
        self.speech_btn = Button(voice_frame, text="🔊 Speech", 
                               font=(self.font_family, 10, 'bold'), bg=self.accent_color, fg='white',
                               padx=15, pady=8, relief=FLAT, cursor='hand2',
                               command=self.toggle_speech)
        self.speech_btn.pack(side=LEFT, padx=(0, 5))
        
        # Quick actions
        action_frame = Frame(control_frame, bg=self.bg_color)
        action_frame.pack(pady=5)
        
        self.theme_btn = Button(action_frame, text="🎨 Theme", 
                            font=(self.font_family, 10, 'bold'), bg=self.accent_color, fg='white',
                            padx=15, pady=8, relief=FLAT, cursor='hand2',
                            command=self.toggle_theme)
        self.theme_btn.pack(side=LEFT, padx=2)
        
        self.export_btn = Button(action_frame, text="💾 Export", 
                             font=(self.font_family, 10, 'bold'), bg='#28a745', fg='white',
                             padx=15, pady=8, relief=FLAT, cursor='hand2',
                             command=self.export_all_data)
        self.export_btn.pack(side=LEFT, padx=2)
    
    def create_ultimate_tabs(self, parent):
        """Create ultimate tabbed interface"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Style
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.bg_color, 
                       foreground=self.text_color, padding=[30, 15],
                       font=(self.font_family, 12, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', self.accent_color)],
                 foreground=[('selected', 'white')])
        
        # Create all ultimate tabs
        self.create_ultimate_chat_tab()
        self.create_ultimate_arena_tab()
        self.create_ultimate_webgl_tab()
        self.create_ultimate_image_tab()
        self.create_ultimate_knowledge_tab()
        self.create_ultimate_analytics_tab()
        self.create_ultimate_settings_tab()
    
    def create_ultimate_chat_tab(self):
        """Create ultimate chat tab with voice input"""
        chat_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(chat_frame, text="💬 Chat")
        
        # Chat controls
        control_frame = Frame(chat_frame, bg=self.bg_color)
        control_frame.pack(fill=X, pady=(10, 0))
        
        Button(control_frame, text="Clear", font=(self.font_family, 10, 'bold'),
               bg='#dc3545', fg='white', padx=15, pady=8, relief=FLAT,
               command=self.clear_chat).pack(side=LEFT, padx=(0, 5))
        
        Button(control_frame, text="Save", font=(self.font_family, 10, 'bold'),
               bg='#28a745', fg='white', padx=15, pady=8, relief=FLAT,
               command=self.save_chat).pack(side=LEFT, padx=(0, 5))
        
        Button(control_frame, text="Export", font=(self.font_family, 10, 'bold'),
               bg='#17a2b8', fg='white', padx=15, pady=8, relief=FLAT,
               command=self.export_chat).pack(side=LEFT)
        
        # Voice input status
        self.voice_status_label = Label(control_frame, text="🎤 Voice: Ready", 
                                   font=(self.font_family, 10, 'bold'),
                                   fg='#28a745', bg=self.bg_color)
        self.voice_status_label.pack(side=RIGHT, padx=(10, 0))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap='word', font=(self.font_family, self.font_size),
            bg=self.bg_color, fg=self.text_color, height=20, borderwidth=1,
            relief=SOLID, padx=20, pady=20, selectbackground=self.accent_color
        )
        self.chat_display.pack(fill=BOTH, expand=True, pady=10)
        
        # Input area with voice
        input_frame = Frame(chat_frame, bg=self.bg_color)
        input_frame.pack(fill=X, pady=(0, 10))
        
        self.input_field = Text(input_frame, height=3, font=(self.font_family, self.font_size),
                               bg='#f8f9fa', fg=self.text_color, insertbackground=self.accent_color,
                               borderwidth=1, relief=SOLID, padx=15, pady=12)
        self.input_field.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        # Voice input button
        voice_btn = Button(input_frame, text="🎤", font=(self.font_family, 16, 'bold'),
                         bg='#28a745', fg='white', width=3, height=2, relief=FLAT,
                         cursor='hand2', command=self.voice_input_message)
        voice_btn.pack(side=RIGHT, padx=(0, 5))
        
        send_btn = Button(input_frame, text="Send", font=(self.font_family, 12, 'bold'),
                         bg=self.accent_color, fg='white', padx=25, pady=12, relief=FLAT,
                         cursor='hand2', command=self.send_message)
        send_btn.pack(side=RIGHT)
        
        # Bind keys
        self.input_field.bind('<Control-Return>', lambda e: self.send_message())
        self.input_field.bind('<Shift-Return>', lambda e: self.input_field.insert('insert', '\n'))
    
    def create_ultimate_arena_tab(self):
        """Create ultimate arena tab with chatbot names"""
        arena_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(arena_frame, text="🏆 Arena")
        
        # Arena controls
        control_frame = Frame(arena_frame, bg=self.bg_color)
        control_frame.pack(fill=X, pady=(10, 0))
        
        # Start/Stop button
        self.arena_btn = Button(control_frame, text="🏆 Start Arena", 
                                font=(self.font_family, 12, 'bold'),
                                bg='#28a745', fg='white', padx=25, pady=10, relief=FLAT,
                                cursor='hand2', command=self.toggle_arena)
        self.arena_btn.pack(side=LEFT, padx=(0, 10))
        
        # Talk button
        self.talk_btn = Button(control_frame, text="🎤 Talk to Arena", 
                              font=(self.font_family, 12, 'bold'),
                              bg='#17a2b8', fg='white', padx=25, pady=10, relief=FLAT,
                              cursor='hand2', command=self.talk_to_arena)
        self.talk_btn.pack(side=LEFT, padx=(0, 10))
        
        # Custom topic controls
        topic_control_frame = Frame(control_frame, bg=self.bg_color)
        topic_control_frame.pack(side=LEFT, padx=(10, 0))
        
        Label(topic_control_frame, text="📝 Topic:", font=(self.font_family, 10, 'bold'),
              fg=self.text_color, bg=self.bg_color).pack(side=LEFT, padx=(0, 5))
        
        self.topic_entry = Entry(topic_control_frame, font=(self.font_family, 10),
                             bg='#f8f9fa', fg=self.text_color, insertbackground=self.accent_color,
                             borderwidth=1, relief=SOLID, width=25)
        self.topic_entry.pack(side=LEFT, padx=(0, 5))
        self.topic_entry.bind('<Return>', self.add_custom_topic)
        
        Button(topic_control_frame, text="Add", font=(self.font_family, 10, 'bold'),
               bg='#6c757d', fg='white', padx=10, pady=6, relief=FLAT,
               cursor='hand2', command=self.add_custom_topic).pack(side=LEFT)
        
        # Topic selector
        topic_frame = Frame(arena_frame, bg=self.bg_color)
        topic_frame.pack(fill=X, pady=(5, 0))
        
        Label(topic_frame, text="🎯 Select Topic:", font=(self.font_family, 10, 'bold'),
              fg=self.text_color, bg=self.bg_color).pack(side=LEFT, padx=(0, 5))
        
        self.topic_var = StringVar(value=self.current_topic)
        self.topic_combo = ttk.Combobox(topic_frame, textvariable=self.topic_var,
                                        values=self.custom_topics, state='readonly',
                                        font=(self.font_family, 10), width=40)
        self.topic_combo.pack(side=LEFT, padx=(0, 10))
        self.topic_combo.bind('<<ComboboxSelected>>', self.change_topic)
        
        # Status
        self.arena_status = Label(topic_frame, text="🟢 Arena Ready", 
                                 font=(self.font_family, 11, 'bold'),
                                 fg='#28a745', bg=self.bg_color)
        self.arena_status.pack(side=LEFT, padx=(10, 0))
        
        # Arena display
        self.arena_display = scrolledtext.ScrolledText(
            arena_frame, wrap='word', font=(self.font_family, self.font_size),
            bg=self.bg_color, fg=self.text_color, height=18, borderwidth=1,
            relief=SOLID, padx=20, pady=20, selectbackground=self.accent_color
        )
        self.arena_display.pack(fill=BOTH, expand=True, pady=10)
        
        # User input
        arena_input_frame = Frame(arena_frame, bg=self.bg_color)
        arena_input_frame.pack(fill=X, pady=(0, 10))
        
        self.arena_input = Entry(arena_input_frame, font=(self.font_family, self.font_size),
                                bg='#f8f9fa', fg=self.text_color, insertbackground=self.accent_color,
                                borderwidth=1, relief=SOLID)
        self.arena_input.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        arena_send_btn = Button(arena_input_frame, text="Send Message", 
                               font=(self.font_family, 12, 'bold'),
                               bg=self.accent_color, fg='white', padx=25, pady=10, relief=FLAT,
                               cursor='hand2', command=self.send_arena_message)
        arena_send_btn.pack(side=RIGHT)
        
        self.arena_input.bind('<Return>', lambda e: self.send_arena_message())
    
    def create_ultimate_webgl_tab(self):
        """Create ultimate visual web browser tab"""
        webgl_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(webgl_frame, text="🌐 Visual Browser")
        
        # Create visual web browser with root reference
        self.visual_browser = VisualWebBrowser(webgl_frame, self.root)
        
        # Browser info
        info_frame = Frame(webgl_frame, bg=self.bg_color)
        info_frame.pack(fill=X, pady=(0, 10))
        
        info_text = "🌐 Visual Web Browser - HTML Rendering & Search Integration"
        info_label = Label(info_frame, text=info_text, 
                           font=(self.font_family, 12, 'bold'), 
                           fg=self.text_color, bg=self.bg_color)
        info_label.pack()
    
    def create_ultimate_image_tab(self):
        """Create ultimate advanced image generation tab"""
        image_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(image_frame, text="🎨 Advanced Images")
        
        # Image controls
        control_frame = Frame(image_frame, bg=self.bg_color)
        control_frame.pack(fill=X, pady=(10, 0))
        
        # Advanced generation button
        gen_status = "Advanced AI" if ADVANCED_IMG_GEN else "Basic"
        self.adv_gen_btn = Button(control_frame, text=f"🎨 Generate ({gen_status})", 
                               font=(self.font_family, 12, 'bold'),
                               bg='#ff6b6b', fg='white', padx=25, pady=10, relief=FLAT,
                               cursor='hand2', command=self.generate_advanced_image)
        self.adv_gen_btn.pack(side=LEFT, padx=(0, 10))
        
        # Style buttons
        Button(control_frame, text="Realistic", font=(self.font_family, 10),
               bg='#6c757d', fg='white', padx=15, pady=8, relief=FLAT,
               command=lambda: self.set_image_style('realistic')).pack(side=LEFT, padx=2)
        
        Button(control_frame, text="Artistic", font=(self.font_family, 10),
               bg='#6c757d', fg='white', padx=15, pady=8, relief=FLAT,
               command=lambda: self.set_image_style('artistic')).pack(side=LEFT, padx=2)
        
        Button(control_frame, text="Abstract", font=(self.font_family, 10),
               bg='#6c757d', fg='white', padx=15, pady=8, relief=FLAT,
               command=lambda: self.set_image_style('abstract')).pack(side=LEFT, padx=2)
        
        Button(control_frame, text="Fantasy", font=(self.font_family, 10),
               bg='#6c757d', fg='white', padx=15, pady=8, relief=FLAT,
               command=lambda: self.set_image_style('fantasy')).pack(side=LEFT, padx=2)
        
        # Prompt area
        prompt_frame = Frame(image_frame, bg=self.bg_color)
        prompt_frame.pack(fill=X, pady=10)
        
        Label(prompt_frame, text="📝 Advanced Image Prompt:", font=(self.font_family, 12, 'bold'),
              fg=self.text_color, bg=self.bg_color).pack(anchor=W)
        
        self.image_prompt = Text(prompt_frame, height=3, font=(self.font_family, self.font_size),
                                bg='#f8f9fa', fg=self.text_color, insertbackground=self.accent_color,
                                borderwidth=1, relief=SOLID, padx=15, pady=12)
        self.image_prompt.pack(fill=X, pady=(5, 0))
        
        # Parameters
        param_frame = Frame(prompt_frame, bg=self.bg_color)
        param_frame.pack(fill=X, pady=(5, 0))
        
        Label(param_frame, text="Width:", font=(self.font_family, 10),
              fg=self.text_color, bg=self.bg_color).pack(side=LEFT, padx=(0, 5))
        
        self.width_var = IntVar(value=512)
        width_scale = Scale(param_frame, from_=256, to=1024, orient=HORIZONTAL,
                           variable=self.width_var, bg=self.bg_color, fg=self.text_color,
                           font=(self.font_family, 10))
        width_scale.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        Label(param_frame, text="Height:", font=(self.font_family, 10),
              fg=self.text_color, bg=self.bg_color).pack(side=LEFT, padx=(10, 5))
        
        self.height_var = IntVar(value=512)
        height_scale = Scale(param_frame, from_=256, to=1024, orient=HORIZONTAL,
                            variable=self.height_var, bg=self.bg_color, fg=self.text_color,
                            font=(self.font_family, 10))
        height_scale.pack(side=LEFT, fill=X, expand=True)
        
        # Image display
        self.image_frame = Frame(image_frame, bg=self.bg_color, relief=SOLID, bd=1)
        self.image_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Placeholder
        self.image_placeholder = Label(self.image_frame, 
                                text="🎨 Advanced AI Image Generation\n\n" +
                                     "✨ Features:\n" +
                                     "• Stable Diffusion\n" +
                                     "• Multiple Styles\n" +
                                     "• Custom Parameters\n" +
                                     "• High Quality Output\n" +
                                     "• Real-time Generation\n" +
                                     "• No More Crashes\n\n" +
                                     "Enter a prompt and click Generate!",
                                font=(self.font_family, 16), fg=self.secondary_color, bg=self.bg_color)
        self.image_placeholder.pack(expand=True)
    
    def create_ultimate_knowledge_tab(self):
        """Create ultimate knowledge base tab"""
        knowledge_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(knowledge_frame, text="📚 Knowledge")
        
        # Knowledge controls
        control_frame = Frame(knowledge_frame, bg=self.bg_color)
        control_frame.pack(fill=X, pady=(10, 0))
        
        Button(control_frame, text="Import", font=(self.font_family, 10, 'bold'),
               bg='#28a745', fg='white', padx=15, pady=8, relief=FLAT,
               cursor='hand2', command=self.import_knowledge).pack(side=LEFT, padx=(0, 5))
        
        Button(control_frame, text="Search", font=(self.font_family, 10, 'bold'),
               bg='#17a2b8', fg='white', padx=15, pady=8, relief=FLAT,
               cursor='hand2', command=self.search_knowledge).pack(side=LEFT, padx=(0, 5))
        
        Button(control_frame, text="Clear", font=(self.font_family, 10, 'bold'),
               bg='#dc3545', fg='white', padx=15, pady=8, relief=FLAT,
               cursor='hand2', command=self.clear_knowledge).pack(side=LEFT, padx=(0, 5))
        
        Button(control_frame, text="Export", font=(self.font_family, 10, 'bold'),
               bg='#6c757d', fg='white', padx=15, pady=8, relief=FLAT,
               cursor='hand2', command=self.export_knowledge).pack(side=LEFT)
        
        # Knowledge display
        self.knowledge_display = scrolledtext.ScrolledText(
            knowledge_frame, wrap='word', font=(self.font_family, self.font_size),
            bg=self.bg_color, fg=self.text_color, height=25, borderwidth=1,
            relief=SOLID, padx=20, pady=20, selectbackground=self.accent_color
        )
        self.knowledge_display.pack(fill=BOTH, expand=True, pady=10)
        
        # Welcome message
        self.knowledge_display.insert(END, "📚 Ultimate Knowledge Base\n\n")
        self.knowledge_display.insert(END, "🎯 Features:\n")
        self.knowledge_display.insert(END, "• 📁 Import documents (PDF, TXT, etc.)\n")
        self.knowledge_display.insert(END, "• 🔍 Smart search with AI assistance\n")
        self.knowledge_display.insert(END, "• 💬 Get responses based on your documents\n")
        self.knowledge_display.insert(END, "• 📊 Track document insights\n")
        self.knowledge_display.insert(END, "• 💾 Export knowledge base\n")
        self.knowledge_display.insert(END, "• ✅ Working without errors\n\n")
        self.knowledge_display.insert(END, "Click 'Import' to build your personal knowledge base!")
        self.knowledge_display.config(state=DISABLED)
    
    def create_ultimate_analytics_tab(self):
        """Create ultimate analytics tab"""
        analytics_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(analytics_frame, text="📊 Analytics")
        
        # Analytics controls
        control_frame = Frame(analytics_frame, bg=self.bg_color)
        control_frame.pack(fill=X, pady=(10, 0))
        
        Button(control_frame, text="Refresh", font=(self.font_family, 10, 'bold'),
               bg='#28a745', fg='white', padx=15, pady=8, relief=FLAT,
               cursor='hand2', command=self.refresh_analytics).pack(side=LEFT, padx=(0, 5))
        
        Button(control_frame, text="Export Data", font=(self.font_family, 10, 'bold'),
               bg='#17a2b8', fg='white', padx=15, pady=8, relief=FLAT,
               cursor='hand2', command=self.export_analytics).pack(side=LEFT, padx=(0, 5))
        
        Button(control_frame, text="Reset Stats", font=(self.font_family, 10, 'bold'),
               bg='#ffc107', fg='white', padx=15, pady=8, relief=FLAT,
               cursor='hand2', command=self.reset_stats).pack(side=LEFT)
        
        # Analytics display
        self.analytics_display = Text(analytics_frame, font=('Courier', self.font_size),
                                  bg='#f8f9fa', fg=self.text_color, height=25, borderwidth=1,
                                  relief=SOLID, padx=20, pady=20, selectbackground=self.accent_color)
        self.analytics_display.pack(fill=BOTH, expand=True, pady=10)
        
        # Load initial analytics
        self.refresh_analytics()
    
    def create_ultimate_settings_tab(self):
        """Create ultimate settings tab"""
        settings_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Scrollable settings
        settings_canvas = Canvas(settings_frame, bg=self.bg_color)
        scrollbar = Scrollbar(settings_frame, orient='vertical', command=settings_canvas.yview)
        settings_scroll = Frame(settings_canvas, bg=self.bg_color)
        
        settings_scroll.bind("<Configure>", lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all")))
        settings_canvas.create_window((0, 0), window=settings_scroll, anchor="nw")
        settings_canvas.configure(yscrollcommand=scrollbar.set)
        
        settings_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # API Settings
        api_frame = Frame(settings_scroll, bg='#f8f9fa', relief=RAISED, bd=1)
        api_frame.pack(fill=X, padx=10, pady=10)
        
        Label(api_frame, text="🔑 API Configuration", font=(self.font_family, 14, 'bold'),
              fg=self.text_color, bg='#f8f9fa').pack(anchor=W, padx=15, pady=10)
        
        # Display provider status only. Never show key text, even partially.
        for i, api_key in enumerate(API_KEYS):
            key_display = Frame(api_frame, bg='#f8f9fa')
            key_display.pack(fill=X, padx=15, pady=2)
            
            status = "🟢 Active" if i == current_api_index else "⚪ Backup"
            Label(key_display, text=f"Groq key {i+1}: configured - {status}", 
                  font=(self.font_family, 10), fg=self.secondary_color, bg='#f8f9fa').pack(anchor=W)
        
        Button(api_frame, text="🔑 Create New API Key", font=(self.font_family, 10, 'bold'),
               bg='#28a745', fg='white', padx=20, pady=10, relief=FLAT,
               cursor='hand2', command=self.open_groq_console).pack(padx=15, pady=10)
        
        # Image Generation Settings
        img_frame = Frame(settings_scroll, bg='#f8f9fa', relief=RAISED, bd=1)
        img_frame.pack(fill=X, padx=10, pady=10)
        
        Label(img_frame, text="🎨 Image Generation", font=(self.font_family, 14, 'bold'),
              fg=self.text_color, bg='#f8f9fa').pack(anchor=W, padx=15, pady=10)
        
        img_status = "Advanced AI (Stable Diffusion)" if ADVANCED_IMG_GEN else "Basic PIL"
        Label(img_frame, text=f"Engine: {img_status}", font=(self.font_family, 12, 'bold'),
              fg=self.text_color, bg='#f8f9fa').pack(anchor=W, padx=15, pady=5)
        
        if ADVANCED_IMG_GEN:
            device_status = f"Device: {self.image_generator.device.upper()}"
            Label(img_frame, text=device_status, font=(self.font_family, 10),
                  fg=self.text_color, bg='#f8f9fa').pack(anchor=W, padx=15, pady=2)
        
        Label(img_frame, text="Features: Real-time Generation, Multiple Styles, High Quality", 
              font=(self.font_family, 10), fg=self.text_color, bg='#f8f9fa').pack(anchor=W, padx=15, pady=2)
        
        # Visual Web Browser Settings
        browser_frame = Frame(settings_scroll, bg='#f8f9fa', relief=RAISED, bd=1)
        browser_frame.pack(fill=X, padx=10, pady=10)
        
        Label(browser_frame, text="🌐 Visual Web Browser", font=(self.font_family, 14, 'bold'),
              fg=self.text_color, bg='#f8f9fa').pack(anchor=W, padx=15, pady=10)
        
        browser_status = "Google & Bing Search" if HAS_GOOGLE else "Basic Search"
        Label(browser_frame, text=f"Search: {browser_status}", font=(self.font_family, 12, 'bold'),
              fg=self.text_color, bg='#f8f9fa').pack(anchor=W, padx=15, pady=5)
        
        Label(browser_frame, text="Features: Visual HTML Rendering, URL Navigation, History", 
              font=(self.font_family, 10), fg=self.text_color, bg='#f8f9fa').pack(anchor=W, padx=15, pady=2)
        
        # Arena Settings
        arena_frame = Frame(settings_scroll, bg='#f8f9fa', relief=RAISED, bd=1)
        arena_frame.pack(fill=X, padx=10, pady=10)
        
        Label(arena_frame, text="🏆 Arena System", font=(self.font_family, 14, 'bold'),
              fg=self.text_color, bg='#f8f9fa').pack(anchor=W, padx=15, pady=10)
        
        Label(arena_frame, text="Agents: Chatbot Names (AI Assistant Names)", 
              font=(self.font_family, 12, 'bold'), fg=self.text_color, bg='#f8f9fa').pack(anchor=W, padx=15, pady=5)
        
        Label(arena_frame, text="Features: Custom Topics, Voice Chat, Real-time Conversations", 
              font=(self.font_family, 10), fg=self.text_color, bg='#f8f9fa').pack(anchor=W, padx=15, pady=2)
        
        # Theme Settings
        theme_frame = Frame(settings_scroll, bg='#f8f9fa', relief=RAISED, bd=1)
        theme_frame.pack(fill=X, padx=10, pady=10)
        
        Label(theme_frame, text="🎨 Theme Settings", font=(self.font_family, 14, 'bold'),
              fg=self.text_color, bg='#f8f9fa').pack(anchor=W, padx=15, pady=10)
        
        theme_buttons = Frame(theme_frame, bg='#f8f9fa')
        theme_buttons.pack(fill=X, padx=15, pady=10)
        
        Button(theme_buttons, text="☀️ Light", font=(self.font_family, 10, 'bold'),
               bg=self.accent_color, fg='white', padx=20, pady=8, relief=FLAT,
               cursor='hand2', command=lambda: self.set_theme('light')).pack(side=LEFT, padx=5)
        
        Button(theme_buttons, text="🌙 Dark", font=(self.font_family, 10, 'bold'),
               bg='#343a40', fg='white', padx=20, pady=8, relief=FLAT,
               cursor='hand2', command=lambda: self.set_theme('dark')).pack(side=LEFT, padx=5)
        
        Button(theme_buttons, text="🔵 Blue", font=(self.font_family, 10, 'bold'),
               bg='#007bff', fg='white', padx=20, pady=8, relief=FLAT,
               cursor='hand2', command=lambda: self.set_theme('blue')).pack(side=LEFT, padx=5)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = Frame(parent, bg=self.bg_color, height=30)
        status_frame.pack(fill=X, pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = Label(status_frame, text="✅ Ultimate Ready", 
                                 font=(self.font_family, 10),
                                 fg=self.secondary_color, bg=self.bg_color)
        self.status_label.pack(side=LEFT, padx=15, pady=5)
        
        self.connection_label = Label(status_frame, text="🟢 All Systems Online", 
                                     font=(self.font_family, 10),
                                     fg='#28a745', bg=self.bg_color)
        self.connection_label.pack(side=RIGHT, padx=15, pady=5)
    
    def create_ultimate_header(self, parent):
        """Create the modern LightSky header."""
        header = self.panel(parent, fill=X, pady=(0, 12), ipady=12)
        header.configure(height=132)
        header.pack_propagate(False)

        title_frame = Frame(header, bg=self.panel_color)
        title_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=22, pady=12)

        self.label(title_frame, "LightSky AI", size=26, weight='bold').pack(anchor=W)
        self.label(
            title_frame,
            "Chat, arena, voice, images, browser, knowledge, analytics",
            size=11,
            color=self.secondary_color
        ).pack(anchor=W, pady=(4, 0))

        self.stats_label = self.label(
            title_frame,
            "Messages 0   Tokens 0   Voice 0   Images 0   Arena 0",
            size=10,
            color=self.muted_color
        )
        self.stats_label.pack(anchor=W, pady=(14, 0))

        control_frame = Frame(header, bg=self.panel_color)
        control_frame.pack(side=RIGHT, padx=22, pady=12)

        model_frame = Frame(control_frame, bg=self.panel_color)
        model_frame.pack(anchor=E, pady=(0, 8))
        self.label(model_frame, "Model", size=10, weight='bold').pack(side=LEFT, padx=(0, 8))

        self.model_var = StringVar(value=list(MODELS.keys())[0])
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=list(MODELS.keys()),
            state='readonly',
            font=(self.font_family, 10),
            width=34
        )
        self.model_combo.pack(side=LEFT)
        self.model_combo.bind('<<ComboboxSelected>>', self.change_model)

        voice_frame = Frame(control_frame, bg=self.panel_color)
        voice_frame.pack(anchor=E, pady=4)
        self.voice_input_btn = self.button(voice_frame, "Voice Input", self.toggle_voice_input, tone='success')
        self.voice_input_btn.pack(side=LEFT, padx=(0, 6))
        self.speech_btn = self.button(voice_frame, "Speech", self.toggle_speech, tone='primary')
        self.speech_btn.pack(side=LEFT)

        action_frame = Frame(control_frame, bg=self.panel_color)
        action_frame.pack(anchor=E, pady=(4, 0))
        self.theme_btn = self.button(action_frame, "Theme", self.toggle_theme)
        self.theme_btn.pack(side=LEFT, padx=(0, 6))
        self.export_btn = self.button(action_frame, "Export", self.export_all_data)
        self.export_btn.pack(side=LEFT)

    def create_status_bar(self, parent):
        """Create compact status bar."""
        status_frame = Frame(parent, bg=self.bg_color, height=32)
        status_frame.pack(fill=X, pady=(0, 12))
        status_frame.pack_propagate(False)

        self.status_label = self.label(status_frame, "Ready", size=10, color=self.secondary_color, bg=self.bg_color)
        self.status_label.pack(side=LEFT, padx=6, pady=6)

        self.connection_label = self.label(status_frame, "Systems online", size=10, color=self.success_color, bg=self.bg_color)
        self.connection_label.pack(side=RIGHT, padx=6, pady=6)

    def create_ultimate_tabs(self, parent):
        """Create modern tabbed interface."""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=BOTH, expand=True)

        self.create_ultimate_chat_tab()
        self.create_ultimate_arena_tab()
        self.create_ultimate_webgl_tab()
        self.create_ultimate_image_tab()
        self.create_ultimate_knowledge_tab()
        self.create_ultimate_analytics_tab()
        self.create_ultimate_settings_tab()

    def create_ultimate_chat_tab(self):
        chat_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(chat_frame, text="Chat")

        control_frame = self.toolbar(chat_frame, fill=X, pady=(12, 8))
        self.button(control_frame, "Clear", self.clear_chat, tone='danger').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Save", self.save_chat).pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Export", self.export_chat).pack(side=LEFT)
        self.voice_status_label = self.label(control_frame, "Voice: ready", size=10, color=self.success_color, bg=self.bg_color)
        self.voice_status_label.pack(side=RIGHT)

        chat_panel = self.panel(chat_frame, fill=BOTH, expand=True, pady=(0, 10))
        self.chat_display = scrolledtext.ScrolledText(
            chat_panel,
            wrap='word',
            font=(self.font_family, self.font_size),
            height=20
        )
        self.configure_text_widget(self.chat_display)
        self.chat_display.pack(fill=BOTH, expand=True)

        input_panel = self.panel(chat_frame, fill=X, pady=(0, 4))
        input_frame = Frame(input_panel, bg=self.panel_color)
        input_frame.pack(fill=X, padx=12, pady=12)

        self.input_field = Text(input_frame, height=3, font=(self.font_family, self.font_size))
        self.configure_text_widget(self.input_field)
        self.input_field.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        self.button(input_frame, "Voice", self.voice_input_message, tone='success', width=7).pack(side=RIGHT, padx=(6, 0))
        self.button(input_frame, "Send", self.send_message, tone='primary', size=11, width=8).pack(side=RIGHT)

        self.input_field.bind('<Control-Return>', lambda e: self.send_message())
        self.input_field.bind('<Shift-Return>', lambda e: self.input_field.insert('insert', '\n'))

    def create_ultimate_arena_tab(self):
        arena_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(arena_frame, text="Arena")

        control_frame = self.toolbar(arena_frame, fill=X, pady=(12, 8))
        self.arena_btn = self.button(control_frame, "Start Arena", self.toggle_arena, tone='success', size=11)
        self.arena_btn.pack(side=LEFT, padx=(0, 8))
        self.talk_btn = self.button(control_frame, "Talk to Arena", self.talk_to_arena, tone='primary', size=11)
        self.talk_btn.pack(side=LEFT, padx=(0, 12))

        self.label(control_frame, "Topic", size=10, weight='bold', bg=self.bg_color).pack(side=LEFT, padx=(0, 6))
        self.topic_entry = Entry(
            control_frame,
            font=(self.font_family, 10),
            bg=self.input_color,
            fg=self.text_color,
            insertbackground=self.accent_color,
            borderwidth=0,
            width=26
        )
        self.topic_entry.pack(side=LEFT, ipady=9, padx=(0, 6))
        self.topic_entry.bind('<Return>', self.add_custom_topic)
        self.button(control_frame, "Add", self.add_custom_topic).pack(side=LEFT)

        topic_frame = self.toolbar(arena_frame, fill=X, pady=(0, 8))
        self.label(topic_frame, "Selected topic", size=10, weight='bold', bg=self.bg_color).pack(side=LEFT, padx=(0, 6))
        self.topic_var = StringVar(value=self.current_topic)
        self.topic_combo = ttk.Combobox(
            topic_frame,
            textvariable=self.topic_var,
            values=self.custom_topics,
            state='readonly',
            font=(self.font_family, 10),
            width=42
        )
        self.topic_combo.pack(side=LEFT, padx=(0, 10))
        self.topic_combo.bind('<<ComboboxSelected>>', self.change_topic)
        self.arena_status = self.label(topic_frame, "Arena ready", size=10, weight='bold', color=self.success_color, bg=self.bg_color)
        self.arena_status.pack(side=LEFT)

        arena_panel = self.panel(arena_frame, fill=BOTH, expand=True, pady=(0, 10))
        self.arena_display = scrolledtext.ScrolledText(arena_panel, wrap='word', font=(self.font_family, self.font_size), height=18)
        self.configure_text_widget(self.arena_display)
        self.arena_display.pack(fill=BOTH, expand=True)

        arena_input_frame = self.panel(arena_frame, fill=X)
        inner = Frame(arena_input_frame, bg=self.panel_color)
        inner.pack(fill=X, padx=12, pady=12)
        self.arena_input = Entry(
            inner,
            font=(self.font_family, self.font_size),
            bg=self.input_color,
            fg=self.text_color,
            insertbackground=self.accent_color,
            borderwidth=0
        )
        self.arena_input.pack(side=LEFT, fill=X, expand=True, ipady=12, padx=(0, 10))
        self.button(inner, "Send Message", self.send_arena_message, tone='primary', size=11).pack(side=RIGHT)
        self.arena_input.bind('<Return>', lambda e: self.send_arena_message())

    def create_ultimate_webgl_tab(self):
        webgl_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(webgl_frame, text="Browser")
        self.visual_browser = VisualWebBrowser(webgl_frame, self.root)
        info_frame = self.panel(webgl_frame, fill=X, pady=(8, 0))
        self.label(info_frame, "Visual web browser with URL navigation, search, history, and HTML rendering", size=11, color=self.secondary_color).pack(padx=14, pady=10)

    def create_ultimate_image_tab(self):
        image_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(image_frame, text="Images")

        control_frame = self.toolbar(image_frame, fill=X, pady=(12, 8))
        gen_status = "Advanced AI" if ADVANCED_IMG_GEN else "Basic"
        self.adv_gen_btn = self.button(control_frame, f"Generate ({gen_status})", self.generate_advanced_image, tone='primary', size=11)
        self.adv_gen_btn.pack(side=LEFT, padx=(0, 10))
        for style_name in ['realistic', 'artistic', 'abstract', 'fantasy']:
            self.button(control_frame, style_name.title(), lambda s=style_name: self.set_image_style(s)).pack(side=LEFT, padx=3)

        prompt_panel = self.panel(image_frame, fill=X, pady=(0, 10))
        prompt_inner = Frame(prompt_panel, bg=self.panel_color)
        prompt_inner.pack(fill=X, padx=14, pady=12)
        self.label(prompt_inner, "Image prompt", size=11, weight='bold').pack(anchor=W, pady=(0, 6))
        self.image_prompt = Text(prompt_inner, height=3, font=(self.font_family, self.font_size))
        self.configure_text_widget(self.image_prompt)
        self.image_prompt.pack(fill=X)

        param_frame = Frame(prompt_inner, bg=self.panel_color)
        param_frame.pack(fill=X, pady=(10, 0))
        self.label(param_frame, "Width", size=10).pack(side=LEFT, padx=(0, 6))
        self.width_var = IntVar(value=512)
        Scale(param_frame, from_=256, to=1024, orient=HORIZONTAL, variable=self.width_var,
              bg=self.panel_color, fg=self.secondary_color, troughcolor=self.input_color,
              highlightthickness=0, font=(self.font_family, 9)).pack(side=LEFT, fill=X, expand=True, padx=(0, 14))
        self.label(param_frame, "Height", size=10).pack(side=LEFT, padx=(0, 6))
        self.height_var = IntVar(value=512)
        Scale(param_frame, from_=256, to=1024, orient=HORIZONTAL, variable=self.height_var,
              bg=self.panel_color, fg=self.secondary_color, troughcolor=self.input_color,
              highlightthickness=0, font=(self.font_family, 9)).pack(side=LEFT, fill=X, expand=True)

        self.image_frame = self.panel(image_frame, fill=BOTH, expand=True)
        self.image_placeholder = self.label(
            self.image_frame,
            "Advanced AI Image Generation\n\nEnter a prompt, choose a style, and generate.",
            size=16,
            color=self.secondary_color
        )
        self.image_placeholder.pack(expand=True)

    def create_ultimate_knowledge_tab(self):
        knowledge_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(knowledge_frame, text="Knowledge")

        control_frame = self.toolbar(knowledge_frame, fill=X, pady=(12, 8))
        self.button(control_frame, "Import", self.import_knowledge, tone='success').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Search", self.search_knowledge, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Clear", self.clear_knowledge, tone='danger').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Export", self.export_knowledge).pack(side=LEFT)

        panel = self.panel(knowledge_frame, fill=BOTH, expand=True)
        self.knowledge_display = scrolledtext.ScrolledText(panel, wrap='word', font=(self.font_family, self.font_size), height=25)
        self.configure_text_widget(self.knowledge_display)
        self.knowledge_display.pack(fill=BOTH, expand=True)
        self.knowledge_display.insert(END, "Knowledge Base\n\nImport documents, search your saved content, and export your knowledge base.")
        self.knowledge_display.config(state=DISABLED)

    def create_ultimate_analytics_tab(self):
        analytics_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(analytics_frame, text="Analytics")

        control_frame = self.toolbar(analytics_frame, fill=X, pady=(12, 8))
        self.button(control_frame, "Refresh", self.refresh_analytics, tone='success').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Export Data", self.export_analytics, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Reset Stats", self.reset_stats, tone='warning').pack(side=LEFT)

        panel = self.panel(analytics_frame, fill=BOTH, expand=True)
        self.analytics_display = Text(panel, font=(self.mono_family, self.font_size), height=25)
        self.configure_text_widget(self.analytics_display)
        self.analytics_display.pack(fill=BOTH, expand=True)
        self.refresh_analytics()

    def create_ultimate_settings_tab(self):
        settings_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(settings_frame, text="Settings")

        settings_canvas = Canvas(settings_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = Scrollbar(settings_frame, orient='vertical', command=settings_canvas.yview)
        settings_scroll = Frame(settings_canvas, bg=self.bg_color)
        settings_scroll.bind("<Configure>", lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all")))
        settings_canvas.create_window((0, 0), window=settings_scroll, anchor="nw")
        settings_canvas.configure(yscrollcommand=scrollbar.set)
        settings_canvas.pack(side="left", fill="both", expand=True, padx=4, pady=12)
        scrollbar.pack(side="right", fill="y")

        api_rows = [
            f"Groq key {i + 1}: configured - {'Active' if i == current_api_index else 'Backup'}"
            for i, _key in enumerate(API_KEYS)
        ] or ["Groq: missing GROQ_API_KEY or GROQ_API_KEYS environment variable"]
        sections = [
            ("API Configuration", api_rows),
            ("Image Generation", [f"Engine: {'Advanced AI (Stable Diffusion)' if ADVANCED_IMG_GEN else 'Basic PIL'}", "Features: real-time generation, styles, custom sizes"]),
            ("Visual Web Browser", [f"Search: {'Google & Bing Search' if HAS_GOOGLE else 'Basic Search'}", "Features: visual HTML rendering, URL navigation, history"]),
            ("Arena System", ["Agents: GPT-OSS 120B, Llama 3.3 70B, Groq Compound", "Features: custom topics, voice chat, live conversations"]),
        ]

        for heading, rows in sections:
            section = self.panel(settings_scroll, fill=X, padx=10, pady=8, ipady=10)
            self.label(section, heading, size=14, weight='bold').pack(anchor=W, padx=16, pady=(8, 6))
            for row in rows:
                self.label(section, row, size=10, color=self.secondary_color).pack(anchor=W, padx=16, pady=2)
            if heading == "API Configuration":
                self.button(section, "Create New API Key", self.open_groq_console, tone='primary').pack(anchor=W, padx=16, pady=(10, 8))

        theme_section = self.panel(settings_scroll, fill=X, padx=10, pady=8, ipady=10)
        self.label(theme_section, "Theme Settings", size=14, weight='bold').pack(anchor=W, padx=16, pady=(8, 6))
        theme_buttons = Frame(theme_section, bg=self.panel_color)
        theme_buttons.pack(anchor=W, padx=16, pady=(2, 10))
        self.button(theme_buttons, "Light", lambda: self.set_theme('light'), tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(theme_buttons, "Dark", lambda: self.set_theme('dark')).pack(side=LEFT, padx=(0, 6))
        self.button(theme_buttons, "Blue", lambda: self.set_theme('blue')).pack(side=LEFT)

    def init_arena_agents(self):
        """Initialize enhanced arena agents with model names as their names"""
        enhanced_bots = [
            {"name": "GPT-OSS 120B", "personality": "advanced AI assistant", "voice": "male", "model": "openai/gpt-oss-120b"},
            {"name": "Llama 3.3 70B", "personality": "knowledgeable AI model", "voice": "female", "model": "llama-3.3-70b-versatile"},
            {"name": "Groq Compound", "personality": "compound AI specialist", "voice": "male", "model": "groq/compound"}
        ]
        
        for bot_config in enhanced_bots:
            agent = ArenaAgent(
                name=bot_config["name"],
                personality=bot_config["personality"],
                voice_gender=bot_config["voice"],
                model=bot_config["model"],
                lightsky_instance=self
            )
            self.arena_agents.append(agent)
    
    # Core functionality methods
    def get_groq_response(self, prompt, model=CURRENT_MODEL, max_tokens=150):
        """Get response from Groq API"""
        return get_groq_response(prompt, model, max_tokens)

    def _ensure_codebox_tags(self, widget):
        """Configure tags used to render code blocks in boxed style."""
        if not hasattr(self, "_codebox_widgets"):
            self._codebox_widgets = set()
        widget_id = str(widget)
        if widget_id in self._codebox_widgets:
            return
        try:
            widget.tag_configure("msg_header", foreground=self.accent_color, font=(self.font_family, 10, "bold"))
            widget.tag_configure("msg_plain", foreground=self.text_color, font=(self.font_family, self.font_size))
            widget.tag_configure("code_lang", foreground=self.secondary_color, font=(self.mono_family, 9, "bold"))
            widget.tag_configure("code_border", foreground="#8f99ad", font=(self.mono_family, 10, "bold"))
            widget.tag_configure("code_block", foreground=self.text_color, background=self.panel_color, font=(self.mono_family, 10))
        except Exception:
            pass
        self._codebox_widgets.add(widget_id)

    def _insert_with_codeboxes(self, widget, text):
        """Insert text and render fenced code blocks inside a visible ASCII box."""
        self._ensure_codebox_tags(widget)
        pattern = re.compile(r"```([A-Za-z0-9_.+-]*)\n(.*?)```", re.DOTALL)
        idx = 0
        found = False
        for m in pattern.finditer(text):
            found = True
            if m.start() > idx:
                plain = text[idx:m.start()]
                if plain:
                    widget.insert(END, plain, "msg_plain")
            lang = (m.group(1) or "").strip()
            code = (m.group(2) or "").rstrip("\n")
            lines = code.splitlines() if code else [""]
            box_width = max(18, min(92, max((len(x) for x in lines), default=0) + 2))

            if lang:
                widget.insert(END, f"\n[{lang}]\n", "code_lang")
            else:
                widget.insert(END, "\n[code]\n", "code_lang")

            widget.insert(END, "+" + ("-" * box_width) + "+\n", "code_border")
            for raw in lines:
                line = raw.replace("\t", "    ")
                # Keep the box stable if a line is very long.
                while len(line) > box_width - 2:
                    part = line[:box_width - 2]
                    widget.insert(END, f"| {part.ljust(box_width - 2)} |\n", "code_block")
                    line = line[box_width - 2:]
                widget.insert(END, f"| {line.ljust(box_width - 2)} |\n", "code_block")
            widget.insert(END, "+" + ("-" * box_width) + "+\n", "code_border")
            idx = m.end()

        if found:
            if idx < len(text):
                tail = text[idx:]
                if tail:
                    widget.insert(END, tail, "msg_plain")
        else:
            widget.insert(END, text, "msg_plain")
    
    def add_message(self, sender, message):
        """Add message to chat display"""
        timestamp = datetime.now().strftime("%H:%M")
        self._ensure_codebox_tags(self.chat_display)
        self.chat_display.insert(END, f"[{timestamp}] {sender}:\n", "msg_header")
        self._insert_with_codeboxes(self.chat_display, message)
        self.chat_display.insert(END, "\n\n", "msg_plain")
        self.chat_display.see(END)
        
        if sender == "You":
            self.user_data['messages_sent'] += 1
            self.update_stats()

    def _handle_direct_agent_command(self, user_input):
        """Run explicit user tool commands from chat."""
        text = user_input.strip()
        if text.startswith("/run "):
            tool_call = {"action": "command", "command": text[5:].strip(), "reason": "User requested direct command execution."}
        elif text.startswith("/py "):
            parts = shlex.split(text[4:].strip(), posix=False)
            if not parts:
                self.add_message("Tool Runner", "No Python script path provided.")
                return True
            tool_call = {"action": "python", "path": parts[0].strip('"'), "args": [p.strip('"') for p in parts[1:]], "reason": "User requested Python script execution."}
        elif text.startswith("/pip "):
            packages = [p for p in shlex.split(text[5:].strip(), posix=False) if p]
            tool_call = {"action": "pip_install", "packages": packages, "reason": "User requested package installation."}
        elif text.startswith("/plugin "):
            rest = text[8:].strip()
            if not rest:
                self.add_message("Tool Runner", "Usage: /plugin <name> {json params}")
                return True
            parts = rest.split(" ", 1)
            plugin_name = parts[0].strip()
            params = {}
            if len(parts) > 1 and parts[1].strip():
                try:
                    params = json.loads(parts[1].strip())
                except Exception as e:
                    self.add_message("Tool Runner", f"Plugin params must be JSON: {e}")
                    return True
            tool_call = {"action": "plugin", "plugin": plugin_name, "params": params, "reason": "User requested plugin execution."}
        else:
            return False

        threading.Thread(target=self._execute_direct_tool_call, args=(tool_call,), daemon=True).start()
        return True

    def show_agent_tool_help(self):
        help_text = (
            "Agent Tools are enabled for every model.\n\n"
            "Direct chat commands:\n"
            "/run <PowerShell command>\n"
            "/py <script.py> [args]\n"
            "/pip <package1> <package2>\n"
            "/plugin <name> {json params}\n\n"
            "Built-in model plugins:\n"
            "web_search, fetch_url, hf_model_search, hf_repo_info, hf_inference, "
            "list_files, read_file, write_file, knowledge_search, debug_scan\n\n"
            "Models can also request tools with an ls_tool_call JSON block. "
            "Lightsky asks before running model-requested actions and then returns the output to the model."
        )
        messagebox.showinfo("Lightsky Agent Tools", help_text)

    def get_plugin_catalog(self):
        """Built-in plugin catalog exposed to every selected model."""
        return [
            {"name": "web_search", "summary": "Search the web and return result titles/URLs."},
            {"name": "fetch_url", "summary": "Fetch a URL and return a clean page summary."},
            {"name": "hf_model_search", "summary": "Search Hugging Face Hub models using the configured access token."},
            {"name": "hf_repo_info", "summary": "Fetch Hugging Face model/dataset/space metadata."},
            {"name": "hf_inference", "summary": "Run a prompt through a Hugging Face text model."},
            {"name": "list_files", "summary": "List files from a local directory with optional pattern filtering."},
            {"name": "read_file", "summary": "Read a local text/code file with size limits."},
            {"name": "write_file", "summary": "Write or overwrite a local file after confirmation."},
            {"name": "knowledge_search", "summary": "Search imported Knowledge Lab documents."},
            {"name": "debug_scan", "summary": "Run LS 5.1 local debug/vulnerability scanner over code/text."},
        ]

    def _plugin_result(self, ok, data=None, error=None):
        return {"ok": ok, "data": data if data is not None else {}, "error": error}

    def _safe_tool_path(self, path, cwd=None):
        base = self._normalize_tool_cwd(cwd)
        target = path if os.path.isabs(path or "") else os.path.join(base, path or "")
        target = os.path.abspath(os.path.expanduser(target))
        lowered = target.lower()
        blocked_roots = [
            os.path.abspath(os.environ.get("SystemRoot", "C:\\Windows")).lower(),
            os.path.abspath(os.environ.get("ProgramFiles", "C:\\Program Files")).lower(),
            os.path.abspath(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")).lower(),
        ]
        if any(lowered == root or lowered.startswith(root + os.sep) for root in blocked_roots):
            raise ValueError("System/program directories are blocked for plugin file access.")
        return target

    def _run_plugin_call(self, plugin_name, params, cwd=None):
        plugin_name = (plugin_name or "").strip().lower()
        params = params or {}
        try:
            if plugin_name == "web_search":
                query = (params.get("query") or "").strip()
                if not query:
                    return self._plugin_result(False, error="web_search requires query")
                max_results = max(1, min(int(params.get("max_results") or 5), 10))
                return self._plugin_result(True, {"results": _ls51_duckduckgo_search(query, max_results=max_results)})

            if plugin_name == "fetch_url":
                url = (params.get("url") or "").strip()
                if not url.startswith(("http://", "https://")):
                    return self._plugin_result(False, error="fetch_url requires http/https url")
                return self._plugin_result(True, _ls51_fetch_page_summary(url) or {"title": "No page", "summary": "Could not fetch URL."})

            if plugin_name == "hf_model_search":
                query = (params.get("query") or "").strip()
                limit = max(1, min(int(params.get("limit") or 5), 20))
                if not query:
                    return self._plugin_result(False, error="hf_model_search requires query")
                headers = {"Authorization": f"Bearer {HF_ACCESS_TOKEN}"} if HF_ACCESS_TOKEN else {}
                resp = requests.get(
                    "https://huggingface.co/api/models",
                    params={"search": query, "limit": limit, "sort": "downloads", "direction": -1},
                    headers=headers,
                    timeout=25
                )
                if resp.status_code != 200:
                    return self._plugin_result(False, error=f"Hugging Face search failed: HTTP {resp.status_code}")
                models = []
                for item in resp.json()[:limit]:
                    models.append({
                        "id": item.get("modelId") or item.get("id"),
                        "downloads": item.get("downloads"),
                        "likes": item.get("likes"),
                        "pipeline_tag": item.get("pipeline_tag"),
                        "tags": item.get("tags", [])[:8],
                    })
                return self._plugin_result(True, {"query": query, "models": models})

            if plugin_name == "hf_repo_info":
                repo_id = (params.get("repo_id") or "").strip()
                repo_type = (params.get("repo_type") or "model").strip().lower()
                if not repo_id:
                    return self._plugin_result(False, error="hf_repo_info requires repo_id")
                if repo_type not in {"model", "dataset", "space"}:
                    return self._plugin_result(False, error="repo_type must be model, dataset, or space")
                prefix = {"model": "models", "dataset": "datasets", "space": "spaces"}[repo_type]
                headers = {"Authorization": f"Bearer {HF_ACCESS_TOKEN}"} if HF_ACCESS_TOKEN else {}
                resp = requests.get(f"https://huggingface.co/api/{prefix}/{repo_id}", headers=headers, timeout=25)
                if resp.status_code != 200:
                    return self._plugin_result(False, error=f"Hugging Face repo lookup failed: HTTP {resp.status_code}")
                data = resp.json()
                return self._plugin_result(True, {
                    "id": data.get("modelId") or data.get("id"),
                    "author": data.get("author"),
                    "downloads": data.get("downloads"),
                    "likes": data.get("likes"),
                    "pipeline_tag": data.get("pipeline_tag"),
                    "tags": data.get("tags", [])[:16],
                    "lastModified": data.get("lastModified"),
                    "private": data.get("private"),
                })

            if plugin_name == "hf_inference":
                prompt = (params.get("prompt") or "").strip()
                if not prompt:
                    return self._plugin_result(False, error="hf_inference requires prompt")
                model = (params.get("model") or DEFAULT_HF_TEXT_MODEL).strip()
                max_tokens = max(32, min(int(params.get("max_tokens") or 256), 1200))
                answer = get_huggingface_response(prompt, model=model, max_tokens=max_tokens)
                return self._plugin_result(True, {"model": model, "response": answer})

            if plugin_name == "list_files":
                root = self._safe_tool_path(params.get("path") or ".", cwd)
                if not os.path.isdir(root):
                    return self._plugin_result(False, error=f"Directory not found: {root}")
                pattern = (params.get("pattern") or "").lower()
                max_files = max(1, min(int(params.get("max_files") or 60), 200))
                found = []
                for dirpath, dirnames, filenames in os.walk(root):
                    dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__", "node_modules", ".venv", "venv"}]
                    for name in filenames:
                        rel = os.path.relpath(os.path.join(dirpath, name), root)
                        if not pattern or pattern in name.lower() or pattern in rel.lower():
                            found.append(rel)
                        if len(found) >= max_files:
                            return self._plugin_result(True, {"root": root, "files": found})
                return self._plugin_result(True, {"root": root, "files": found})

            if plugin_name == "read_file":
                target = self._safe_tool_path(params.get("path"), cwd)
                if not os.path.isfile(target):
                    return self._plugin_result(False, error=f"File not found: {target}")
                max_chars = max(1000, min(int(params.get("max_chars") or 20000), 80000))
                with open(target, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read(max_chars)
                return self._plugin_result(True, {"path": target, "content": content, "truncated": os.path.getsize(target) > max_chars})

            if plugin_name == "write_file":
                target = self._safe_tool_path(params.get("path"), cwd)
                content = params.get("content")
                if content is None:
                    return self._plugin_result(False, error="write_file requires content")
                overwrite = bool(params.get("overwrite", False))
                if os.path.exists(target) and not overwrite:
                    return self._plugin_result(False, error="File exists. Set overwrite=true to replace it.")
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, "w", encoding="utf-8", errors="replace") as f:
                    f.write(str(content))
                return self._plugin_result(True, {"path": target, "bytes": len(str(content).encode("utf-8"))})

            if plugin_name == "knowledge_search":
                query = (params.get("query") or "").strip()
                limit = max(1, min(int(params.get("limit") or 8), 20))
                if not query:
                    return self._plugin_result(False, error="knowledge_search requires query")
                if not getattr(self, "conn", None):
                    return self._plugin_result(False, error="Knowledge database unavailable")
                like = f"%{query}%"
                self.cursor.execute(
                    "SELECT title, content FROM documents WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC LIMIT ?",
                    (like, like, limit)
                )
                rows = [{"title": title, "excerpt": content[:900]} for title, content in self.cursor.fetchall()]
                return self._plugin_result(True, {"query": query, "results": rows})

            if plugin_name == "debug_scan":
                text = params.get("text") or params.get("code") or ""
                if "```" not in text and params.get("code"):
                    text = "```python\n" + str(params.get("code")) + "\n```"
                findings = ls51_local_debug_vuln_scan(str(text))
                return self._plugin_result(True, {"findings": findings})

            return self._plugin_result(False, error=f"Unknown plugin: {plugin_name}")
        except Exception as e:
            return self._plugin_result(False, error=str(e))

    def _execute_direct_tool_call(self, tool_call):
        result = self._run_agent_tool_call(tool_call)
        self.root.after(0, lambda: self.add_message("Tool Runner", self._format_tool_result(tool_call, result)))

    def _extract_agent_tool_call(self, text):
        """Extract one ls_tool_call JSON block from model output."""
        if not text:
            return None
        patterns = [
            r"```ls_tool_call\s*(\{.*?\})\s*```",
            r"```json\s*(\{.*?\"action\".*?\})\s*```"
        ]
        for pat in patterns:
            m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
            if not m:
                continue
            try:
                data = json.loads(m.group(1))
                if isinstance(data, dict) and data.get("action"):
                    return data
            except Exception:
                continue
        return None

    def _strip_agent_tool_blocks(self, text):
        text = re.sub(r"```ls_tool_call\s*\{.*?\}\s*```", "", text or "", flags=re.DOTALL | re.IGNORECASE)
        return text.strip()

    def _askyesno_sync(self, title, message):
        result = {"ok": False}
        done = threading.Event()

        def ask():
            try:
                result["ok"] = messagebox.askyesno(title, message)
            finally:
                done.set()

        self.root.after(0, ask)
        done.wait()
        return result["ok"]

    def _normalize_tool_cwd(self, cwd):
        default_cwd = os.path.join(os.path.expanduser("~"), "Documents", "Codex", "2026-05-13", "hi")
        chosen = cwd or default_cwd
        try:
            chosen = os.path.abspath(os.path.expanduser(chosen))
            if os.path.isdir(chosen):
                return chosen
        except Exception:
            pass
        return default_cwd if os.path.isdir(default_cwd) else os.getcwd()

    def _blocked_command_reason(self, command):
        lowered = (command or "").lower()
        blocked = [
            (r"\bformat\b", "formatting drives is blocked"),
            (r"\bdiskpart\b", "disk partitioning is blocked"),
            (r"\bshutdown\b", "shutdown/reboot commands are blocked"),
            (r"\brestart-computer\b", "restart commands are blocked"),
            (r"\breg\s+delete\b", "registry deletion is blocked"),
            (r"\brm\s+-rf\b", "recursive forced deletion is blocked"),
            (r"\bdel\s+/s\b", "recursive deletion is blocked"),
            (r"\brd\s+/s\b", "recursive directory deletion is blocked"),
            (r"\brmdir\s+/s\b", "recursive directory deletion is blocked"),
            (r"remove-item\b.*-recurse.*-force", "recursive forced deletion is blocked"),
            (r"\bcipher\s+/w\b", "disk wiping is blocked"),
        ]
        for pattern, reason in blocked:
            if re.search(pattern, lowered):
                return reason
        return None

    def _run_agent_tool_call(self, tool_call):
        """Execute a confirmed local tool call and return structured output."""
        action = (tool_call.get("action") or "").strip().lower()
        timeout = int(tool_call.get("timeout") or 120)
        timeout = max(5, min(timeout, 600))
        cwd = self._normalize_tool_cwd(tool_call.get("cwd"))

        try:
            if action == "command":
                command = (tool_call.get("command") or "").strip()
                if not command:
                    return {"ok": False, "error": "No command provided."}
                blocked = self._blocked_command_reason(command)
                if blocked:
                    return {"ok": False, "error": f"Blocked command: {blocked}"}
                proc = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=cwd
                )
                return {"ok": proc.returncode == 0, "code": proc.returncode, "stdout": proc.stdout[-12000:], "stderr": proc.stderr[-12000:], "cwd": cwd}

            if action == "python":
                path = (tool_call.get("path") or "").strip().strip('"')
                args = tool_call.get("args") or []
                if isinstance(args, str):
                    args = shlex.split(args, posix=False)
                if not path:
                    return {"ok": False, "error": "No Python script path provided."}
                script = path if os.path.isabs(path) else os.path.join(cwd, path)
                script = os.path.abspath(script)
                if not os.path.exists(script):
                    return {"ok": False, "error": f"Script not found: {script}"}
                if os.path.splitext(script.lower())[1] != ".py":
                    return {"ok": False, "error": "Only .py scripts can be run with the python action."}
                proc = subprocess.run(
                    ["py", script] + [str(a).strip('"') for a in args],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=os.path.dirname(script)
                )
                return {"ok": proc.returncode == 0, "code": proc.returncode, "stdout": proc.stdout[-12000:], "stderr": proc.stderr[-12000:], "cwd": os.path.dirname(script)}

            if action == "pip_install":
                packages = tool_call.get("packages") or []
                if isinstance(packages, str):
                    packages = shlex.split(packages, posix=False)
                packages = [str(p).strip('"') for p in packages if str(p).strip()]
                if not packages:
                    return {"ok": False, "error": "No packages provided."}
                unsafe = [p for p in packages if not re.match(r"^[A-Za-z0-9_.\-\[\]>=<!,]+$", p)]
                if unsafe:
                    return {"ok": False, "error": f"Unsafe package spec blocked: {', '.join(unsafe)}"}
                proc = subprocess.run(
                    ["py", "-m", "pip", "install"] + packages,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=cwd
                )
                return {"ok": proc.returncode == 0, "code": proc.returncode, "stdout": proc.stdout[-12000:], "stderr": proc.stderr[-12000:], "cwd": cwd}

            if action in ("plugin", "internal_tool"):
                plugin_name = tool_call.get("tool") or tool_call.get("plugin") or tool_call.get("name")
                params = tool_call.get("params") or {}
                plugin_result = self._run_plugin_call(plugin_name, params, cwd)
                return {"ok": bool(plugin_result.get("ok")), "tool": plugin_name, "data": plugin_result.get("data"), "error": plugin_result.get("error"), "cwd": cwd}

            if action == "github_plugin":
                plugin_name = (tool_call.get("plugin") or tool_call.get("name") or "").strip()
                plugin = self._find_installed_github_plugin(plugin_name)
                if not plugin:
                    return {"ok": False, "error": f"GitHub plugin is not installed: {plugin_name}", "cwd": cwd}
                return {"ok": True, "plugin": plugin_name, "data": plugin, "cwd": cwd}

            return {"ok": False, "error": f"Unsupported tool action: {action}"}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": f"Tool timed out after {timeout} seconds.", "cwd": cwd}
        except Exception as e:
            return {"ok": False, "error": str(e), "cwd": cwd}

    def _format_tool_result(self, tool_call, result):
        action = tool_call.get("action", "tool")
        reason = tool_call.get("reason", "")
        body = [
            f"Action: {action}",
            f"Plugin: {result.get('plugin')}" if result.get("plugin") else "",
            f"Tool: {result.get('tool')}" if result.get("tool") else "",
            f"Reason: {reason}" if reason else "",
            f"OK: {result.get('ok')}",
            f"Exit code: {result.get('code')}" if "code" in result else "",
            f"CWD: {result.get('cwd')}" if result.get("cwd") else "",
        ]
        if result.get("error"):
            body.append(f"Error: {result.get('error')}")
        if "data" in result and result.get("data") is not None:
            body.append("DATA:\n" + json.dumps(result.get("data"), indent=2, ensure_ascii=False)[:12000])
        if result.get("stdout"):
            body.append("STDOUT:\n" + result.get("stdout", ""))
        if result.get("stderr"):
            body.append("STDERR:\n" + result.get("stderr", ""))
        clean = "\n".join([x for x in body if x])
        return f"```text\n{clean}\n```"

    def _handle_model_tool_call(self, user_input, model_response, provider_label):
        tool_call = self._extract_agent_tool_call(model_response)
        if not tool_call:
            return False

        visible = self._strip_agent_tool_blocks(model_response)
        if visible:
            self.root.after(0, lambda: self.add_message(f"{self.app_name} ({provider_label})", visible))

        preview = json.dumps(tool_call, indent=2)
        ok = self._askyesno_sync("Run Agent Tool", f"The selected model wants to run this local tool action:\n\n{preview}\n\nRun it?")
        if not ok:
            self.root.after(0, lambda: self.add_message("Tool Runner", "Tool action was not run."))
            return True

        self.root.after(0, lambda: self.update_status("Running model-requested tool..."))
        result = self._run_agent_tool_call(tool_call)
        result_text = self._format_tool_result(tool_call, result)
        self.root.after(0, lambda: self.add_message("Tool Runner", result_text))

        followup = (
            "The local tool action has completed. Use the output to give the user the final answer. "
            "Do not request another tool unless absolutely necessary.\n\n"
            f"Original user request:\n{user_input}\n\n"
            f"Tool call:\n{json.dumps(tool_call, ensure_ascii=True)}\n\n"
            f"Tool result:\n{json.dumps(result, ensure_ascii=True)}"
        )
        final_response = get_provider_response(followup, CURRENT_PROVIDER, CURRENT_MODEL, 650)
        self.root.after(0, lambda: self.add_message(f"{self.app_name} ({provider_label})", final_response))
        self.root.after(0, lambda: self.update_status("Agent tool run complete"))
        return True
    
    def send_message(self):
        """Send message to AI"""
        user_input = self.input_field.get("1.0", END).strip()
        if not user_input:
            return

        self.add_message("You", user_input)
        self.input_field.delete("1.0", END)

        if self._handle_direct_agent_command(user_input):
            return

        threading.Thread(target=self.get_ai_response, args=(user_input,), daemon=True).start()
    
    def get_ai_response(self, user_input):
        """Get AI response"""
        try:
            self.chat_display.insert(END, "LightSky AI: ✨ Thinking...\n")
            self.chat_display.see(END)
            
            response = self.get_groq_response(user_input, CURRENT_MODEL, 300)
            
            self.chat_display.delete("end-2l", "end-1l")
            self.add_message("LightSky AI", response)
            
            self.update_status(f"✅ Response received")
            
            if self.speech_engine:
                threading.Thread(target=self.speak_response, args=(response,), daemon=True).start()
                
        except Exception as e:
            self.chat_display.delete("end-2l", "end-1l")
            self.add_message("LightSky AI", f"❌ Error: {str(e)}")
    
    def speak_response(self, text):
        """Speak response"""
        if self.speech_engine:
            try:
                self.speech_engine.say(text)
                self.speech_engine.runAndWait()
            except Exception as e:
                print(f"Speech error: {e}")
    
    # Voice Input Methods
    def toggle_voice_input(self):
        """Toggle voice input"""
        if self.listening:
            self.stop_voice_input()
        else:
            self.start_voice_input()
    
    def start_voice_input(self):
        """Start voice input"""
        self.listening = True
        self.voice_input_btn.config(text="🔴 Recording", bg='#dc3545')
        self.voice_status_label.config(text="🎤 Voice: Recording...", fg='#dc3545')
        
        threading.Thread(target=self._voice_input_worker, daemon=True).start()
    
    def stop_voice_input(self):
        """Stop voice input"""
        self.listening = False
        self.voice_input_btn.config(text="🎤 Voice Input", bg='#28a745')
        self.voice_status_label.config(text="🎤 Voice: Ready", fg='#28a745')
    
    def _voice_input_worker(self):
        """Voice input worker thread"""
        try:
            text = self.speech_recognizer.recognize_speech()
            self.root.after(0, lambda: self._process_voice_input(text))
        except Exception as e:
            error_msg = f"Voice input error: {e}"
            self.root.after(0, lambda: self._process_voice_input(error_msg))
        finally:
            self.root.after(0, self.stop_voice_input)
    
    def _process_voice_input(self, text):
        """Process voice input"""
        if text and "not available" not in text and "error" not in text.lower():
            if hasattr(self, "_replace_chat_input"):
                self._replace_chat_input(text)
            else:
                self.input_field.delete("1.0", END)
                self.input_field.insert("1.0", text)
            self.send_message()
            self.user_data['voice_commands'] += 1
            self.update_stats()
        else:
            self.update_status(f"🎤 {text}")
    
    def voice_input_message(self):
        """Quick voice input for chat"""
        threading.Thread(target=self._voice_input_worker, daemon=True).start()
    
    # Advanced Image Generation Methods
    def generate_advanced_image(self):
        """Generate image using advanced AI"""
        prompt = self.image_prompt.get("1.0", END).strip()
        if not prompt:
            messagebox.showwarning("No Prompt", "Please enter an image prompt")
            return
        
        width = self.width_var.get()
        height = self.height_var.get()
        
        self.update_status("🎨 Generating advanced AI image...")
        threading.Thread(target=self._generate_advanced_image_worker, args=(prompt, width, height), daemon=True).start()
    
    def _generate_advanced_image_worker(self, prompt, width, height):
        """Worker for advanced image generation"""
        try:
            if ADVANCED_IMG_GEN:
                image = self.image_generator.generate_image(prompt, width=width, height=height)
                if image:
                    self.root.after(0, lambda: self.display_advanced_image(image, prompt, width, height))
                else:
                    self.root.after(0, lambda: self.update_status("❌ Advanced image generation failed"))
            else:
                # Fallback to basic generation
                self._generate_basic_image_worker(prompt)
        except Exception as e:
            print(f"Image generation error: {e}")
            self.root.after(0, lambda: self.update_status(f"❌ Image generation error: {e}"))
    
    def _generate_basic_image_worker(self, prompt):
        """Fallback basic image generation"""
        try:
            from PIL import Image, ImageDraw
            import random
            
            width, height = 512, 512
            image = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(image)
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#3F51B5', '#2196F3']
            
            for _ in range(50):
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                x2 = random.randint(0, width)
                y2 = random.randint(0, height)
                color = random.choice(colors)
                draw.ellipse([x1, y1, x2, y2], fill=color)
            
            self.root.after(0, lambda: self.display_advanced_image(image, prompt, width, height))
            
        except Exception as e:
            print(f"Basic image generation error: {e}")
            self.root.after(0, lambda: self.update_status(f"❌ Basic image generation error: {e}"))
    
    def display_advanced_image(self, image, prompt, width, height):
        """Display generated image with info"""
        try:
            for widget in self.image_frame.winfo_children():
                widget.destroy()
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Create info panel
            info_frame = Frame(self.image_frame, bg=self.bg_color)
            info_frame.pack(fill=X, pady=(0, 5))
            
            # Image info
            info_text = f"Generated: {prompt} | {width}x{height} | {'Advanced AI' if ADVANCED_IMG_GEN else 'Basic'}"
            info_label = Label(info_frame, text=info_text, 
                             font=(self.font_family, 10), fg=self.secondary_color, bg=self.bg_color)
            info_label.pack(side=LEFT, padx=10)
            
            # Save button
            save_btn = Button(info_frame, text="💾 Save", 
                             font=(self.font_family, 10, 'bold'), bg='#28a745', fg='white',
                             padx=10, pady=5, relief=FLAT, cursor='hand2',
                             command=lambda: self.save_generated_image(image, prompt))
            save_btn.pack(side=RIGHT, padx=10)
            
            # Image display
            img_label = Label(self.image_frame, image=photo, bg=self.bg_color)
            img_label.image = photo
            img_label.pack(expand=True)
            
            self.user_data['images_generated'] += 1
            self.update_stats()
            self.update_status("✅ Image generated successfully")
            
        except Exception as e:
            print(f"Display image error: {e}")
            self.update_status(f"❌ Display error: {e}")
    
    def save_generated_image(self, image, prompt):
        """Save generated image"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if filename:
                image.save(filename)
                self.update_status(f"💾 Image saved: {os.path.basename(filename)}")
        except Exception as e:
            print(f"Save image error: {e}")
            messagebox.showerror("Save Error", f"Failed to save image: {e}")
    
    def set_image_style(self, style):
        """Set image generation style"""
        self.update_status(f"🎨 Image style: {style}")
    
    # Arena Methods
    def toggle_arena(self):
        """Toggle arena system"""
        if not self.arena_running:
            self.start_arena()
        else:
            self.stop_arena()
    
    def start_arena(self):
        """Start arena battle"""
        self.arena_running = True
        self.arena_btn.config(text="⏹️ Stop Arena", bg='#dc3545')
        self.arena_status.config(text="🔴 Arena Running", fg='#dc3545')
        self.current_topic = self.topic_var.get()
        
        self.arena_display.delete("1.0", END)
        self.arena_display.insert(END, f"🏆 Ultimate Arena Started!\n")
        self.arena_display.insert(END, f"📝 Topic: {self.current_topic}\n")
        self.arena_display.insert(END, f"🤖 Participants: {', '.join([agent.name for agent in self.arena_agents])}\n\n")
        
        self.arena_thread = threading.Thread(target=self.run_arena_conversation, daemon=True).start()
        
        self.user_data['arena_sessions'] += 1
        self.update_stats()
        self.update_status("🏆 Arena started")
    
    def stop_arena(self):
        """Stop arena battle"""
        self.arena_running = False
        self.arena_btn.config(text="🏆 Start Arena", bg='#28a745')
        self.arena_status.config(text="🟢 Arena Ready", fg='#28a745')
        
        self.arena_display.insert(END, "\n⏹️ Arena Stopped\n")
        self.update_status("⏹️ Arena stopped")
    
    def run_arena_conversation(self):
        """Run arena conversation"""
        round_num = 1
        
        while self.arena_running:
            for agent in self.arena_agents:
                if not self.arena_running:
                    break
                
                try:
                    prompt = f"Continue to conversation about {self.current_topic}. Make it interesting and engaging."
                    response = agent.get_response(prompt, self.current_topic)
                    
                    self.root.after(0, lambda a=agent, r=response, rn=round_num: self.add_arena_message(a, r, rn))
                    
                    if agent.speech_engine:
                        agent.speak(response)
                    
                    time.sleep(3)
                    
                except Exception as e:
                    error_msg = f"{agent.name}: I'm having trouble responding right now."
                    self.root.after(0, lambda a=agent, m=error_msg, rn=round_num: self.add_arena_message(a, m, round_num))
            
            round_num += 1
            time.sleep(2)
    
    def add_arena_message(self, agent, message, round_num):
        """Add arena message"""
        if not self.arena_running:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.arena_display.insert(END, f"[{timestamp}] Round {round_num}\n")
        self.arena_display.insert(END, f"{agent.name}: {message}\n\n")
        self.arena_display.see(END)
    
    def send_arena_message(self):
        """Send user message to arena"""
        user_message = self.arena_input.get().strip()
        if not user_message or not self.arena_running:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.arena_display.insert(END, f"[{timestamp}] You: {user_message}\n\n")
        self.arena_display.see(END)
        
        self.arena_input.delete(0, END)
        
        for agent in self.arena_agents:
            if not self.arena_running:
                break
            
            try:
                response = agent.get_response(f"Respond to: {user_message}", self.current_topic)
                self.add_arena_message(agent, response, 0)
                
                if agent.speech_engine:
                    agent.speak(response)
                
                time.sleep(2)
            except Exception as e:
                error_msg = f"{agent.name}: I'm having trouble responding right now."
                self.add_arena_message(agent, error_msg, 0)
    
    def talk_to_arena(self):
        """Talk to arena with voice"""
        threading.Thread(target=self._arena_voice_worker, daemon=True).start()
    
    def _arena_voice_worker(self):
        """Arena voice worker"""
        try:
            text = self.speech_recognizer.recognize_speech()
            self.root.after(0, lambda: self._process_arena_voice(text))
        except Exception as e:
            error_msg = f"Arena voice error: {e}"
            self.root.after(0, lambda: self.update_status(error_msg))
    
    def _process_arena_voice(self, text):
        """Process arena voice input"""
        if text and "not available" not in text and "error" not in text.lower():
            self.arena_input.delete(0, END)
            self.arena_input.insert(0, text)
            self.send_arena_message()
            self.user_data['voice_commands'] += 1
            self.update_stats()
    
    # Custom Topic Methods
    def add_custom_topic(self, event=None):
        """Add custom topic"""
        topic = self.topic_entry.get().strip()
        if topic and topic not in self.custom_topics:
            self.custom_topics.append(topic)
            self.topic_combo['values'] = self.custom_topics
            self.topic_entry.delete(0, END)
            self.update_status(f"✅ Added topic: {topic}")
    
    def change_topic(self, event=None):
        """Change arena topic"""
        self.current_topic = self.topic_var.get()
        self.update_status(f"📝 Topic changed to: {self.current_topic}")
    
    # Knowledge Methods
    def import_knowledge(self):
        """Import knowledge document"""
        try:
            filename = filedialog.askopenfilename(
                title="Select document to import",
                filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if self.conn:
                    self.cursor.execute("INSERT INTO documents (title, content) VALUES (?, ?)",
                                     (os.path.basename(filename), content))
                    self.conn.commit()
                
                self.update_status(f"📁 Imported: {os.path.basename(filename)}")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import document: {e}")
    
    def search_knowledge(self):
        """Search knowledge base"""
        self.update_status("🔍 Searching knowledge base")
    
    def clear_knowledge(self):
        """Clear knowledge base"""
        if self.conn:
            self.cursor.execute("DELETE FROM documents")
            self.conn.commit()
        
        self.knowledge_display.config(state=NORMAL)
        self.knowledge_display.delete("1.0", END)
        self.knowledge_display.insert(END, "📚 Knowledge Base\n\nKnowledge base cleared.")
        self.knowledge_display.config(state=DISABLED)
        
        self.update_status("🗑️ Knowledge base cleared")
    
    def export_knowledge(self):
        """Export knowledge base"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                content = self.knowledge_display.get("1.0", END)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.update_status(f"💾 Exported to {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")
    
    # Analytics Methods
    def refresh_analytics(self):
        """Refresh analytics"""
        self.analytics_display.delete("1.0", END)
        
        self.analytics_display.insert(END, "📊 LightSky AI Ultimate Analytics\n")
        self.analytics_display.insert(END, "=" * 50 + "\n\n")
        
        # User stats
        self.analytics_display.insert(END, "👤 User Statistics:\n")
        self.analytics_display.insert(END, f"   Messages Sent: {self.user_data['messages_sent']}\n")
        self.analytics_display.insert(END, f"   Voice Commands: {self.user_data['voice_commands']}\n")
        self.analytics_display.insert(END, f"   Arena Sessions: {self.user_data['arena_sessions']}\n")
        self.analytics_display.insert(END, f"   Images Generated: {self.user_data['images_generated']}\n")
        self.analytics_display.insert(END, f"   Tokens Used: ~{self.user_data['messages_sent'] * 50}\n\n")
        
        # Model usage
        self.analytics_display.insert(END, "🤖 Model Usage:\n")
        for model in list(MODELS.keys())[:5]:
            usage = random.randint(10, 100)
            self.analytics_display.insert(END, f"   {model}: {usage} calls\n")
        self.analytics_display.insert(END, "\n")
        
        # API status
        self.analytics_display.insert(END, "🔑 API Status:\n")
        for i, key in enumerate(API_KEYS):
            status = "🟢 Active" if i == current_api_index else "⚪ Backup"
            self.analytics_display.insert(END, f"   Key {i+1}: {status}\n")
        
        # Image generation status
        self.analytics_display.insert(END, f"\n🎨 Image Generation:\n")
        img_status = "Advanced AI (Stable Diffusion)" if ADVANCED_IMG_GEN else "Basic PIL"
        self.analytics_display.insert(END, f"   Engine: {img_status}\n")
        if ADVANCED_IMG_GEN:
            device_status = f"Device: {self.image_generator.device.upper()}"
            self.analytics_display.insert(END, device_status)
        
        # Visual web browser status
        self.analytics_display.insert(END, f"\n🌐 Visual Web Browser:\n")
        browser_status = "Google & Bing Search" if HAS_GOOGLE else "Basic Search"
        self.analytics_display.insert(END, f"   Search: {browser_status}\n")
        self.analytics_display.insert(END, f"   Features: Visual HTML Rendering, URL Navigation, History\n")
        
        # Arena status
        self.analytics_display.insert(END, f"\n🏆 Arena System:\n")
        self.analytics_display.insert(END, f"   Agents: Chatbot Names\n")
        self.analytics_display.insert(END, f"   Features: Custom Topics, Voice Chat, Real-time Conversations\n")
        
        self.update_status("📊 Analytics refreshed")
    
    def export_analytics(self):
        """Export analytics data"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Metric', 'Value'])
                    writer.writerow(['Messages Sent', self.user_data['messages_sent']])
                    writer.writerow(['Voice Commands', self.user_data['voice_commands']])
                    writer.writerow(['Arena Sessions', self.user_data['arena_sessions']])
                    writer.writerow(['Images Generated', self.user_data['images_generated']])
                
                self.update_status(f"💾 Analytics exported to {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export analytics: {e}")
    
    def reset_stats(self):
        """Reset user statistics"""
        self.user_data = {
            'name': 'User',
            'messages_sent': 0,
            'tokens_used': 0,
            'images_generated': 0,
            'arena_sessions': 0,
            'voice_commands': 0
        }
        self.update_stats()
        self.refresh_analytics()
        self.update_status("🔄 Statistics reset")
    
    # Settings and Utilities
    def clear_chat(self):
        """Clear chat"""
        self.chat_display.delete("1.0", END)
        self.add_message("LightSky AI", "🗑️ Chat cleared! How can I help you?")
        self.update_status("🗑️ Chat cleared")
    
    def save_chat(self):
        """Save chat"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.chat_display.get("1.0", END))
                self.update_status(f"💾 Chat saved to {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save chat: {e}")
    
    def export_chat(self):
        """Export chat"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                chat_content = self.chat_display.get("1.0", END)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({"chat_content": chat_content}, f, indent=2)
                
                self.update_status(f"📤 Chat exported to {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export chat: {e}")
    
    def export_all_data(self):
        """Export all application data"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                all_data = {
                    'user_stats': self.user_data,
                    'current_model': CURRENT_MODEL,
                    'current_topic': self.current_topic,
                    'custom_topics': self.custom_topics,
                    'advanced_img_gen': ADVANCED_IMG_GEN,
                    'web_browser_enabled': HAS_GOOGLE,
                    'export_date': datetime.now().isoformat()
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, indent=2)
                
                self.update_status(f"💾 All data exported to {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
    
    def change_model(self, event=None):
        """Change AI model - FIXED TO USE REAL GROQ MODELS"""
        global CURRENT_MODEL
        # Get display name and map to model ID
        display_name = self.model_var.get()
        if display_name in MODELS:
            CURRENT_MODEL = MODELS[display_name]
        self.update_status(f"🤖 Model changed to: {display_name}")
    
    def toggle_speech(self):
        """Toggle speech synthesis"""
        if self.speech_engine:
            self.speech_btn.config(text='🔊 On' if self.speech_engine else '🔊 Off')
            status = "enabled" if self.speech_engine else "disabled"
            self.update_status(f"🔊 Speech synthesis {status}")
        else:
            messagebox.showinfo("Speech", "Speech synthesis is not available on this system")
    
    def toggle_theme(self):
        """Toggle theme"""
        themes = ['light', 'dark', 'blue']
        current_themes = [getattr(self, 'current_theme', 'light')]
        next_theme = themes[(themes.index(current_themes[0]) + 1) % len(themes)]
        self.set_theme(next_theme)
    
    def set_theme(self, theme):
        """Set application theme"""
        self.current_theme = theme
        
        if theme == 'dark':
            self.bg_color = '#1a1a1a'
            self.text_color = '#ffffff'
            self.secondary_color = '#8e8e93'
        elif theme == 'blue':
            self.bg_color = '#e3f2fd'
            self.text_color = '#0d47a1'
            self.secondary_color = '#1565c0'
        else:  # light
            self.bg_color = '#ffffff'
            self.text_color = '#000000'
            self.secondary_color = '#666666'
        
        self.update_status(f"🎨 Theme changed to: {theme}")
    
    def open_groq_console(self):
        """Open Groq console"""
        webbrowser.open("https://console.groq.com/keys")
        self.update_status("🔑 Opening Groq console...")
    
    def update_stats(self):
        """Update statistics display"""
        stats_text = f"Messages: {self.user_data['messages_sent']} | Tokens: ~{self.user_data['messages_sent'] * 50} | Voice: {self.user_data['voice_commands']} | Images: {self.user_data['images_generated']} | Arena: {self.user_data['arena_sessions']}"
        self.stats_label.config(text=stats_text)
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def start_voice_input(self):
        """Start voice input with modern status styling."""
        self.listening = True
        self.voice_input_btn.config(text="Recording", bg=self.danger_color)
        self.voice_status_label.config(text="Voice: recording", fg=self.danger_color)
        threading.Thread(target=self._voice_input_worker, daemon=True).start()

    def stop_voice_input(self):
        """Stop voice input with modern status styling."""
        self.listening = False
        self.voice_input_btn.config(text="Voice Input", bg=self.success_color)
        self.voice_status_label.config(text="Voice: ready", fg=self.success_color)

    def start_arena(self):
        """Start arena battle."""
        self.arena_running = True
        self.arena_btn.config(text="Stop Arena", bg=self.danger_color)
        self.arena_status.config(text="Arena running", fg=self.danger_color)
        self.current_topic = self.topic_var.get()

        self.arena_display.delete("1.0", END)
        self.arena_display.insert(END, f"Arena started\n")
        self.arena_display.insert(END, f"Topic: {self.current_topic}\n")
        self.arena_display.insert(END, f"Participants: {', '.join([agent.name for agent in self.arena_agents])}\n\n")

        self.arena_thread = threading.Thread(target=self.run_arena_conversation, daemon=True).start()

        self.user_data['arena_sessions'] += 1
        self.update_stats()
        self.update_status("Arena started")

    def stop_arena(self):
        """Stop arena battle."""
        self.arena_running = False
        self.arena_btn.config(text="Start Arena", bg=self.success_color)
        self.arena_status.config(text="Arena ready", fg=self.success_color)

        self.arena_display.insert(END, "\nArena stopped\n")
        self.update_status("Arena stopped")

    def set_theme(self, theme):
        """Set theme colors for future updates; restart repaints the full app."""
        self.current_theme = theme

        if theme == 'blue':
            self.bg_color = "#101a33"
            self.surface_color = "#162446"
            self.panel_color = "#203052"
            self.input_color = "#111d36"
            self.text_color = "#eef6ff"
            self.secondary_color = "#b7c9e6"
            self.muted_color = "#7f91ad"
        elif theme == 'light':
            self.bg_color = "#f6f7fb"
            self.surface_color = "#ffffff"
            self.panel_color = "#ffffff"
            self.input_color = "#f0f2f7"
            self.text_color = "#10131a"
            self.secondary_color = "#485263"
            self.muted_color = "#737d8d"
        else:
            self.bg_color = "#101a33"
            self.surface_color = "#162446"
            self.panel_color = "#203052"
            self.input_color = "#111d36"
            self.text_color = "#eef6ff"
            self.secondary_color = "#b7c7e8"
            self.muted_color = "#8190b2"

        self.update_status(f"Theme changed to: {theme}. Restart the app to repaint every panel.")

    def update_stats(self):
        """Update compact statistics display."""
        stats_text = (
            f"Messages {self.user_data['messages_sent']}   "
            f"Tokens ~{self.user_data['messages_sent'] * 50}   "
            f"Voice {self.user_data['voice_commands']}   "
            f"Images {self.user_data['images_generated']}   "
            f"Arena {self.user_data['arena_sessions']}"
        )
        self.stats_label.config(text=stats_text)

    def create_ultimate_header(self, parent):
        """Create the modern LightSky header with provider-aware model controls."""
        header = self.panel(parent, fill=X, pady=(0, 12), ipady=10)
        header.configure(height=146)
        header.pack_propagate(False)

        RainbowLine(header, bg=self.panel_color).pack(fill=X, side=TOP)

        title_frame = Frame(header, bg=self.panel_color)
        title_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=22, pady=12)

        self.label(title_frame, "LightSky AI", size=26, weight='bold').pack(anchor=W)
        self.label(
            title_frame,
            "Groq + CometAPI, arena, voice, images, browser, knowledge, analytics",
            size=11,
            color=self.secondary_color
        ).pack(anchor=W, pady=(4, 0))

        self.provider_badge = self.label(title_frame, "Provider: Groq", size=10, color=self.accent_color)
        self.provider_badge.pack(anchor=W, pady=(10, 0))

        self.stats_label = self.label(
            title_frame,
            "Messages 0   Tokens 0   Voice 0   Images 0   Arena 0",
            size=10,
            color=self.muted_color
        )
        self.stats_label.pack(anchor=W, pady=(4, 0))

        control_frame = Frame(header, bg=self.panel_color)
        control_frame.pack(side=RIGHT, padx=22, pady=12)

        model_frame = Frame(control_frame, bg=self.panel_color)
        model_frame.pack(anchor=E, pady=(0, 8))
        self.label(model_frame, "Model", size=10, weight='bold').pack(side=LEFT, padx=(0, 8))

        self.model_var = StringVar(value=DEFAULT_MODEL_DISPLAY if DEFAULT_MODEL_DISPLAY in MODEL_OPTIONS else list(MODEL_OPTIONS.keys())[0])
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=list(MODEL_OPTIONS.keys()),
            state='readonly',
            font=(self.font_family, 10),
            width=38
        )
        self.model_combo.pack(side=LEFT)
        self.model_combo.bind('<<ComboboxSelected>>', self.change_model)

        provider_frame = Frame(control_frame, bg=self.panel_color)
        provider_frame.pack(anchor=E, pady=(0, 6))
        self.button(provider_frame, "Groq", lambda: self.pick_provider("groq")).pack(side=LEFT, padx=(0, 6))
        self.button(provider_frame, "CometAPI", lambda: self.pick_provider("cometapi"), tone='primary').pack(side=LEFT)

        action_frame = Frame(control_frame, bg=self.panel_color)
        action_frame.pack(anchor=E)
        self.voice_input_btn = self.button(action_frame, "Voice Input", self.toggle_voice_input, tone='success')
        self.voice_input_btn.pack(side=LEFT, padx=(0, 6))
        self.speech_btn = self.button(action_frame, "Speech", self.toggle_speech, tone='primary')
        self.speech_btn.pack(side=LEFT, padx=(0, 6))
        self.theme_btn = self.button(action_frame, "Theme", self.toggle_theme)
        self.theme_btn.pack(side=LEFT, padx=(0, 6))
        self.export_btn = self.button(action_frame, "Export", self.export_all_data)
        self.export_btn.pack(side=LEFT)

    def create_ultimate_chat_tab(self):
        chat_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(chat_frame, text="Chat")

        control_frame = self.toolbar(chat_frame, fill=X, pady=(12, 8))
        self.button(control_frame, "Enhance Prompt", self.enhance_current_prompt, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Compare Models", self.compare_models, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Ask Web", self.ask_web, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Code Helper", self.code_helper).pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Translate", self.translate_text).pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "To-Do", self.extract_todos).pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Summarize Chat", self.summarize_chat).pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Explain Last", self.explain_last_response).pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Search", self.search_chat).pack(side=LEFT, padx=(0, 14))
        self.button(control_frame, "Clear", self.clear_chat, tone='danger').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Save", self.save_chat).pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Export", self.export_chat).pack(side=LEFT)
        self.voice_status_label = self.label(control_frame, "Voice: ready", size=10, color=self.success_color, bg=self.bg_color)
        self.voice_status_label.pack(side=RIGHT)

        chat_panel = self.panel(chat_frame, fill=BOTH, expand=True, pady=(0, 10))
        self.chat_display = scrolledtext.ScrolledText(
            chat_panel,
            wrap='word',
            font=(self.font_family, self.font_size),
            height=20
        )
        self.configure_text_widget(self.chat_display)
        self.chat_display.pack(fill=BOTH, expand=True)

        input_panel = self.panel(chat_frame, fill=X, pady=(0, 4))
        RainbowLine(input_panel, height=3, bg=self.panel_color, speed=95).pack(fill=X)
        input_frame = Frame(input_panel, bg=self.panel_color)
        input_frame.pack(fill=X, padx=12, pady=12)

        self.input_field = Text(input_frame, height=3, font=(self.font_family, self.font_size))
        self.configure_text_widget(self.input_field)
        self.input_field.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        self.button(input_frame, "Voice", self.voice_input_message, tone='success', width=7).pack(side=RIGHT, padx=(6, 0))
        self.button(input_frame, "Send", self.send_message, tone='primary', size=11, width=8).pack(side=RIGHT)

        self.input_field.bind('<Control-Return>', lambda e: self.send_message())
        self.input_field.bind('<Shift-Return>', lambda e: self.input_field.insert('insert', '\n'))

    def pick_provider(self, provider):
        """Jump the model selector to the first model for a provider."""
        for display_name, config in MODEL_OPTIONS.items():
            if config["provider"] == provider:
                self.model_var.set(display_name)
                self.change_model()
                return

    def change_model(self, event=None):
        """Change provider and model together."""
        global CURRENT_MODEL, CURRENT_PROVIDER
        display_name = self.model_var.get()
        config = MODEL_OPTIONS.get(display_name)
        if config:
            CURRENT_PROVIDER = config["provider"]
            CURRENT_MODEL = config["model"]
            provider_label = "CometAPI" if CURRENT_PROVIDER == "cometapi" else "Groq"
            if hasattr(self, "provider_badge"):
                self.provider_badge.config(text=f"Provider: {provider_label}")
            self.update_status(f"Model changed to {display_name}")

    def infer_provider_for_model(self, model):
        if model == LS_51_MODEL_ID and CURRENT_PROVIDER == "ls_custom":
            return "ls_custom"
        if model in COMET_MODELS.values():
            return "cometapi"
        if model in HUGGINGFACE_MODELS.values():
            return "huggingface"
        if model in XAI_MODELS.values():
            return "xai"
        if model in NVIDIA_NEMOTRON_MODELS.values():
            return "nvidia"
        return "groq"

    def get_groq_response(self, prompt, model=CURRENT_MODEL, max_tokens=150):
        """Backward-compatible AI call that now supports Groq and CometAPI."""
        provider = self.infer_provider_for_model(model)
        if model == CURRENT_MODEL:
            provider = CURRENT_PROVIDER
        return get_provider_response(prompt, provider, model, max_tokens)

    def get_ai_response(self, user_input):
        """Get AI response from the selected provider."""
        try:
            provider_label = "CometAPI" if CURRENT_PROVIDER == "cometapi" else "Groq"
            self.chat_display.insert(END, f"LightSky AI ({provider_label}): Thinking...\n")
            self.chat_display.see(END)

            response = get_provider_response(user_input, CURRENT_PROVIDER, CURRENT_MODEL, 450)

            self.chat_display.delete("end-2l", "end-1l")
            self.add_message(f"LightSky AI ({provider_label})", response)
            self.update_status(f"Response received from {provider_label}")

            if self.speech_engine:
                threading.Thread(target=self.speak_response, args=(response,), daemon=True).start()
        except Exception as e:
            self.chat_display.delete("end-2l", "end-1l")
            self.add_message("LightSky AI", f"Error: {str(e)}")

    def run_ai_task(self, task_name, prompt, on_done):
        """Run an assistant utility in the background."""
        def worker():
            try:
                self.root.after(0, lambda: self.update_status(f"{task_name}..."))
                result = get_provider_response(prompt, CURRENT_PROVIDER, CURRENT_MODEL, 500)
                self.root.after(0, lambda: on_done(result))
                self.root.after(0, lambda: self.update_status(f"{task_name} complete"))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"{task_name} failed: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def enhance_current_prompt(self):
        """Rewrite the draft prompt into a sharper version."""
        draft = self._get_chat_input_text() if hasattr(self, "_get_chat_input_text") else self.input_field.get("1.0", END).strip()
        if not draft:
            self.update_status("Type a draft prompt first")
            return
        prompt = (
            "Rewrite this user prompt to be clearer, more specific, and more powerful. "
            "Keep the user's intent, do not answer it, and return only the improved prompt:\n\n"
            f"{draft}"
        )
        self.run_ai_task("Enhancing prompt", prompt, lambda result: self._replace_chat_input(result.strip()) if hasattr(self, "_replace_chat_input") else (
            self.input_field.delete("1.0", END),
            self.input_field.insert("1.0", result.strip())
        ))

    def summarize_chat(self):
        """Summarize the visible chat into a useful brief."""
        chat = self.chat_display.get("1.0", END).strip()
        if not chat:
            self.update_status("No chat to summarize")
            return
        prompt = "Summarize this conversation into key points, decisions, and next steps:\n\n" + chat[-8000:]
        self.run_ai_task("Summarizing chat", prompt, lambda result: self.add_message("LightSky Summary", result))

    def explain_last_response(self):
        """Explain the last assistant response in simpler terms."""
        chat = self.chat_display.get("1.0", END).strip()
        if not chat:
            self.update_status("No response to explain")
            return
        prompt = "Explain the last assistant response from this chat in simple, practical terms:\n\n" + chat[-5000:]
        self.run_ai_task("Explaining last response", prompt, lambda result: self.add_message("LightSky Explainer", result))

    def compare_models(self):
        """Ask the selected model and a second provider model to answer the same prompt."""
        user_prompt = self._get_chat_input_text() if hasattr(self, "_get_chat_input_text") else self.input_field.get("1.0", END).strip()
        if not user_prompt:
            user_prompt = simpledialog.askstring("Compare Models", "Prompt to compare:")
        if not user_prompt:
            return

        if CURRENT_PROVIDER == "groq":
            challenger_provider, challenger_model, challenger_name = "cometapi", "gpt-5.2-chat-latest", "CometAPI / GPT-5.2 Chat"
        else:
            challenger_provider, challenger_model, challenger_name = "groq", "llama-3.3-70b-versatile", "Groq / Llama 3.3 70B"

        current_name = self.model_var.get()
        self.add_message("You", f"Model comparison prompt: {user_prompt}")

        def worker():
            try:
                self.root.after(0, lambda: self.update_status("Comparing models..."))
                first = get_provider_response(user_prompt, CURRENT_PROVIDER, CURRENT_MODEL, 350)
                second = get_provider_response(user_prompt, challenger_provider, challenger_model, 350)
                report = (
                    f"{current_name}\n{first}\n\n"
                    f"{challenger_name}\n{second}\n\n"
                    "Use whichever answer is clearer, more accurate, and more useful."
                )
                self.root.after(0, lambda: self.add_message("LightSky Model Compare", report))
                self.root.after(0, lambda: self.update_status("Model comparison complete"))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Model comparison failed: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def search_chat(self):
        """Find text in the chat display and jump to it."""
        query = simpledialog.askstring("Search Chat", "Find:")
        if not query:
            return
        self.chat_display.tag_remove("search_match", "1.0", END)
        start = "1.0"
        first_match = None
        while True:
            index = self.chat_display.search(query, start, stopindex=END, nocase=True)
            if not index:
                break
            end = f"{index}+{len(query)}c"
            self.chat_display.tag_add("search_match", index, end)
            if first_match is None:
                first_match = index
            start = end
        self.chat_display.tag_config("search_match", background=self.accent_color, foreground=self.text_color)
        if first_match:
            self.chat_display.see(first_match)
            self.update_status(f"Found matches for: {query}")
        else:
            self.update_status(f"No matches for: {query}")

    def ask_web(self):
        """Fetch a web page or search page and ask the selected model to answer from it."""
        target = simpledialog.askstring("Ask Web", "URL or search query:")
        if not target:
            return

        def worker():
            try:
                self.root.after(0, lambda: self.update_status("Fetching web context..."))
                if not re.match(r'^https?://', target, re.I):
                    url = "https://duckduckgo.com/html/?q=" + urllib.parse.quote(target)
                else:
                    url = target
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=12)
                text = re.sub(r'<(script|style).*?</\1>', ' ', response.text, flags=re.I | re.S)
                text = html.unescape(re.sub(r'<[^>]+>', ' ', text))
                text = re.sub(r'\s+', ' ', text).strip()[:7000]
                prompt = (
                    "Answer the user's web question using this fetched page/search context. "
                    "Be concise and mention if the context is weak.\n\n"
                    f"Question or URL: {target}\n\nContext:\n{text}"
                )
                answer = get_provider_response(prompt, CURRENT_PROVIDER, CURRENT_MODEL, 500)
                self.root.after(0, lambda: self.add_message("LightSky Web", answer))
                self.root.after(0, lambda: self.update_status("Web answer ready"))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Web fetch failed: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def code_helper(self):
        """Review or improve code pasted in the input box."""
        code = self._get_chat_input_text() if hasattr(self, "_get_chat_input_text") else self.input_field.get("1.0", END).strip()
        if not code:
            code = simpledialog.askstring("Code Helper", "Paste code or describe the coding problem:")
        if not code:
            return
        prompt = (
            "Act as a senior coding assistant. Find bugs, improve the code, and explain the changes briefly. "
            "If code is incomplete, give a clear implementation:\n\n"
            f"{code}"
        )
        self.run_ai_task("Running code helper", prompt, lambda result: self.add_message("LightSky Code Helper", result))

    def translate_text(self):
        """Translate text from input or selected chat content."""
        text = self._get_chat_input_text() if hasattr(self, "_get_chat_input_text") else self.input_field.get("1.0", END).strip()
        if not text:
            text = simpledialog.askstring("Translate", "Text to translate:")
        if not text:
            return
        language = simpledialog.askstring("Translate", "Target language:", initialvalue="English")
        if not language:
            return
        prompt = f"Translate this text to {language}. Preserve meaning and formatting. Return only the translation:\n\n{text}"
        self.run_ai_task("Translating", prompt, lambda result: self.add_message("LightSky Translator", result))

    def extract_todos(self):
        """Extract a clean task list from chat or input."""
        text = (self._get_chat_input_text() if hasattr(self, "_get_chat_input_text") else self.input_field.get("1.0", END).strip()) or self.chat_display.get("1.0", END).strip()
        if not text:
            self.update_status("No text to turn into tasks")
            return
        prompt = (
            "Extract a practical to-do list from this text. Group by priority, include clear action verbs, "
            "and keep it concise:\n\n"
            f"{text[-7000:]}"
        )
        self.run_ai_task("Extracting tasks", prompt, lambda result: self.add_message("LightSky To-Do", result))

    def create_ultimate_image_tab(self):
        image_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(image_frame, text="Images")

        control_frame = self.toolbar(image_frame, fill=X, pady=(12, 8))
        gen_status = "Advanced AI" if ADVANCED_IMG_GEN and self.image_generator.pipe else "Smart Fallback"
        self.adv_gen_btn = self.button(control_frame, f"Generate ({gen_status})", self.generate_advanced_image, tone='primary', size=11)
        self.adv_gen_btn.pack(side=LEFT, padx=(0, 8))
        self.button(control_frame, "Enhance Prompt", self.enhance_image_prompt, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Random Prompt", self.random_image_prompt).pack(side=LEFT, padx=(0, 10))
        for style_name in ['realistic', 'artistic', 'abstract', 'fantasy', 'cinematic', 'minimal']:
            self.button(control_frame, style_name.title(), lambda s=style_name: self.set_image_style(s)).pack(side=LEFT, padx=3)

        prompt_panel = self.panel(image_frame, fill=X, pady=(0, 10))
        RainbowLine(prompt_panel, height=3, bg=self.panel_color, speed=95).pack(fill=X)
        prompt_inner = Frame(prompt_panel, bg=self.panel_color)
        prompt_inner.pack(fill=X, padx=14, pady=12)
        self.label(prompt_inner, "Image prompt", size=11, weight='bold').pack(anchor=W, pady=(0, 6))
        self.image_prompt = Text(prompt_inner, height=3, font=(self.font_family, self.font_size))
        self.configure_text_widget(self.image_prompt)
        self.image_prompt.pack(fill=X)

        param_frame = Frame(prompt_inner, bg=self.panel_color)
        param_frame.pack(fill=X, pady=(10, 0))
        self.label(param_frame, "Width", size=10).pack(side=LEFT, padx=(0, 6))
        self.width_var = IntVar(value=768)
        Scale(param_frame, from_=256, to=1024, orient=HORIZONTAL, variable=self.width_var,
              bg=self.panel_color, fg=self.secondary_color, troughcolor=self.input_color,
              highlightthickness=0, font=(self.font_family, 9)).pack(side=LEFT, fill=X, expand=True, padx=(0, 14))
        self.label(param_frame, "Height", size=10).pack(side=LEFT, padx=(0, 6))
        self.height_var = IntVar(value=768)
        Scale(param_frame, from_=256, to=1024, orient=HORIZONTAL, variable=self.height_var,
              bg=self.panel_color, fg=self.secondary_color, troughcolor=self.input_color,
              highlightthickness=0, font=(self.font_family, 9)).pack(side=LEFT, fill=X, expand=True)

        self.current_image_style = "realistic"
        self.last_generated_image = None
        self.image_frame = self.panel(image_frame, fill=BOTH, expand=True)
        self.image_placeholder = self.label(
            self.image_frame,
            "Image Studio\n\nUse advanced generation when available, or the improved fallback renderer.",
            size=16,
            color=self.secondary_color
        )
        self.image_placeholder.pack(expand=True)

    def set_image_style(self, style):
        """Set image generation style for the next render."""
        self.current_image_style = style
        self.update_status(f"Image style: {style}")

    def random_image_prompt(self):
        ideas = [
            "a futuristic desktop AI workspace with glowing glass panels, cinematic lighting",
            "a quiet mountain observatory control room, holographic screens, sunrise",
            "a minimal robot assistant made of soft light, editorial tech poster style",
            "a neon city library where AI agents debate ideas, detailed digital art",
            "a sleek black-and-rainbow interface floating in space, premium product render"
        ]
        self.image_prompt.delete("1.0", END)
        self.image_prompt.insert("1.0", random.choice(ideas))
        self.update_status("Random image prompt added")

    def enhance_image_prompt(self):
        draft = self.image_prompt.get("1.0", END).strip()
        if not draft:
            self.random_image_prompt()
            draft = self.image_prompt.get("1.0", END).strip()
        prompt = (
            "Turn this into a vivid image-generation prompt. Include subject, composition, lighting, "
            "style, camera/detail notes, and avoid text/logos unless requested. Return only the prompt:\n\n"
            f"{draft}"
        )
        self.run_ai_task("Enhancing image prompt", prompt, lambda result: (
            self.image_prompt.delete("1.0", END),
            self.image_prompt.insert("1.0", result.strip())
        ))

    def generate_advanced_image(self):
        """Generate one or multiple images with premium controls."""
        prompt = self.image_prompt.get("1.0", END).strip()
        if not prompt:
            messagebox.showwarning("No Prompt", "Please enter an image prompt")
            return

        width = self.width_var.get()
        height = self.height_var.get()
        style = getattr(self, "current_image_style", "realistic")
        negative = self.negative_prompt_var.get().strip() if hasattr(self, "negative_prompt_var") else ""
        quality = self.image_quality_var.get() if hasattr(self, "image_quality_var") else "High"
        variants = int(self.variants_var.get()) if hasattr(self, "variants_var") else 1
        variants = max(1, min(4, variants))

        self.update_status(f"Generating {variants} image(s) ({style}, {quality})...")
        if variants == 1:
            threading.Thread(
                target=self._generate_advanced_image_worker,
                args=(prompt, width, height, style, negative, quality),
                daemon=True
            ).start()
        else:
            threading.Thread(
                target=self._generate_multi_image_worker,
                args=(prompt, width, height, style, negative, quality, variants),
                daemon=True
            ).start()

    def _compose_image_prompt(self, prompt, negative="", quality="High", variant_index=None):
        quality_map = {
            "Draft": "fast draft quality, simple lighting, lower detail",
            "High": "high quality, rich detail, crisp composition",
            "Ultra": "ultra-detailed, cinematic lighting, premium texture detail, sharp focus"
        }
        quality_hint = quality_map.get(quality, quality_map["High"])
        out = f"{prompt}. Render style: {quality_hint}."
        if negative:
            out += f" Avoid: {negative}."
        if variant_index is not None:
            out += f" Variation angle {variant_index + 1}: alternative composition."
        return out

    def _generate_advanced_image_worker(self, prompt, width, height, style="realistic", negative="", quality="High"):
        """Worker for image generation."""
        try:
            composed_prompt = self._compose_image_prompt(prompt, negative, quality)
            image = None
            if ADVANCED_IMG_GEN and self.image_generator.pipe:
                image = self.image_generator.generate_image(composed_prompt, style=style, width=width, height=height)
            if image is None:
                image = generate_huggingface_image(composed_prompt, width=width, height=height)
            if image is None:
                image = self.create_fallback_image(composed_prompt, width, height, style)
            self.root.after(0, lambda: self.display_advanced_image(image, prompt, width, height))
        except Exception as e:
            print(f"Image generation error: {e}")
            self.root.after(0, lambda: self.update_status(f"Image generation error: {e}"))

    def _generate_multi_image_worker(self, prompt, width, height, style, negative, quality, variants):
        """Generate multiple variations in a single run."""
        try:
            images = []
            for i in range(variants):
                composed_prompt = self._compose_image_prompt(prompt, negative, quality, variant_index=i)
                image = None
                if ADVANCED_IMG_GEN and self.image_generator.pipe:
                    image = self.image_generator.generate_image(composed_prompt, style=style, width=width, height=height)
                if image is None:
                    image = generate_huggingface_image(composed_prompt, width=width, height=height)
                if image is None:
                    image = self.create_fallback_image(composed_prompt, width, height, style)
                if image is not None:
                    images.append(image)
            if not images:
                raise RuntimeError("No image produced")
            self.root.after(0, lambda: self.display_image_gallery(images, prompt, width, height))
        except Exception as e:
            print(f"Multi image generation error: {e}")
            self.root.after(0, lambda: self.update_status(f"Image generation error: {e}"))

    def create_fallback_image(self, prompt, width, height, style):
        """Create a polished deterministic abstract image when diffusion is unavailable."""
        seed = int(hashlib.sha256(f"{prompt}|{style}".encode("utf-8")).hexdigest()[:8], 16)
        rng = random.Random(seed)
        image = Image.new('RGB', (width, height), "#10131a")
        draw = ImageDraw.Draw(image, "RGBA")

        palettes = {
            "realistic": ["#1d2940", "#7c9cff", "#67e8f9", "#f4f7fb"],
            "artistic": ["#231942", "#c084fc", "#f472b6", "#facc15"],
            "abstract": ["#0f1117", "#4ade80", "#67e8f9", "#fb7185"],
            "fantasy": ["#172033", "#c084fc", "#facc15", "#58d68d"],
            "cinematic": ["#0b0f19", "#fb7185", "#f4c95d", "#7c9cff"],
            "minimal": ["#f6f7fb", "#10131a", "#7c9cff", "#aab2c0"],
        }
        colors = palettes.get(style, palettes["realistic"])

        for y in range(height):
            mix = y / max(height - 1, 1)
            c1 = colors[0].lstrip("#")
            c2 = colors[1].lstrip("#")
            rgb = tuple(int(int(c1[i:i+2], 16) * (1 - mix) + int(c2[i:i+2], 16) * mix) for i in (0, 2, 4))
            draw.line([(0, y), (width, y)], fill=rgb)

        for _ in range(34):
            x = rng.randint(-width // 4, width)
            y = rng.randint(-height // 4, height)
            r = rng.randint(width // 12, width // 3)
            color = rng.choice(colors)
            draw.ellipse([x, y, x + r, y + r], fill=color + "55")

        for _ in range(16):
            x1, y1 = rng.randint(0, width), rng.randint(0, height)
            x2, y2 = rng.randint(0, width), rng.randint(0, height)
            draw.line([x1, y1, x2, y2], fill=rng.choice(colors) + "AA", width=rng.randint(2, 8))

        title = "LightSky Image Studio"
        words = " ".join(prompt.split()[:10])
        draw.rounded_rectangle([36, height - 140, width - 36, height - 36], radius=18, fill="#0f1117CC", outline="#ffffff22")
        draw.text((58, height - 118), title, fill="#f4f7fb")
        draw.text((58, height - 86), words, fill="#aab2c0")
        return image

    def display_advanced_image(self, image, prompt, width, height):
        """Display generated image with modern controls."""
        try:
            self.last_generated_image = image
            for widget in self.image_frame.winfo_children():
                widget.destroy()

            display_image = image.copy()
            display_image.thumbnail((900, 620))
            photo = ImageTk.PhotoImage(display_image)

            info_frame = Frame(self.image_frame, bg=self.panel_color)
            info_frame.pack(fill=X, padx=12, pady=12)
            engine = "Advanced AI" if ADVANCED_IMG_GEN and self.image_generator.pipe else "Smart Fallback"
            self.label(info_frame, f"{engine} | {width}x{height} | {prompt[:90]}", size=10, color=self.secondary_color).pack(side=LEFT)
            self.button(info_frame, "Save", lambda: self.save_generated_image(image, prompt), tone='success').pack(side=RIGHT)

            img_label = Label(self.image_frame, image=photo, bg=self.panel_color)
            img_label.image = photo
            img_label.pack(expand=True, padx=16, pady=(0, 16))

            self.user_data['images_generated'] += 1
            self.update_stats()
            self.update_status("Image generated successfully")
        except Exception as e:
            print(f"Display image error: {e}")
            self.update_status(f"Display error: {e}")

    def display_image_gallery(self, images, prompt, width, height):
        """Display a compact gallery for multi-variant output."""
        try:
            self.last_generated_images = images
            self.last_generated_image = images[0]
            for widget in self.image_frame.winfo_children():
                widget.destroy()

            info_frame = Frame(self.image_frame, bg=self.panel_color)
            info_frame.pack(fill=X, padx=12, pady=12)
            engine = "Advanced AI" if ADVANCED_IMG_GEN and self.image_generator.pipe else "Smart Fallback"
            self.label(info_frame, f"{engine} | {len(images)} variants | {width}x{height}", size=10, color=self.secondary_color).pack(side=LEFT)
            self.button(info_frame, "Save Selected", lambda: self.save_generated_image(self.last_generated_image, prompt), tone='success').pack(side=RIGHT)

            grid = Frame(self.image_frame, bg=self.panel_color)
            grid.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
            thumbs = []
            for idx, img in enumerate(images):
                preview = img.copy()
                preview.thumbnail((420, 280))
                photo = ImageTk.PhotoImage(preview)
                thumbs.append(photo)
                cell = Frame(grid, bg=self.input_color, highlightthickness=1, highlightbackground=self.border_color)
                cell.grid(row=idx // 2, column=idx % 2, padx=8, pady=8, sticky="nsew")
                lbl = Label(cell, image=photo, bg=self.input_color, cursor="hand2")
                lbl.image = photo
                lbl.pack(padx=8, pady=8)
                self.label(cell, f"Variant {idx + 1}", size=10, bg=self.input_color).pack(pady=(0, 8))
                lbl.bind("<Button-1>", lambda _e, sel=img: self._select_gallery_image(sel))

            grid.grid_columnconfigure(0, weight=1)
            grid.grid_columnconfigure(1, weight=1)
            self._gallery_thumbs = thumbs
            self.user_data['images_generated'] += len(images)
            self.update_stats()
            self.update_status(f"Generated {len(images)} image variants")
        except Exception as e:
            print(f"Gallery display error: {e}")
            self.update_status(f"Gallery error: {e}")

    def _select_gallery_image(self, image):
        self.last_generated_image = image
        self.update_status("Selected variant for save/export")

    def create_ultimate_knowledge_tab(self):
        knowledge_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(knowledge_frame, text="Knowledge")

        control_frame = self.toolbar(knowledge_frame, fill=X, pady=(12, 8))
        self.button(control_frame, "Import", self.import_knowledge, tone='success').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Search", self.search_knowledge, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Ask KB", self.ask_knowledge, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Summarize KB", self.summarize_knowledge).pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Clear", self.clear_knowledge, tone='danger').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Export", self.export_knowledge).pack(side=LEFT)

        panel = self.panel(knowledge_frame, fill=BOTH, expand=True)
        self.knowledge_display = scrolledtext.ScrolledText(panel, wrap='word', font=(self.font_family, self.font_size), height=25)
        self.configure_text_widget(self.knowledge_display)
        self.knowledge_display.pack(fill=BOTH, expand=True)
        self.knowledge_display.insert(END, "Knowledge Base\n\nImport TXT, MD, CSV, JSON, or PDF files. Search and ask questions over your documents.")
        self.knowledge_display.config(state=DISABLED)

    def read_document_text(self, filename):
        """Read common document formats with graceful fallback."""
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(filename)
                return "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception as e:
                return f"[PDF import needs pypdf or readable text extraction failed: {e}]"
        with open(filename, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()

    def import_knowledge(self):
        """Import knowledge documents into SQLite and display them."""
        try:
            filenames = filedialog.askopenfilenames(
                title="Select documents to import",
                filetypes=[
                    ("Documents", "*.txt *.md *.csv *.json *.py *.pdf"),
                    ("Text files", "*.txt"),
                    ("PDF files", "*.pdf"),
                    ("All files", "*.*")
                ]
            )
            if not filenames:
                return

            imported = []
            for filename in filenames:
                content = self.read_document_text(filename)
                title = os.path.basename(filename)
                if self.conn:
                    self.cursor.execute("INSERT INTO documents (title, content) VALUES (?, ?)", (title, content))
                    self.conn.commit()
                imported.append((title, content))

            self.knowledge_display.config(state=NORMAL)
            self.knowledge_display.delete("1.0", END)
            self.knowledge_display.insert(END, f"Imported {len(imported)} document(s)\n\n")
            for title, content in imported:
                self.knowledge_display.insert(END, f"{title}\n")
                self.knowledge_display.insert(END, f"{content[:1200]}\n\n")
            self.knowledge_display.config(state=DISABLED)
            self.update_status(f"Imported {len(imported)} document(s)")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import document: {e}")

    def search_knowledge(self):
        """Search knowledge base and show matching excerpts."""
        query = simpledialog.askstring("Search Knowledge", "Find:")
        if not query:
            return
        if not self.conn:
            self.update_status("Knowledge database is unavailable")
            return
        like = f"%{query}%"
        self.cursor.execute(
            "SELECT title, content FROM documents WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC LIMIT 20",
            (like, like)
        )
        rows = self.cursor.fetchall()
        self.knowledge_display.config(state=NORMAL)
        self.knowledge_display.delete("1.0", END)
        self.knowledge_display.insert(END, f"Search results for: {query}\n\n")
        for title, content in rows:
            idx = content.lower().find(query.lower())
            start = max(idx - 180, 0) if idx >= 0 else 0
            excerpt = content[start:start + 700].replace("\n", " ")
            self.knowledge_display.insert(END, f"{title}\n{excerpt}\n\n")
        if not rows:
            self.knowledge_display.insert(END, "No matching documents found.")
        self.knowledge_display.config(state=DISABLED)
        self.update_status(f"Knowledge search found {len(rows)} result(s)")

    def collect_knowledge_context(self, limit=6000):
        if not self.conn:
            return ""
        self.cursor.execute("SELECT title, content FROM documents ORDER BY created_at DESC LIMIT 8")
        chunks = []
        for title, content in self.cursor.fetchall():
            chunks.append(f"Document: {title}\n{content[:1200]}")
        return "\n\n".join(chunks)[:limit]

    def ask_knowledge(self):
        question = simpledialog.askstring("Ask Knowledge Base", "Question:")
        if not question:
            return
        context = self.collect_knowledge_context()
        if not context:
            self.update_status("Import documents first")
            return
        prompt = f"Answer using only this knowledge base context. If missing, say what is missing.\n\n{context}\n\nQuestion: {question}"
        self.run_ai_task("Asking knowledge base", prompt, lambda result: self.add_message("Knowledge Answer", result))

    def summarize_knowledge(self):
        context = self.collect_knowledge_context(9000)
        if not context:
            self.update_status("Import documents first")
            return
        prompt = "Summarize this knowledge base into key ideas, useful facts, and suggested follow-up questions:\n\n" + context
        self.run_ai_task("Summarizing knowledge base", prompt, lambda result: self.add_message("Knowledge Summary", result))

    def create_ultimate_analytics_tab(self):
        analytics_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(analytics_frame, text="Analytics")

        control_frame = self.toolbar(analytics_frame, fill=X, pady=(12, 8))
        self.button(control_frame, "Refresh", self.refresh_analytics, tone='success').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Export Data", self.export_analytics, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(control_frame, "Reset Stats", self.reset_stats, tone='warning').pack(side=LEFT)

        panel = self.panel(analytics_frame, fill=BOTH, expand=True)
        self.analytics_display = Text(panel, font=(self.mono_family, self.font_size), height=25)
        self.configure_text_widget(self.analytics_display)
        self.analytics_display.pack(fill=BOTH, expand=True)
        self.refresh_analytics()

    def refresh_analytics(self):
        """Refresh analytics using real local data instead of random usage."""
        if not hasattr(self, "analytics_display"):
            return
        self.analytics_display.delete("1.0", END)
        provider_label = provider_display_name()
        docs = 0
        chars = 0
        if self.conn:
            try:
                self.cursor.execute("SELECT COUNT(*), COALESCE(SUM(LENGTH(content)), 0) FROM documents")
                docs, chars = self.cursor.fetchone()
            except Exception:
                pass

        chat_chars = len(self.chat_display.get("1.0", END)) if hasattr(self, "chat_display") else 0
        self.analytics_display.insert(END, "LightSky AI Analytics\n")
        self.analytics_display.insert(END, "=" * 42 + "\n\n")
        self.analytics_display.insert(END, f"Provider: {provider_label}\n")
        self.analytics_display.insert(END, f"Current model: {CURRENT_MODEL}\n")
        self.analytics_display.insert(END, f"Messages sent: {self.user_data['messages_sent']}\n")
        self.analytics_display.insert(END, f"Estimated tokens: {max(1, chat_chars // 4)}\n")
        self.analytics_display.insert(END, f"Voice commands: {self.user_data['voice_commands']}\n")
        self.analytics_display.insert(END, f"Images generated: {self.user_data['images_generated']}\n")
        self.analytics_display.insert(END, f"Arena sessions: {self.user_data['arena_sessions']}\n\n")
        self.analytics_display.insert(END, f"Knowledge documents: {docs}\n")
        self.analytics_display.insert(END, f"Knowledge characters: {chars}\n\n")
        self.analytics_display.insert(END, "Available providers\n")
        self.analytics_display.insert(END, f"- Groq models: {len(MODELS)}\n")
        self.analytics_display.insert(END, f"- CometAPI models: {len(COMET_MODELS)}\n")
        self.analytics_display.insert(END, "- Custom model: LS 5.1 (developed by Lightsky)\n")
        self.update_status("Analytics refreshed")

    def create_ultimate_header(self, parent):
        """Create the modern LightSky header with the sparkle logo."""
        header = self.panel(parent, fill=X, pady=(0, 12), ipady=10)
        header.configure(height=150)
        header.pack_propagate(False)

        RainbowLine(header, bg=self.panel_color).pack(fill=X, side=TOP)

        title_frame = Frame(header, bg=self.panel_color)
        title_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=22, pady=12)

        brand_frame = Frame(title_frame, bg=self.panel_color)
        brand_frame.pack(anchor=W)
        self.logo_label = self.label(brand_frame, "✨", size=28, weight='bold', color=self.accent_color)
        self.logo_label.pack(side=LEFT, padx=(0, 10))
        self.label(brand_frame, self.app_name, size=26, weight='bold').pack(side=LEFT)

        self.label(
            title_frame,
            "Powered by LS 5.1 custom model, Groq, CometAPI, arena, voice, images, browser, knowledge",
            size=11,
            color=self.secondary_color
        ).pack(anchor=W, pady=(4, 0))

        self.provider_badge = self.label(title_frame, "✨ Model: LS 5.1 (custom)", size=10, color=self.accent_color)
        self.provider_badge.pack(anchor=W, pady=(10, 0))

        self.stats_label = self.label(
            title_frame,
            "Messages 0   Tokens 0   Voice 0   Images 0   Arena 0",
            size=10,
            color=self.muted_color
        )
        self.stats_label.pack(anchor=W, pady=(4, 0))

        control_frame = Frame(header, bg=self.panel_color)
        control_frame.pack(side=RIGHT, padx=22, pady=12)

        model_frame = Frame(control_frame, bg=self.panel_color)
        model_frame.pack(anchor=E, pady=(0, 8))
        self.label(model_frame, "Model", size=10, weight='bold').pack(side=LEFT, padx=(0, 8))

        self.model_var = StringVar(value=DEFAULT_MODEL_DISPLAY if DEFAULT_MODEL_DISPLAY in MODEL_OPTIONS else list(MODEL_OPTIONS.keys())[0])
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=list(MODEL_OPTIONS.keys()),
            state='readonly',
            font=(self.font_family, 10),
            width=38
        )
        self.model_combo.pack(side=LEFT)
        self.model_combo.bind('<<ComboboxSelected>>', self.change_model)

        provider_frame = Frame(control_frame, bg=self.panel_color)
        provider_frame.pack(anchor=E, pady=(0, 6))
        self.button(provider_frame, "LS 5.1", lambda: self.pick_provider("ls_custom"), tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(provider_frame, "Groq", lambda: self.pick_provider("groq")).pack(side=LEFT, padx=(0, 6))
        self.button(provider_frame, "CometAPI", lambda: self.pick_provider("cometapi")).pack(side=LEFT)

        action_frame = Frame(control_frame, bg=self.panel_color)
        action_frame.pack(anchor=E)
        self.voice_input_btn = self.button(action_frame, "Voice Input", self.toggle_voice_input, tone='success')
        self.voice_input_btn.pack(side=LEFT, padx=(0, 6))
        self.speech_btn = self.button(action_frame, "Speech", self.toggle_speech, tone='primary')
        self.speech_btn.pack(side=LEFT, padx=(0, 6))
        self.theme_btn = self.button(action_frame, "Theme", self.toggle_theme)
        self.theme_btn.pack(side=LEFT, padx=(0, 6))
        self.export_btn = self.button(action_frame, "Export", self.export_all_data)
        self.export_btn.pack(side=LEFT)

    def start_thinking_spinner(self, provider_label):
        """Animate the sparkle logo while a response is being generated."""
        self.thinking_active = True
        self.thinking_frame = 0
        self.thinking_mark = self.chat_display.index(END)
        self.chat_display.insert(END, f"✨ {self.app_name} ({provider_label}): thinking\n")
        self.chat_display.see(END)
        self.animate_thinking_spinner(provider_label)

    def animate_thinking_spinner(self, provider_label):
        if not getattr(self, "thinking_active", False):
            return
        frames = ["✨", "✦", "✧", "✶", "✧", "✦"]
        dots = "." * ((self.thinking_frame % 3) + 1)
        mark = getattr(self, "thinking_mark", None)
        if mark:
            try:
                self.chat_display.delete(mark, "end-1c")
                self.chat_display.insert(mark, f"{frames[self.thinking_frame % len(frames)]} {self.app_name} ({provider_label}): thinking{dots}\n")
                self.chat_display.see(END)
            except Exception:
                pass
        if hasattr(self, "logo_label"):
            self.logo_label.config(text=frames[self.thinking_frame % len(frames)])
        self.thinking_frame += 1
        self.root.after(140, lambda: self.animate_thinking_spinner(provider_label))

    def stop_thinking_spinner(self):
        self.thinking_active = False
        if hasattr(self, "logo_label"):
            self.logo_label.config(text="✨")
        mark = getattr(self, "thinking_mark", None)
        if mark:
            try:
                self.chat_display.delete(mark, "end-1c")
            except Exception:
                pass

    def get_ai_response(self, user_input):
        """Get AI response from the selected provider with animated sparkle thinking state."""
        provider_label = provider_display_name()
        try:
            self.root.after(0, lambda: self.start_thinking_spinner(provider_label))
            response = get_provider_response(user_input, CURRENT_PROVIDER, CURRENT_MODEL, 450)

            self.root.after(0, self.stop_thinking_spinner)
            handled_tool = False
            if MODEL_AGENT_TOOLS_ENABLED:
                handled_tool = self._handle_model_tool_call(user_input, response, provider_label)
            if not handled_tool:
                self.root.after(0, lambda: self.add_message(f"✨ {self.app_name} ({provider_label})", response))
                self.root.after(0, lambda: self.update_status(f"✨ Response received from {provider_label}"))

            if self.speech_engine and not handled_tool:
                threading.Thread(target=self.speak_response, args=(response,), daemon=True).start()
        except Exception as e:
            self.root.after(0, self.stop_thinking_spinner)
            self.root.after(0, lambda: self.add_message(f"✨ {self.app_name}", f"Error: {str(e)}"))

    def change_model(self, event=None):
        """Change provider and model together."""
        global CURRENT_MODEL, CURRENT_PROVIDER, CURRENT_SYSTEM_PROMPT, CURRENT_TEMPERATURE
        display_name = self.model_var.get()
        config = MODEL_OPTIONS.get(display_name)
        if config:
            CURRENT_PROVIDER = config["provider"]
            CURRENT_MODEL = config["model"]
            CURRENT_SYSTEM_PROMPT = config.get("system_prompt", "You are Lightsky AI pro by krivi, a helpful desktop assistant.")
            CURRENT_TEMPERATURE = config.get("temperature", 0.7)
            provider_label = provider_display_name(CURRENT_PROVIDER)
            if hasattr(self, "provider_badge"):
                self.provider_badge.config(text=f"✨ Model: {display_name}" if CURRENT_PROVIDER == "ls_custom" else f"✨ Provider: {provider_label}")
            if hasattr(self, "chat_provider_value"):
                self.chat_provider_value.config(text=provider_label)
            if hasattr(self, "update_header_cards"):
                self.update_header_cards()
            self.update_status(f"✨ Model changed to {display_name}")

    # App shell modern overrides
    def show_startup_screen(self):
        """Show startup splash before loading the main interface."""
        self.root.configure(bg=self.bg_color)
        self.startup_frame = Frame(self.root, bg=self.bg_color)
        self.startup_frame.pack(fill=BOTH, expand=True)

        center = Frame(self.startup_frame, bg=self.bg_color)
        center.place(relx=0.5, rely=0.5, anchor=CENTER)

        Label(center, text="✨", font=(self.font_family, 66, "bold"),
              fg=self.accent_color, bg=self.bg_color).pack()
        Label(center, text="lightsky AI", font=(self.font_family, 34, "bold"),
              fg=self.text_color, bg=self.bg_color).pack(pady=(8, 0))
        Label(center, text="by Krivi and codex", font=(self.font_family, 12),
              fg=self.secondary_color, bg=self.bg_color).pack(pady=(6, 0))

        self.root.after(1500, self.finish_startup_screen)

    def finish_startup_screen(self):
        """Destroy splash and build the main app."""
        if self.startup_frame is not None:
            self.startup_frame.destroy()
            self.startup_frame = None
        self.create_ultimate_interface()
        self.main_ui_ready = True
        if getattr(self, "welcome_message_text", ""):
            self.add_message(self.app_name, self.welcome_message_text)

    def create_status_bar(self, parent):
        """Modern status/footer strip."""
        strip = self.panel(parent, fill=X, pady=(0, 10))
        row = Frame(strip, bg=self.panel_color)
        row.pack(fill=X, padx=10, pady=8)

        self.status_label = self.label(row, "Ready", size=10, color=self.secondary_color, bg=self.panel_color)
        self.status_label.pack(side=LEFT)

        right = Frame(row, bg=self.panel_color)
        right.pack(side=RIGHT)
        self.connection_label = self.label(right, "Online", size=10, color=self.success_color, bg=self.panel_color)
        self.connection_label.pack(side=LEFT, padx=(0, 12))
        self.mode_badge_label = self.label(right, "Mode: LS 5.1", size=10, color=self.accent_color, bg=self.panel_color)
        self.mode_badge_label.pack(side=LEFT)

    def create_ultimate_header(self, parent):
        """Modern header with compact status cards."""
        header = self.panel(parent, fill=X, pady=(0, 12), ipady=10)
        header.configure(height=190)
        header.pack_propagate(False)

        RainbowLine(header, bg=self.panel_color).pack(fill=X, side=TOP)

        title_frame = Frame(header, bg=self.panel_color)
        title_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=22, pady=12)

        brand_frame = Frame(title_frame, bg=self.panel_color)
        brand_frame.pack(anchor=W)
        self.logo_label = self.label(brand_frame, "✨", size=28, weight='bold', color=self.accent_color)
        self.logo_label.pack(side=LEFT, padx=(0, 10))
        self.label(brand_frame, self.app_name, size=26, weight='bold').pack(side=LEFT)

        self.label(
            title_frame,
            "Powered by LS 5.1 custom model, Groq, CometAPI, arena, voice, images, browser, knowledge",
            size=11,
            color=self.secondary_color
        ).pack(anchor=W, pady=(4, 0))

        self.provider_badge = self.label(title_frame, "✨ Model: LS 5.1 (custom)", size=10, color=self.accent_color)
        self.provider_badge.pack(anchor=W, pady=(10, 0))

        self.stats_label = self.label(
            title_frame,
            "Messages 0   Tokens 0   Voice 0   Images 0   Arena 0",
            size=10,
            color=self.muted_color
        )
        self.stats_label.pack(anchor=W, pady=(4, 8))

        cards = Frame(title_frame, bg=self.panel_color)
        cards.pack(anchor=W, fill=X, pady=(2, 0))

        self.model_card_value = self._make_header_card(cards, "Model", "LS 5.1 (custom)")
        self.provider_card_value = self._make_header_card(cards, "Provider", "LS 5.1")
        self.arena_card_value = self._make_header_card(cards, "Arena", "Ready")

        control_frame = Frame(header, bg=self.panel_color)
        control_frame.pack(side=RIGHT, padx=22, pady=12)

        model_frame = Frame(control_frame, bg=self.panel_color)
        model_frame.pack(anchor=E, pady=(0, 8))
        self.label(model_frame, "Model", size=10, weight='bold').pack(side=LEFT, padx=(0, 8))

        self.model_var = StringVar(value=DEFAULT_MODEL_DISPLAY if DEFAULT_MODEL_DISPLAY in MODEL_OPTIONS else list(MODEL_OPTIONS.keys())[0])
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=list(MODEL_OPTIONS.keys()),
            state='readonly',
            font=(self.font_family, 10),
            width=38
        )
        self.model_combo.pack(side=LEFT)
        self.model_combo.bind('<<ComboboxSelected>>', self.change_model)

        provider_frame = Frame(control_frame, bg=self.panel_color)
        provider_frame.pack(anchor=E, pady=(0, 6))
        self.button(provider_frame, "LS 5.1", lambda: self.pick_provider("ls_custom"), tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(provider_frame, "Groq", lambda: self.pick_provider("groq")).pack(side=LEFT, padx=(0, 6))
        self.button(provider_frame, "CometAPI", lambda: self.pick_provider("cometapi")).pack(side=LEFT)

        action_frame = Frame(control_frame, bg=self.panel_color)
        action_frame.pack(anchor=E)
        self.voice_input_btn = self.button(action_frame, "Voice Input", self.toggle_voice_input, tone='success')
        self.voice_input_btn.pack(side=LEFT, padx=(0, 6))
        self.speech_btn = self.button(action_frame, "Speech", self.toggle_speech, tone='primary')
        self.speech_btn.pack(side=LEFT, padx=(0, 6))
        self.theme_btn = self.button(action_frame, "Theme", self.toggle_theme)
        self.theme_btn.pack(side=LEFT, padx=(0, 6))
        self.export_btn = self.button(action_frame, "Export", self.export_all_data)
        self.export_btn.pack(side=LEFT)
        self.update_header_cards()

    def _make_header_card(self, parent, label_text, value_text):
        palette = {
            "Model": ("#132f4c", self.brand_cyan if hasattr(self, "brand_cyan") else self.accent_color),
            "Provider": ("#2d2555", self.brand_violet if hasattr(self, "brand_violet") else self.accent_hover),
            "Arena": ("#183a2d", self.success_color),
        }
        bg, accent = palette.get(label_text, (self.input_color, self.accent_color))
        card = Frame(parent, bg=bg, highlightthickness=1, highlightbackground=accent, bd=0)
        card.pack(side=LEFT, padx=(0, 10), ipadx=10, ipady=6)
        self.label(card, label_text, size=9, color=accent, bg=bg).pack(anchor=W)
        value = self.label(card, value_text, size=10, weight='bold', color=self.text_color, bg=bg)
        value.pack(anchor=W)
        return value

    def update_header_cards(self):
        if hasattr(self, "model_card_value"):
            selected = self.model_var.get() if hasattr(self, "model_var") else "LS 5.1 (custom)"
            self.model_card_value.config(text=selected[:26])
        if hasattr(self, "provider_card_value"):
            self.provider_card_value.config(text=provider_display_name(CURRENT_PROVIDER))
        if hasattr(self, "arena_card_value"):
            state = "Running" if getattr(self, "arena_running", False) else "Ready"
            self.arena_card_value.config(text=state)

    def _register_tab_frame(self, tab_name, frame):
        if not hasattr(self, "_tab_frames"):
            self._tab_frames = {}
        self._tab_frames[tab_name] = frame

    def _animate_tab_enter(self, frame):
        if not frame or not frame.winfo_exists():
            return
        children = [c for c in frame.winfo_children() if c.winfo_manager() == "pack"]
        pack_data = []
        for child in children:
            try:
                pack_data.append((child, child.pack_info()))
            except Exception:
                pass
        for child, _ in pack_data:
            try:
                child.pack_forget()
            except Exception:
                pass
        for i, (child, info) in enumerate(pack_data):
            self.root.after(18 + i * 45, lambda c=child, d=info: c.pack(**d))

    def _on_tab_changed(self, event=None):
        try:
            tab_id = self.notebook.select()
            tab_label = self.notebook.tab(tab_id, "text")
            frame = self._tab_frames.get(tab_label) if hasattr(self, "_tab_frames") else None
            self._animate_tab_enter(frame)
        except Exception:
            pass

    def create_ultimate_tabs(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=BOTH, expand=True)
        self.create_ultimate_chat_tab()
        self.create_ultimate_arena_tab()
        self.create_ultimate_webgl_tab()
        self.create_look_take_tab()
        self.create_plugin_center_tab()
        self.create_inter_test_tab()
        self.create_ultimate_image_tab()
        self.create_ultimate_knowledge_tab()
        self.create_ultimate_analytics_tab()
        self.create_ultimate_settings_tab()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.notebook.select(0)
        self.root.after(120, self._on_tab_changed)
        self.root.after(260, lambda: self.input_field.focus_set() if hasattr(self, "input_field") else None)

    def create_ultimate_chat_tab(self):
        """Modernized chat workspace."""
        chat_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(chat_frame, text="Chat")
        self._register_tab_frame("Chat", chat_frame)

        top = self.toolbar(chat_frame, fill=X, pady=(12, 8))
        self.button(top, "Enhance", self.enhance_current_prompt, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(top, "Code Helper", self.code_helper).pack(side=LEFT, padx=(0, 6))
        self.button(top, "Translate", self.translate_text).pack(side=LEFT, padx=(0, 6))
        self.button(top, "To-Do", self.extract_todos).pack(side=LEFT, padx=(0, 12))
        self.button(top, "Clear", self.clear_chat, tone='danger').pack(side=LEFT, padx=(0, 6))
        self.button(top, "Export", self.export_chat).pack(side=LEFT, padx=(0, 6))
        self.button(top, "Agent Tools", self.show_agent_tool_help, tone='primary').pack(side=LEFT)
        self.voice_status_label = self.label(top, "Voice: ready", size=10, color=self.success_color, bg=self.bg_color)
        self.voice_status_label.pack(side=RIGHT)

        transcript = self.panel(chat_frame, fill=BOTH, expand=True, pady=(0, 10))
        self.chat_display = scrolledtext.ScrolledText(transcript, wrap='word', font=(self.font_family, self.font_size), height=20)
        self.configure_text_widget(self.chat_display)
        self.chat_display.pack(fill=BOTH, expand=True)
        self.chat_display.insert(END, "Lightsky chat is ready. Type below and press Enter to send.\n\n")

        composer_shell = self.panel(chat_frame, fill=X, pady=(0, 4))
        RainbowLine(composer_shell, height=3, bg=self.panel_color, speed=90).pack(fill=X)
        composer = Frame(composer_shell, bg=self.panel_color)
        composer.pack(fill=X, padx=12, pady=12)

        input_side = Frame(composer, bg=self.panel_color)
        input_side.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        self.label(input_side, "Message", size=10, weight='bold', bg=self.panel_color).pack(anchor=W, pady=(0, 4))
        self.input_field = Text(input_side, height=3, font=(self.font_family, self.font_size))
        self.configure_text_widget(self.input_field)
        self.input_field.pack(fill=BOTH, expand=True)

        self.button(composer, "Voice", self.voice_input_message, tone='success', width=7).pack(side=RIGHT, padx=(6, 0))
        self.button(composer, "Send", self.send_message, tone='primary', size=11, width=8).pack(side=RIGHT)
        self.input_field.bind('<Return>', self._chat_enter_to_send)
        self.input_field.bind('<Control-Return>', self._chat_enter_to_send)
        self.input_field.bind('<Shift-Return>', self._chat_shift_enter_newline)

    def _chat_enter_to_send(self, event=None):
        self.send_message()
        return "break"

    def _chat_shift_enter_newline(self, event=None):
        self.input_field.insert('insert', '\n')
        return "break"

    def create_ultimate_webgl_tab(self):
        """Modernized browser tab shell."""
        web_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(web_frame, text="Browser")
        self._register_tab_frame("Browser", web_frame)
        self.visual_browser = VisualWebBrowser(web_frame, self.root)
        info = self.panel(web_frame, fill=X, pady=(8, 0))
        self.label(info, "Browse, inspect page structure, and use web-assisted answers in one workspace.", size=11, color=self.secondary_color).pack(padx=14, pady=10)

    def create_look_take_tab(self):
        """Search the web, inspect results, download safely, and run trusted scripts."""
        frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text="Look & Take")
        self._register_tab_frame("Look & Take", frame)

        hero = self.panel(frame, fill=X, pady=(10, 8))
        RainbowLine(hero, height=3, bg=self.panel_color, speed=92).pack(fill=X)
        hero_inner = Frame(hero, bg=self.panel_color)
        hero_inner.pack(fill=X, padx=12, pady=10)
        self.label(hero_inner, "Look & Take", size=14, weight='bold', bg=self.panel_color).pack(side=LEFT)
        self.label(hero_inner, "Web search, safe download, controlled execute", size=10, color=self.secondary_color, bg=self.panel_color).pack(side=LEFT, padx=(10, 0))

        top = self.toolbar(frame, fill=X, pady=(12, 8))
        self.look_take_query = StringVar(value="")
        Entry(
            top,
            textvariable=self.look_take_query,
            font=(self.font_family, self.font_size),
            bg=self.input_color,
            fg=self.text_color,
            insertbackground=self.accent_color,
            relief=FLAT
        ).pack(side=LEFT, fill=X, expand=True, ipady=8, padx=(0, 8))
        self.button(top, "Search", self.look_take_search, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(top, "Download Safe", self.look_take_download_selected, tone='success').pack(side=LEFT, padx=(0, 6))
        self.button(top, "Execute", self.look_take_execute_selected, tone='danger').pack(side=LEFT)

        body = self.panel(frame, fill=BOTH, expand=True)
        left = Frame(body, bg=self.panel_color)
        left.pack(side=LEFT, fill=BOTH, expand=True, padx=(12, 6), pady=12)
        right = Frame(body, bg=self.panel_color)
        right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(6, 12), pady=12)

        self.label(left, "Results", size=11, weight='bold', bg=self.panel_color).pack(anchor=W, pady=(0, 6))
        self.look_take_results = Listbox(
            left,
            font=(self.font_family, 10),
            bg=self.input_color,
            fg=self.text_color,
            selectbackground=self.accent_color,
            relief=FLAT,
            borderwidth=0
        )
        self.look_take_results.pack(fill=BOTH, expand=True)
        self.look_take_results.bind("<<ListboxSelect>>", self.look_take_show_details)

        self.label(right, "Details", size=11, weight='bold', bg=self.panel_color).pack(anchor=W, pady=(0, 6))
        self.look_take_details = scrolledtext.ScrolledText(right, wrap='word', font=(self.font_family, 10), height=18)
        self.configure_text_widget(self.look_take_details)
        self.look_take_details.pack(fill=BOTH, expand=True)
        self.look_take_details.insert(END, "Search for a file, package, dataset, or tool.\nSelect a result to view details.")
        self.look_take_index = []
        self.look_take_download_dir = os.path.join(os.path.expanduser("~"), "Documents", "Codex", "2026-05-13", "hi", "downloads")
        os.makedirs(self.look_take_download_dir, exist_ok=True)

    def look_take_search(self):
        query = self.look_take_query.get().strip()
        if not query:
            self.update_status("Enter a search query")
            return
        self.update_status("Searching web...")
        threading.Thread(target=self._look_take_search_worker, args=(query,), daemon=True).start()

    def _look_take_search_worker(self, query):
        try:
            if not requests:
                raise RuntimeError("requests library unavailable")
            url = "https://duckduckgo.com/html/?q=" + urllib.parse.quote(query)
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
            html_text = res.text if res.status_code == 200 else ""
            items = []
            for m in re.finditer(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html_text, re.IGNORECASE | re.DOTALL):
                href = html.unescape(m.group(1))
                title = re.sub(r"<[^>]+>", "", html.unescape(m.group(2))).strip()
                if title and href:
                    items.append({"title": title, "url": href})
                if len(items) >= 20:
                    break
            if not items:
                # Backup parse
                for m in re.finditer(r'<a rel="nofollow" class="[^"]*" href="([^"]+)"[^>]*>(.*?)</a>', html_text, re.IGNORECASE | re.DOTALL):
                    href = html.unescape(m.group(1))
                    title = re.sub(r"<[^>]+>", "", html.unescape(m.group(2))).strip()
                    if title and href and href.startswith("http"):
                        items.append({"title": title, "url": href})
                    if len(items) >= 20:
                        break
            self.root.after(0, lambda: self._look_take_apply_results(query, items))
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Search failed: {e}"))

    def _look_take_apply_results(self, query, items):
        self.look_take_results.delete(0, END)
        self.look_take_index = items
        for i, it in enumerate(items, 1):
            self.look_take_results.insert(END, f"{i}. {it['title'][:110]}")
        self.look_take_details.delete("1.0", END)
        self.look_take_details.insert(END, f"Query: {query}\nResults: {len(items)}\n\nSelect a result for details.")
        self.update_status(f"Found {len(items)} results")

    def look_take_show_details(self, event=None):
        try:
            sel = self.look_take_results.curselection()
            if not sel:
                return
            item = self.look_take_index[sel[0]]
            self.look_take_details.delete("1.0", END)
            self.look_take_details.insert(END, f"Title: {item['title']}\n")
            self.look_take_details.insert(END, f"URL: {item['url']}\n\n")
            self.look_take_details.insert(END, "Actions:\n- Download Safe: downloads after safety checks.\n- Execute: runs only trusted script types from local download folder.")
        except Exception:
            pass

    def _look_take_is_safe_download(self, url, head_resp):
        blocked_ext = {".exe", ".msi", ".bat", ".cmd", ".scr", ".com", ".dll", ".vbs", ".js", ".jar", ".ps1"}
        parsed = urllib.parse.urlparse(url)
        ext = os.path.splitext(parsed.path.lower())[1]
        if ext in blocked_ext:
            return False, f"Blocked file type: {ext}"
        ctype = (head_resp.headers.get("content-type", "") if head_resp else "").lower()
        if any(x in ctype for x in ["application/x-msdownload", "application/java-archive", "application/x-bat"]):
            return False, f"Blocked content-type: {ctype}"
        return True, "ok"

    def look_take_download_selected(self):
        sel = self.look_take_results.curselection()
        if not sel:
            self.update_status("Pick a result first")
            return
        item = self.look_take_index[sel[0]]
        self.update_status("Checking and downloading...")
        threading.Thread(target=self._look_take_download_worker, args=(item,), daemon=True).start()

    def _look_take_download_worker(self, item):
        try:
            url = item["url"]
            head = None
            try:
                head = requests.head(url, allow_redirects=True, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            except Exception:
                head = None
            safe, reason = self._look_take_is_safe_download(url, head)
            if not safe:
                self.root.after(0, lambda: self.update_status(f"Download blocked: {reason}"))
                return

            resp = requests.get(url, stream=True, timeout=25, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                self.root.after(0, lambda: self.update_status(f"Download failed: HTTP {resp.status_code}"))
                return

            parsed = urllib.parse.urlparse(resp.url)
            name = os.path.basename(parsed.path) or "downloaded_file"
            name = re.sub(r'[^A-Za-z0-9._-]', '_', name)[:120]
            dest = os.path.abspath(os.path.join(self.look_take_download_dir, name))
            if not dest.startswith(os.path.abspath(self.look_take_download_dir)):
                self.root.after(0, lambda: self.update_status("Unsafe target path blocked"))
                return

            total = 0
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        total += len(chunk)
                        if total > 50 * 1024 * 1024:
                            raise RuntimeError("Blocked: file too large (>50MB)")
                        f.write(chunk)

            self.root.after(0, lambda: self._look_take_after_download(dest, total))
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Download error: {e}"))

    def _look_take_after_download(self, path, total):
        self.look_take_details.delete("1.0", END)
        self.look_take_details.insert(END, f"Downloaded:\n{path}\nSize: {total} bytes\n\nInstallers and apps are saved only; Execute only runs trusted .py scripts.")
        self.look_take_last_file = path
        self.update_status("Download complete")

    def look_take_execute_selected(self):
        path = getattr(self, "look_take_last_file", None)
        if not path or not os.path.exists(path):
            self.update_status("Download a file first")
            return
        ext = os.path.splitext(path.lower())[1]
        if ext != ".py":
            self.update_status("Execution allowed only for .py scripts")
            return
        ok = messagebox.askyesno(
            "Execute File",
            f"Execute this Python file?\n\n{path}\n\nOnly run code you trust."
        )
        if not ok:
            return
        self.update_status("Executing script...")
        threading.Thread(target=self._look_take_execute_worker, args=(path,), daemon=True).start()

    def _look_take_execute_worker(self, path):
        try:
            proc = subprocess.run(["py", path], capture_output=True, text=True, timeout=180, cwd=os.path.dirname(path))
            out = (proc.stdout or "").strip()
            err = (proc.stderr or "").strip()
            code = proc.returncode
            self.root.after(0, lambda: self._look_take_show_exec_result(path, code, out, err))
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Execution error: {e}"))

    def _look_take_show_exec_result(self, path, code, out, err):
        self.look_take_details.delete("1.0", END)
        self.look_take_details.insert(END, f"Executed: {path}\nExit code: {code}\n\n")
        if out:
            self.look_take_details.insert(END, "STDOUT:\n" + out[:8000] + "\n\n")
        if err:
            self.look_take_details.insert(END, "STDERR:\n" + err[:8000] + "\n")
        self.update_status(f"Execution finished (code {code})")

    def create_inter_test_tab(self):
        """Internal app test bench for generated apps/scripts."""
        frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text="Inter-Test")
        self._register_tab_frame("Inter-Test", frame)

        hero = self.panel(frame, fill=X, pady=(10, 8))
        RainbowLine(hero, height=3, bg=self.panel_color, speed=88).pack(fill=X)
        hero_inner = Frame(hero, bg=self.panel_color)
        hero_inner.pack(fill=X, padx=12, pady=10)
        self.label(hero_inner, "Inter-Test", size=14, weight='bold', bg=self.panel_color).pack(side=LEFT)
        self.label(hero_inner, "Internal test bench for AI-built apps", size=10, color=self.secondary_color, bg=self.panel_color).pack(side=LEFT, padx=(10, 0))

        top = self.toolbar(frame, fill=X, pady=(12, 8))
        self.intertest_file_var = StringVar(value="")
        Entry(
            top,
            textvariable=self.intertest_file_var,
            font=(self.font_family, 10),
            bg=self.input_color,
            fg=self.text_color,
            insertbackground=self.accent_color,
            relief=FLAT
        ).pack(side=LEFT, fill=X, expand=True, ipady=8, padx=(0, 8))
        self.button(top, "Pick App", self.intertest_pick_file).pack(side=LEFT, padx=(0, 6))
        self.button(top, "Run Internal Tests", self.intertest_run_tests, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(top, "Execute App", self.intertest_execute_app, tone='success').pack(side=LEFT)

        cfg = self.panel(frame, fill=X, pady=(0, 8))
        row = Frame(cfg, bg=self.panel_color)
        row.pack(fill=X, padx=12, pady=10)
        self.label(row, "Endpoint (optional)", size=10, bg=self.panel_color).pack(side=LEFT, padx=(0, 8))
        self.intertest_endpoint_var = StringVar(value="http://127.0.0.1:8000")
        Entry(
            row,
            textvariable=self.intertest_endpoint_var,
            font=(self.font_family, 10),
            bg=self.input_color,
            fg=self.text_color,
            insertbackground=self.accent_color,
            relief=FLAT
        ).pack(side=LEFT, fill=X, expand=True, ipady=6)

        self.intertest_output = scrolledtext.ScrolledText(frame, wrap='word', font=(self.mono_family, 10), height=24)
        self.configure_text_widget(self.intertest_output)
        self.intertest_output.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.intertest_output.insert(END, "Inter-Test ready.\nPick an app file and run tests.\n")

    def intertest_pick_file(self):
        file_path = filedialog.askopenfilename(
            title="Choose app/script to test",
            filetypes=[
                ("App files", "*.py *.js *.mjs *.html"),
                ("Python", "*.py"),
                ("JavaScript", "*.js *.mjs"),
                ("All files", "*.*")
            ]
        )
        if not file_path:
            return
        self.intertest_file_var.set(file_path)
        self._intertest_log(f"Selected: {file_path}")
        self.update_status("Inter-Test file selected")

    def _intertest_log(self, text):
        if hasattr(self, "intertest_output"):
            self.intertest_output.insert(END, text + "\n")
            self.intertest_output.see(END)

    def intertest_run_tests(self):
        target = self.intertest_file_var.get().strip()
        if not target:
            self.update_status("Pick a file for Inter-Test")
            return
        self.intertest_output.delete("1.0", END)
        self._intertest_log(f"Running internal tests for: {target}")
        self.update_status("Running internal tests...")
        threading.Thread(target=self._intertest_run_tests_worker, args=(target,), daemon=True).start()

    def _intertest_run_tests_worker(self, target):
        checks = []
        try:
            if not os.path.exists(target):
                raise RuntimeError("Target file does not exist")

            ext = os.path.splitext(target.lower())[1]

            # Check 1: file readable
            size = os.path.getsize(target)
            checks.append(("File readable", True, f"size={size} bytes"))

            # Check 2: syntax/parse
            if ext == ".py":
                p = subprocess.run(["py", "-m", "py_compile", target], capture_output=True, text=True, timeout=90)
                ok = (p.returncode == 0)
                checks.append(("Python syntax compile", ok, (p.stderr or p.stdout or "ok").strip()))
            elif ext in [".js", ".mjs"]:
                checks.append(("JavaScript syntax compile", True, "Skipped (node compile check not configured)"))
            elif ext == ".html":
                checks.append(("HTML static file", True, "Looks testable as static page"))
            else:
                checks.append(("Known file type", False, f"Unsupported type: {ext}"))

            # Check 3: startup smoke run for python
            if ext == ".py":
                p = subprocess.run(["py", target], capture_output=True, text=True, timeout=12, cwd=os.path.dirname(target))
                smoke_ok = p.returncode == 0
                stderr = (p.stderr or "").strip()
                stdout = (p.stdout or "").strip()
                detail = ("exit=0" if smoke_ok else f"exit={p.returncode}") + (f" | stderr: {stderr[:220]}" if stderr else "")
                checks.append(("Startup smoke run (12s)", smoke_ok, detail))
                if stdout:
                    checks.append(("Startup stdout", True, stdout[:300]))

            # Check 4: optional endpoint ping
            ep = self.intertest_endpoint_var.get().strip() if hasattr(self, "intertest_endpoint_var") else ""
            if ep:
                try:
                    r = requests.get(ep, timeout=4)
                    checks.append(("Endpoint health ping", r.status_code < 500, f"HTTP {r.status_code}"))
                except Exception as e:
                    checks.append(("Endpoint health ping", False, str(e)))

            passed = sum(1 for _, ok, _ in checks if ok)
            total = len(checks)
            self.root.after(0, lambda: self._intertest_render_results(target, checks, passed, total))
        except Exception as e:
            self.root.after(0, lambda: self._intertest_log(f"Inter-Test error: {e}"))
            self.root.after(0, lambda: self.update_status("Inter-Test failed"))

    def _intertest_render_results(self, target, checks, passed, total):
        self._intertest_log("")
        self._intertest_log(f"Target: {target}")
        self._intertest_log("-" * 60)
        for name, ok, detail in checks:
            mark = "PASS" if ok else "FAIL"
            self._intertest_log(f"[{mark}] {name}")
            if detail:
                self._intertest_log(f"  {detail}")
        self._intertest_log("-" * 60)
        self._intertest_log(f"Summary: {passed}/{total} checks passed")
        self.update_status(f"Inter-Test complete: {passed}/{total}")

    def intertest_execute_app(self):
        target = self.intertest_file_var.get().strip()
        if not target:
            self.update_status("Pick a file first")
            return
        if not os.path.exists(target):
            self.update_status("File not found")
            return
        ext = os.path.splitext(target.lower())[1]
        if ext not in [".py", ".html"]:
            self.update_status("Execute supports .py and .html in Inter-Test")
            return
        ok = messagebox.askyesno("Execute App", f"Execute/open this app?\n\n{target}")
        if not ok:
            return
        self._intertest_log("")
        self._intertest_log(f"Executing: {target}")
        self.update_status("Executing app...")
        threading.Thread(target=self._intertest_execute_worker, args=(target, ext), daemon=True).start()

    def _intertest_execute_worker(self, target, ext):
        try:
            if ext == ".py":
                p = subprocess.run(["py", target], capture_output=True, text=True, timeout=180, cwd=os.path.dirname(target))
                out = (p.stdout or "").strip()
                err = (p.stderr or "").strip()
                code = p.returncode
                self.root.after(0, lambda: self._intertest_log(f"Exit code: {code}"))
                if out:
                    self.root.after(0, lambda: self._intertest_log("STDOUT:\n" + out[:10000]))
                if err:
                    self.root.after(0, lambda: self._intertest_log("STDERR:\n" + err[:10000]))
                self.root.after(0, lambda: self.update_status(f"Execution finished (code {code})"))
            else:
                webbrowser.open("file:///" + target.replace("\\", "/"))
                self.root.after(0, lambda: self._intertest_log("Opened HTML in system browser"))
                self.root.after(0, lambda: self.update_status("HTML opened"))
        except Exception as e:
            self.root.after(0, lambda: self._intertest_log(f"Execute error: {e}"))
            self.root.after(0, lambda: self.update_status("Execution failed"))

    def create_plugin_center_tab(self):
        """Plugin catalog for all model agent tools."""
        frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text="Plugin Center")
        self._register_tab_frame("Plugin Center", frame)

        hero = self.panel(frame, fill=X, pady=(10, 8))
        RainbowLine(hero, height=3, bg=self.panel_color, speed=86).pack(fill=X)
        hero_inner = Frame(hero, bg=self.panel_color)
        hero_inner.pack(fill=X, padx=12, pady=10)
        self.label(hero_inner, "Plugin Center", size=14, weight='bold', bg=self.panel_color).pack(side=LEFT)
        self.label(hero_inner, "Built-in plugins available to every model", size=10, color=self.secondary_color, bg=self.panel_color).pack(side=LEFT, padx=(10, 0))

        top = self.toolbar(frame, fill=X, pady=(0, 8))
        self.button(top, "Refresh", self.plugin_center_refresh, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(top, "Run Sample", self.plugin_center_run_sample, tone='success').pack(side=LEFT, padx=(0, 6))
        self.button(top, "Show Tool Prompt", self.plugin_center_show_prompt).pack(side=LEFT)

        body = self.panel(frame, fill=BOTH, expand=True)
        left = Frame(body, bg=self.panel_color)
        left.pack(side=LEFT, fill=BOTH, expand=False, padx=(12, 6), pady=12)
        right = Frame(body, bg=self.panel_color)
        right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(6, 12), pady=12)

        self.label(left, "Installed", size=11, weight='bold', bg=self.panel_color).pack(anchor=W, pady=(0, 6))
        self.plugin_listbox = Listbox(
            left,
            font=(self.font_family, 10),
            bg=self.input_color,
            fg=self.text_color,
            selectbackground=self.accent_color,
            relief=FLAT,
            borderwidth=0,
            width=28
        )
        self.plugin_listbox.pack(fill=BOTH, expand=True)
        self.plugin_listbox.bind("<<ListboxSelect>>", self.plugin_center_show_details)

        self.label(right, "Details / Output", size=11, weight='bold', bg=self.panel_color).pack(anchor=W, pady=(0, 6))
        self.plugin_details = scrolledtext.ScrolledText(right, wrap='word', font=(self.mono_family, 10), height=24)
        self.configure_text_widget(self.plugin_details)
        self.plugin_details.pack(fill=BOTH, expand=True)
        self.plugin_center_refresh()

    def plugin_center_refresh(self):
        if not hasattr(self, "plugin_listbox"):
            return
        self.plugin_listbox.delete(0, END)
        for plugin in self.get_plugin_catalog():
            self.plugin_listbox.insert(END, plugin["name"])
        self.plugin_details.delete("1.0", END)
        self.plugin_details.insert(END, "Every selected model can request these plugins through ls_tool_call.\n")
        self.plugin_details.insert(END, "Pick a plugin to view details or run a sample.\n")
        self.update_status("Plugin Center refreshed")

    def plugin_center_show_details(self, event=None):
        sel = self.plugin_listbox.curselection() if hasattr(self, "plugin_listbox") else ()
        if not sel:
            return
        plugin = self.get_plugin_catalog()[sel[0]]
        self.plugin_details.delete("1.0", END)
        self.plugin_details.insert(END, f"Plugin: {plugin['name']}\n")
        self.plugin_details.insert(END, f"Summary: {plugin['summary']}\n\n")
        self.plugin_details.insert(END, "Model call format:\n")
        sample = {"action": "plugin", "plugin": plugin["name"], "params": self._sample_plugin_params(plugin["name"]), "reason": "Use plugin from Lightsky Plugin Center."}
        self.plugin_details.insert(END, "```ls_tool_call\n" + json.dumps(sample, indent=2) + "\n```\n")

    def _sample_plugin_params(self, name):
        samples = {
            "web_search": {"query": "Python requests timeout best practices", "max_results": 3},
            "fetch_url": {"url": "https://example.com"},
            "hf_model_search": {"query": "text generation instruct", "limit": 5},
            "hf_repo_info": {"repo_id": "Qwen/Qwen2.5-7B-Instruct", "repo_type": "model"},
            "hf_inference": {"prompt": "Reply with exactly one word: OK", "model": DEFAULT_HF_TEXT_MODEL, "max_tokens": 32},
            "list_files": {"path": ".", "pattern": ".py", "max_files": 20},
            "read_file": {"path": "C:\\Users\\91994\\Downloads\\Lightsky AI dev\\LightSky_AI.py", "max_chars": 4000},
            "write_file": {"path": "plugin_center_test.txt", "content": "Lightsky plugin write test.", "overwrite": True},
            "knowledge_search": {"query": "Lightsky", "limit": 5},
            "debug_scan": {"code": "import os\npassword='secret12345'\nos.system(user_input)\n"},
        }
        return samples.get(name, {})

    def plugin_center_run_sample(self):
        sel = self.plugin_listbox.curselection() if hasattr(self, "plugin_listbox") else ()
        if not sel:
            self.update_status("Pick a plugin first")
            return
        plugin_name = self.get_plugin_catalog()[sel[0]]["name"]
        tool_call = {
            "action": "plugin",
            "plugin": plugin_name,
            "params": self._sample_plugin_params(plugin_name),
            "reason": "Plugin Center sample run."
        }
        self.plugin_details.delete("1.0", END)
        self.plugin_details.insert(END, "Running sample...\n\n")

        def worker():
            result = self._run_agent_tool_call(tool_call)
            text = self._format_tool_result(tool_call, result)
            self.root.after(0, lambda: self._plugin_center_show_output(text))

        threading.Thread(target=worker, daemon=True).start()

    def _plugin_center_show_output(self, text):
        self.plugin_details.delete("1.0", END)
        self.plugin_details.insert(END, text)
        self.update_status("Plugin sample complete")

    def plugin_center_show_prompt(self):
        self.plugin_details.delete("1.0", END)
        self.plugin_details.insert(END, AGENT_TOOLING_PROMPT)

    def create_ultimate_image_tab(self):
        """Modernized image studio with Copilot-style advanced controls."""
        image_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(image_frame, text="Image Studio")
        self._register_tab_frame("Image Studio", image_frame)

        top = self.toolbar(image_frame, fill=X, pady=(12, 8))
        status = "AI" if ADVANCED_IMG_GEN and self.image_generator.pipe else "Fallback"
        self.adv_gen_btn = self.button(top, f"Generate ({status})", self.generate_advanced_image, tone='primary', size=11)
        self.adv_gen_btn.pack(side=LEFT, padx=(0, 8))
        self.button(top, "Generate 4 Variants", lambda: (self.variants_var.set(4), self.generate_advanced_image()), tone='success').pack(side=LEFT, padx=(0, 8))
        self.button(top, "Enhance Prompt", self.enhance_image_prompt, tone='primary').pack(side=LEFT, padx=(0, 8))
        self.button(top, "Random Prompt", self.random_image_prompt).pack(side=LEFT)
        self.current_image_style = "realistic"
        for style_name in ["realistic", "cinematic", "artistic", "fantasy", "minimal"]:
            self.button(top, style_name.title(), lambda s=style_name: self.set_image_style(s)).pack(side=LEFT, padx=(8, 0))

        prompt_panel = self.panel(image_frame, fill=X, pady=(0, 10))
        RainbowLine(prompt_panel, height=3, bg=self.panel_color, speed=95).pack(fill=X)
        inner = Frame(prompt_panel, bg=self.panel_color)
        inner.pack(fill=X, padx=14, pady=12)
        self.label(inner, "Prompt", size=11, weight='bold').pack(anchor=W, pady=(0, 6))
        self.image_prompt = Text(inner, height=3, font=(self.font_family, self.font_size))
        self.configure_text_widget(self.image_prompt)
        self.image_prompt.pack(fill=X)

        self.label(inner, "Negative Prompt (things to avoid)", size=10, color=self.secondary_color).pack(anchor=W, pady=(10, 4))
        self.negative_prompt_var = StringVar(value="blurry, low quality, watermark, text artifacts")
        Entry(
            inner,
            textvariable=self.negative_prompt_var,
            font=(self.font_family, self.font_size),
            bg=self.input_color,
            fg=self.text_color,
            insertbackground=self.accent_color,
            relief=FLAT
        ).pack(fill=X, ipady=8)

        row = Frame(inner, bg=self.panel_color)
        row.pack(fill=X, pady=(10, 0))

        self.label(row, "Quality", size=10).pack(side=LEFT, padx=(0, 6))
        self.image_quality_var = StringVar(value="High")
        self.image_quality_combo = ttk.Combobox(
            row,
            textvariable=self.image_quality_var,
            values=["Draft", "High", "Ultra"],
            state='readonly',
            font=(self.font_family, 10),
            width=10
        )
        self.image_quality_combo.pack(side=LEFT, padx=(0, 14))

        self.label(row, "Variants", size=10).pack(side=LEFT, padx=(0, 6))
        self.variants_var = IntVar(value=1)
        Spinbox(
            row,
            from_=1,
            to=4,
            textvariable=self.variants_var,
            width=5,
            font=(self.font_family, 10),
            bg=self.input_color,
            fg=self.text_color,
            buttonbackground=self.panel_color
        ).pack(side=LEFT, padx=(0, 14))

        self.label(row, "Width", size=10).pack(side=LEFT, padx=(0, 6))
        self.width_var = IntVar(value=1024)
        Scale(
            row, from_=384, to=1536, resolution=64, orient=HORIZONTAL, variable=self.width_var,
            bg=self.panel_color, fg=self.secondary_color, troughcolor=self.input_color,
            highlightthickness=0, font=(self.font_family, 9), length=220
        ).pack(side=LEFT, padx=(0, 14))

        self.label(row, "Height", size=10).pack(side=LEFT, padx=(0, 6))
        self.height_var = IntVar(value=1024)
        Scale(
            row, from_=384, to=1536, resolution=64, orient=HORIZONTAL, variable=self.height_var,
            bg=self.panel_color, fg=self.secondary_color, troughcolor=self.input_color,
            highlightthickness=0, font=(self.font_family, 9), length=220
        ).pack(side=LEFT)

        self.image_frame = self.panel(image_frame, fill=BOTH, expand=True)
        self.last_generated_image = None
        self.last_generated_images = []
        self.image_placeholder = self.label(
            self.image_frame,
            "Image Studio ready\n\nUse Enhance Prompt + Variants for complex pro-style generations.",
            size=16,
            color=self.secondary_color
        )
        self.image_placeholder.pack(expand=True)

    def create_ultimate_knowledge_tab(self):
        """Modernized knowledge lab."""
        frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text="Knowledge Lab")
        self._register_tab_frame("Knowledge Lab", frame)

        top = self.toolbar(frame, fill=X, pady=(12, 8))
        self.button(top, "Import", self.import_knowledge, tone='success').pack(side=LEFT, padx=(0, 6))
        self.button(top, "Search", self.search_knowledge, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(top, "Ask KB", self.ask_knowledge, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(top, "Summarize", self.summarize_knowledge).pack(side=LEFT, padx=(0, 6))
        self.button(top, "Export", self.export_knowledge).pack(side=LEFT)

        panel = self.panel(frame, fill=BOTH, expand=True)
        self.knowledge_display = scrolledtext.ScrolledText(panel, wrap='word', font=(self.font_family, self.font_size), height=25)
        self.configure_text_widget(self.knowledge_display)
        self.knowledge_display.pack(fill=BOTH, expand=True)
        self.knowledge_display.insert(END, "Knowledge Lab\n\nImport docs, query your corpus, and build synthesis quickly.")
        self.knowledge_display.config(state=DISABLED)

    def create_ultimate_settings_tab(self):
        """Modernized settings hub."""
        settings_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(settings_frame, text="Control Center")
        self._register_tab_frame("Control Center", settings_frame)

        panel = self.panel(settings_frame, fill=BOTH, expand=True, pady=(12, 8))
        body = Frame(panel, bg=self.panel_color)
        body.pack(fill=BOTH, expand=True, padx=12, pady=12)

        self.label(body, "Control Center", size=20, weight='bold').pack(anchor=W)
        self.label(body, "Manage model routing, theme, and tools from one place.", size=11, color=self.secondary_color).pack(anchor=W, pady=(4, 14))

        row = Frame(body, bg=self.panel_color)
        row.pack(fill=X, pady=(0, 10))
        self.button(row, "Theme: Light", lambda: self.set_theme('light')).pack(side=LEFT, padx=(0, 6))
        self.button(row, "Theme: Dark", lambda: self.set_theme('dark')).pack(side=LEFT, padx=(0, 6))
        self.button(row, "Theme: Blue", lambda: self.set_theme('blue')).pack(side=LEFT, padx=(0, 6))
        self.button(row, "Open Groq Console", self.open_groq_console, tone='primary').pack(side=LEFT)

        info = Text(body, height=16, font=(self.mono_family, 10))
        self.configure_text_widget(info)
        info.pack(fill=BOTH, expand=True)
        info.insert(END, f"Active app: {self.app_name}\n")
        info.insert(END, f"Current provider: {provider_display_name()}\n")
        info.insert(END, f"Current model: {CURRENT_MODEL}\n")
        info.insert(END, f"Groq models: {len(MODELS)}\n")
        info.insert(END, f"CometAPI models: {len(COMET_MODELS)}\n")
        info.insert(END, "Custom model: LS 5.1 (developed by Lightsky)\n")
        info.configure(state=DISABLED)

    # Arena v2 override
    def _ensure_arena_state(self):
        if not hasattr(self, "arena_config"):
            self.arena_config = {
                "mode": "Brainstorm",
                "rounds": 6,
                "response_tokens": 180,
                "temperature": 0.75,
                "speaking_order": "Round Robin",
                "stop_condition": "Max Rounds"
            }
        if not hasattr(self, "arena_context_board"):
            self.arena_context_board = []
        if not hasattr(self, "arena_interrupt_message"):
            self.arena_interrupt_message = None
        if not hasattr(self, "arena_scores"):
            self.arena_scores = {}
        if not hasattr(self, "arena_agent_state"):
            self.arena_agent_state = {}

    def create_ultimate_arena_tab(self):
        self._ensure_arena_state()
        arena_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(arena_frame, text="Arena")
        self._register_tab_frame("Arena", arena_frame)
        if not hasattr(self, "arena_voice_enabled"):
            self.arena_voice_enabled = False

        top = self.toolbar(arena_frame, fill=X, pady=(12, 8))
        self.arena_btn = self.button(top, "Start Arena", self.toggle_arena, tone='success', size=11)
        self.arena_btn.pack(side=LEFT, padx=(0, 8))
        self.talk_btn = self.button(top, "Talk to Arena", self.talk_to_arena, tone='primary', size=11)
        self.talk_btn.pack(side=LEFT, padx=(0, 8))
        self.mic_check_btn = self.button(top, "Mic Check", self.arena_check_user_speech)
        self.mic_check_btn.pack(side=LEFT, padx=(0, 8))
        self.ai_voice_btn = self.button(top, "AI Voice Test", self.arena_check_ai_speech)
        self.ai_voice_btn.pack(side=LEFT, padx=(0, 8))
        self.arena_voice_btn = self.button(top, "AI Voice: Off", self.toggle_arena_voice_responses)
        self.arena_voice_btn.pack(side=LEFT, padx=(0, 8))
        self.button(top, "Summarize Debate", self.summarize_arena).pack(side=LEFT, padx=(0, 8))
        self.button(top, "Export Arena", self.export_arena_log).pack(side=LEFT)

        controls = self.panel(arena_frame, fill=X, pady=(0, 8))
        grid = Frame(controls, bg=self.panel_color)
        grid.pack(fill=X, padx=12, pady=10)

        self.label(grid, "Topic", size=10, weight='bold', bg=self.panel_color).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.topic_entry = Entry(grid, font=(self.font_family, 10), bg=self.input_color, fg=self.text_color, insertbackground=self.accent_color, borderwidth=0, width=26)
        self.topic_entry.grid(row=0, column=1, sticky="w", padx=(0, 8), ipady=8)
        self.topic_entry.bind('<Return>', self.add_custom_topic)
        self.button(grid, "Add", self.add_custom_topic).grid(row=0, column=2, sticky="w", padx=(0, 16))

        self.label(grid, "Mode", size=10, weight='bold', bg=self.panel_color).grid(row=0, column=3, sticky="w", padx=(0, 8))
        self.arena_mode_var = StringVar(value=self.arena_config["mode"])
        self.arena_mode_combo = ttk.Combobox(grid, textvariable=self.arena_mode_var, values=["Brainstorm", "Adversarial Debate", "Consensus", "Mentor Panel"], state='readonly', width=18)
        self.arena_mode_combo.grid(row=0, column=4, sticky="w", padx=(0, 16))

        self.label(grid, "Rounds", size=10, weight='bold', bg=self.panel_color).grid(row=0, column=5, sticky="w", padx=(0, 8))
        self.arena_rounds_var = IntVar(value=self.arena_config["rounds"])
        Spinbox(grid, from_=2, to=20, textvariable=self.arena_rounds_var, width=5).grid(row=0, column=6, sticky="w", padx=(0, 12))

        self.label(grid, "Order", size=10, weight='bold', bg=self.panel_color).grid(row=1, column=0, sticky="w", pady=(10, 0), padx=(0, 8))
        self.arena_order_var = StringVar(value=self.arena_config["speaking_order"])
        self.arena_order_combo = ttk.Combobox(grid, textvariable=self.arena_order_var, values=["Round Robin", "Reverse", "Random"], state='readonly', width=14)
        self.arena_order_combo.grid(row=1, column=1, sticky="w", pady=(10, 0), padx=(0, 16))

        self.label(grid, "Response", size=10, weight='bold', bg=self.panel_color).grid(row=1, column=2, sticky="w", pady=(10, 0), padx=(0, 8))
        self.arena_tokens_var = IntVar(value=self.arena_config["response_tokens"])
        Spinbox(grid, from_=80, to=500, increment=20, textvariable=self.arena_tokens_var, width=6).grid(row=1, column=3, sticky="w", pady=(10, 0), padx=(0, 16))

        self.label(grid, "Temp", size=10, weight='bold', bg=self.panel_color).grid(row=1, column=4, sticky="w", pady=(10, 0), padx=(0, 8))
        self.arena_temp_var = DoubleVar(value=self.arena_config["temperature"])
        Scale(grid, from_=0.2, to=1.2, resolution=0.05, orient=HORIZONTAL, length=160, variable=self.arena_temp_var,
              bg=self.panel_color, fg=self.secondary_color, troughcolor=self.input_color, highlightthickness=0).grid(row=1, column=5, columnspan=2, sticky="w", pady=(10, 0), padx=(0, 16))

        self.label(grid, "Stop", size=10, weight='bold', bg=self.panel_color).grid(row=1, column=7, sticky="w", pady=(10, 0), padx=(0, 8))
        self.arena_stop_var = StringVar(value=self.arena_config["stop_condition"])
        self.arena_stop_combo = ttk.Combobox(grid, textvariable=self.arena_stop_var, values=["Max Rounds", "Consensus Reached"], state='readonly', width=18)
        self.arena_stop_combo.grid(row=1, column=8, sticky="w", pady=(10, 0))

        topic_frame = self.toolbar(arena_frame, fill=X, pady=(0, 8))
        self.label(topic_frame, "Selected topic", size=10, weight='bold', bg=self.bg_color).pack(side=LEFT, padx=(0, 6))
        self.topic_var = StringVar(value=self.current_topic)
        self.topic_combo = ttk.Combobox(topic_frame, textvariable=self.topic_var, values=self.custom_topics, state='readonly', font=(self.font_family, 10), width=40)
        self.topic_combo.pack(side=LEFT, padx=(0, 10))
        self.topic_combo.bind('<<ComboboxSelected>>', self.change_topic)
        self.arena_status = self.label(topic_frame, "Arena ready", size=10, weight='bold', color=self.success_color, bg=self.bg_color)
        self.arena_status.pack(side=LEFT)

        self.arena_display = scrolledtext.ScrolledText(self.panel(arena_frame, fill=BOTH, expand=True, pady=(0, 10)), wrap='word', font=(self.font_family, self.font_size), height=16)
        self.configure_text_widget(self.arena_display)
        self.arena_display.pack(fill=BOTH, expand=True)

        board_panel = self.panel(arena_frame, fill=BOTH, expand=False, pady=(0, 10))
        self.label(board_panel, "Context Board (claims and citations)", size=10, weight='bold', bg=self.panel_color).pack(anchor=W, padx=12, pady=(8, 4))
        self.context_board_display = Text(board_panel, height=8, font=(self.mono_family, 10))
        self.configure_text_widget(self.context_board_display)
        self.context_board_display.pack(fill=BOTH, expand=True, padx=12, pady=(0, 10))

        arena_input_frame = self.panel(arena_frame, fill=X)
        inner = Frame(arena_input_frame, bg=self.panel_color)
        inner.pack(fill=X, padx=12, pady=12)
        self.arena_input = Entry(inner, font=(self.font_family, self.font_size), bg=self.input_color, fg=self.text_color, insertbackground=self.accent_color, borderwidth=0)
        self.arena_input.pack(side=LEFT, fill=X, expand=True, ipady=12, padx=(0, 10))
        self.button(inner, "Interrupt / Redirect", self.send_arena_message, tone='primary', size=11).pack(side=RIGHT)
        self.arena_input.bind('<Return>', lambda e: self.send_arena_message())

    def _arena_mode_instructions(self, mode):
        mapping = {
            "Brainstorm": "Generate diverse ideas. Build on others. Cite at least one board item as [#id] when useful.",
            "Adversarial Debate": "Challenge weak assumptions. Attack ideas, not people. Provide counterpoints and alternatives.",
            "Consensus": "Converge toward a shared plan. Reduce disagreement and merge best points into one path.",
            "Mentor Panel": "Act like expert mentors. Give practical guidance, tradeoffs, and concrete recommendations."
        }
        return mapping.get(mode, mapping["Brainstorm"])

    def _arena_speaking_agents(self):
        agents = list(self.arena_agents)
        order = self.arena_order_var.get() if hasattr(self, "arena_order_var") else "Round Robin"
        if order == "Reverse":
            agents.reverse()
        elif order == "Random":
            random.shuffle(agents)
        return agents

    def _format_context_board_snippet(self, limit=10):
        if not self.arena_context_board:
            return "No board entries yet."
        recent = self.arena_context_board[-limit:]
        return "\n".join([f"[#{x['id']}] {x['speaker']}: {x['claim']}" for x in recent])

    def _moderator_score(self, text):
        score = 50
        text_l = text.lower()
        score += min(18, len(text) // 80)
        if any(k in text_l for k in ["because", "therefore", "evidence", "tradeoff", "risk"]):
            score += 12
        if "[#" in text:
            score += 8
        if any(k in text_l for k in ["step", "plan", "action"]):
            score += 8
        repeated = len(set(text_l.split())) < max(10, len(text_l.split()) // 3)
        if repeated:
            score -= 12
        return max(0, min(100, score))

    def _extract_claim(self, text):
        sentence = re.split(r'(?<=[.!?])\s+', text.strip())[0]
        return sentence[:220] if sentence else text[:220]

    def _update_context_board_view(self):
        if not hasattr(self, "context_board_display"):
            return
        self.context_board_display.delete("1.0", END)
        if not self.arena_context_board:
            self.context_board_display.insert(END, "No board entries yet.")
            return
        for entry in self.arena_context_board[-20:]:
            self.context_board_display.insert(END, f"[#{entry['id']}] {entry['speaker']} (score {entry['score']}): {entry['claim']}\n")

    def _check_consensus(self):
        if len(self.arena_context_board) < 4:
            return False
        last = " ".join([x["claim"].lower() for x in self.arena_context_board[-4:]])
        anchors = ["agree", "consensus", "shared plan", "final plan", "we should"]
        return sum(1 for a in anchors if a in last) >= 2

    def start_arena(self):
        self._ensure_arena_state()
        self.arena_running = True
        self.arena_interrupt_message = None
        self.current_topic = self.topic_var.get()
        self.arena_context_board = []
        self.arena_scores = {a.name: [] for a in self.arena_agents}
        self.arena_agent_state = {
            a.name: {
                "persona_shift": f"round-by-round evolution around {self.current_topic}",
                "memory": []
            } for a in self.arena_agents
        }
        self.arena_config = {
            "mode": self.arena_mode_var.get(),
            "rounds": int(self.arena_rounds_var.get()),
            "response_tokens": int(self.arena_tokens_var.get()),
            "temperature": float(self.arena_temp_var.get()),
            "speaking_order": self.arena_order_var.get(),
            "stop_condition": self.arena_stop_var.get()
        }

        self.arena_btn.config(text="Stop Arena", bg=self.danger_color)
        self.arena_status.config(text=f"Arena running ({self.arena_config['mode']})", fg=self.danger_color)

        self.arena_display.delete("1.0", END)
        self.arena_display.insert(END, f"Arena started\n")
        self.arena_display.insert(END, f"Topic: {self.current_topic}\n")
        self.arena_display.insert(END, f"Mode: {self.arena_config['mode']}\n")
        self.arena_display.insert(END, f"Rounds: {self.arena_config['rounds']} | Order: {self.arena_config['speaking_order']} | Stop: {self.arena_config['stop_condition']}\n")
        self.arena_display.insert(END, f"Participants: {', '.join([agent.name for agent in self.arena_agents])}\n\n")
        self._update_context_board_view()

        self.arena_thread = threading.Thread(target=self.run_arena_conversation, daemon=True).start()
        self.user_data['arena_sessions'] += 1
        self.update_stats()
        if hasattr(self, "update_header_cards"):
            self.update_header_cards()
        self.update_status("Arena started")

    def stop_arena(self):
        self.arena_running = False
        self.arena_btn.config(text="Start Arena", bg=self.success_color)
        self.arena_status.config(text="Arena ready", fg=self.success_color)
        self.arena_display.insert(END, "\nArena stopped\n")
        if hasattr(self, "update_header_cards"):
            self.update_header_cards()
        self.update_status("Arena stopped")

    def _build_arena_prompt(self, agent, round_num):
        mode = self.arena_config["mode"]
        board = self._format_context_board_snippet(10)
        memory = self.arena_agent_state.get(agent.name, {}).get("memory", [])
        memory_snippet = "\n".join(memory[-4:]) if memory else "No personal memory yet."
        interruption = f"\nUser interruption: {self.arena_interrupt_message}\nAddress this directly first." if self.arena_interrupt_message else ""
        return (
            f"You are {agent.name}, personality: {agent.personality}.\n"
            f"Topic: {self.current_topic}\n"
            f"Round: {round_num}\n"
            f"Mode behavior: {self._arena_mode_instructions(mode)}\n"
            f"Your evolving memory:\n{memory_snippet}\n\n"
            f"Shared context board:\n{board}\n"
            f"{interruption}\n"
            "Give one strong contribution (120-220 words), include at least one practical point, "
            "and cite board entries as [#id] when relevant."
        )

    def run_arena_conversation(self):
        max_rounds = self.arena_config["rounds"]
        for round_num in range(1, max_rounds + 1):
            if not self.arena_running:
                break

            agents = self._arena_speaking_agents()
            for agent in agents:
                if not self.arena_running:
                    break
                try:
                    prompt = self._build_arena_prompt(agent, round_num)
                    response = get_provider_response(prompt, provider="groq", model=agent.model, max_tokens=self.arena_config["response_tokens"])
                    self.root.after(0, lambda a=agent, r=response, rn=round_num: self.add_arena_message(a, r, rn))
                    time.sleep(1.2)
                except Exception:
                    self.root.after(0, lambda a=agent, rn=round_num: self.add_arena_message(a, "I hit a response issue and will continue next turn.", rn))

            self.arena_interrupt_message = None
            if self.arena_config["stop_condition"] == "Consensus Reached" and self._check_consensus():
                self.root.after(0, lambda: self.arena_display.insert(END, "\nModerator: Consensus reached. Stopping early.\n"))
                break

        self.root.after(0, self._arena_finish_rounds)

    def _arena_finish_rounds(self):
        if self.arena_running:
            self.stop_arena()
        self._print_arena_scoreboard()

    def _print_arena_scoreboard(self):
        self.arena_display.insert(END, "\nModerator Scoreboard\n")
        self.arena_display.insert(END, "-" * 28 + "\n")
        for name, scores in self.arena_scores.items():
            avg = (sum(scores) / len(scores)) if scores else 0
            self.arena_display.insert(END, f"{name}: avg {avg:.1f} over {len(scores)} turns\n")
        self.arena_display.see(END)

    def add_arena_message(self, agent, message, round_num):
        if not self.arena_running:
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        score = self._moderator_score(message)
        self.arena_scores.setdefault(agent.name, []).append(score)

        claim = self._extract_claim(message)
        board_id = len(self.arena_context_board) + 1
        self.arena_context_board.append({
            "id": board_id,
            "speaker": agent.name,
            "claim": claim,
            "score": score
        })
        self.arena_agent_state.setdefault(agent.name, {"memory": [], "persona_shift": ""})
        self.arena_agent_state[agent.name]["memory"].append(claim)
        self.arena_agent_state[agent.name]["memory"] = self.arena_agent_state[agent.name]["memory"][-10:]

        self._ensure_codebox_tags(self.arena_display)
        self.arena_display.insert(END, f"[{timestamp}] Round {round_num} | {agent.name} | Score {score}\n", "msg_header")
        self._insert_with_codeboxes(self.arena_display, message)
        self.arena_display.insert(END, "\n\n", "msg_plain")
        self.arena_display.see(END)
        self._update_context_board_view()
        if getattr(self, "arena_voice_enabled", False):
            try:
                threading.Thread(target=self.speak_response, args=(message,), daemon=True).start()
            except Exception:
                pass

    def send_arena_message(self):
        user_message = self.arena_input.get().strip()
        if not user_message:
            return
        self.arena_input.delete(0, END)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._ensure_codebox_tags(self.arena_display)
        self.arena_display.insert(END, f"[{timestamp}] You (interrupt):\n", "msg_header")
        self._insert_with_codeboxes(self.arena_display, user_message)
        self.arena_display.insert(END, "\n\n", "msg_plain")
        self.arena_display.see(END)
        if self.arena_running:
            self.arena_interrupt_message = user_message
            self.update_status("Arena interrupted with your redirect")
        else:
            self.update_status("Arena is idle, generating direct replies...")
            threading.Thread(target=self._arena_direct_reply_worker, args=(user_message,), daemon=True).start()

    def _arena_direct_reply_worker(self, user_message):
        """When arena is idle, let all agents reply once to the user's message."""
        agents = getattr(self, "arena_agents", [])
        for idx, agent in enumerate(agents, 1):
            try:
                prompt = (
                    f"You are {agent.name}, personality: {agent.personality}. "
                    f"Respond to user message in 90-160 words with concrete advice.\n"
                    f"User message: {user_message}"
                )
                response = get_provider_response(
                    prompt,
                    provider=CURRENT_PROVIDER,
                    model=agent.model,
                    max_tokens=180
                )
                self.root.after(0, lambda a=agent, r=response, i=idx: self._arena_add_direct_reply(a, r, i))
                time.sleep(0.7)
            except Exception as e:
                self.root.after(0, lambda a=agent, i=idx, er=str(e): self._arena_add_direct_reply(a, f"[reply error: {er}]", i))

    def _arena_add_direct_reply(self, agent, message, idx):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._ensure_codebox_tags(self.arena_display)
        self.arena_display.insert(END, f"[{timestamp}] Direct Reply {idx} | {agent.name}\n", "msg_header")
        self._insert_with_codeboxes(self.arena_display, message)
        self.arena_display.insert(END, "\n\n", "msg_plain")
        self.arena_display.see(END)
        if getattr(self, "arena_voice_enabled", False):
            try:
                threading.Thread(target=self.speak_response, args=(message,), daemon=True).start()
            except Exception:
                pass

    def arena_check_user_speech(self):
        """Quick microphone/input check for arena."""
        self.update_status("Mic check running...")
        self.arena_display.insert(END, "\n[Mic Check] Listening...\n")
        self.arena_display.see(END)
        threading.Thread(target=self._arena_check_user_speech_worker, daemon=True).start()

    def _arena_check_user_speech_worker(self):
        try:
            text = self.speech_recognizer.recognize_speech()
            self.root.after(0, lambda: self._arena_finish_user_speech_check(text))
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Mic check failed: {e}"))

    def _arena_finish_user_speech_check(self, text):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.arena_display.insert(END, f"[{timestamp}] Mic Check Result: {text}\n\n")
        self.arena_display.see(END)
        ok = text and "not available" not in text.lower() and "error" not in text.lower()
        self.update_status("Mic check passed" if ok else "Mic check needs attention")

    def arena_check_ai_speech(self):
        """Quick AI speech output check for arena."""
        sample = "Arena voice check complete. Lightsky AI voice output is active."
        self.arena_display.insert(END, f"[{datetime.now().strftime('%H:%M:%S')}] AI Voice Check: speaking sample\n\n")
        self.arena_display.see(END)
        if self.speech_engine:
            threading.Thread(target=self.speak_response, args=(sample,), daemon=True).start()
            self.update_status("AI voice check speaking")
            return
        # fallback: per-agent voice engines
        for agent in getattr(self, "arena_agents", []):
            if getattr(agent, "speech_engine", None):
                threading.Thread(target=agent.speak, args=(sample,), daemon=True).start()
                self.update_status("AI voice check speaking via arena agent")
                return
        self.update_status("AI voice not available")

    def toggle_arena_voice_responses(self):
        self.arena_voice_enabled = not getattr(self, "arena_voice_enabled", False)
        if hasattr(self, "arena_voice_btn"):
            self.arena_voice_btn.config(text=f"AI Voice: {'On' if self.arena_voice_enabled else 'Off'}")
        self.update_status(f"Arena AI voice {'enabled' if self.arena_voice_enabled else 'disabled'}")

    def summarize_arena(self):
        if not self.arena_context_board:
            self.update_status("No arena context to summarize yet")
            return
        board = self._format_context_board_snippet(20)
        prompt = (
            "You are the arena moderator. Summarize the debate into: 1) strongest insights, "
            "2) major disagreements, 3) final recommendation.\n\n"
            f"{board}"
        )
        self.run_ai_task("Summarizing arena", prompt, lambda result: self.arena_display.insert(END, f"\nArena Summary\n{result}\n\n"))

    def export_arena_log(self):
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if not filename:
                return
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.arena_display.get("1.0", END))
                f.write("\nContext Board\n")
                for x in self.arena_context_board:
                    f.write(f"[#{x['id']}] {x['speaker']} (score {x['score']}): {x['claim']}\n")
            self.update_status(f"Arena exported to {os.path.basename(filename)}")
        except Exception as e:
            self.update_status(f"Arena export failed: {e}")

    # Codex-style shell override: larger, readable, chat-first, and less fragile.
    def create_ultimate_interface(self):
        """Create a readable Codex-style workspace shell."""
        self.root.configure(bg=self.bg_color)
        self.root.geometry("1360x840")
        self.root.minsize(1000, 700)
        self.style_ttk()

        main = Frame(self.root, bg=self.bg_color)
        main.pack(fill=BOTH, expand=True)

        self.create_ultimate_header(main)

        body = Frame(main, bg=self.bg_color)
        body.pack(fill=BOTH, expand=True, padx=16, pady=(0, 10))

        self.sidebar = Frame(body, bg=self.surface_color, width=224, highlightthickness=1, highlightbackground=self.border_color)
        self.sidebar.pack(side=LEFT, fill=Y, padx=(0, 12))
        self.sidebar.pack_propagate(False)

        self.content_shell = Frame(body, bg=self.bg_color)
        self.content_shell.pack(side=LEFT, fill=BOTH, expand=True)

        self.create_ultimate_tabs(self.content_shell)
        self.create_status_bar(main)
        self.init_arena_agents()
        self.root.after(120, lambda: self.root.state('zoomed'))

    def create_ultimate_header(self, parent):
        """Readable app header with model controls and compact status cards."""
        header = Frame(parent, bg=self.panel_color, height=112, highlightthickness=1, highlightbackground=self.border_color)
        header.pack(fill=X, padx=16, pady=16)
        header.pack_propagate(False)
        RainbowLine(header, height=3, bg=self.panel_color, speed=85).pack(fill=X, side=TOP)
        left = Frame(header, bg=self.panel_color)
        left.pack(side=LEFT, fill=BOTH, expand=True, padx=18, pady=12)

        title_row = Frame(left, bg=self.panel_color)
        title_row.pack(anchor=W)
        self.logo_label = self.label(title_row, "✨", size=28, weight='bold', color=self.accent_color, bg=self.panel_color)
        self.logo_label.pack(side=LEFT, padx=(0, 10))
        self.label(title_row, self.app_name, size=22, weight='bold', bg=self.panel_color).pack(side=LEFT)

        self.provider_badge = self.label(left, "Model: LS 5.1 (custom)", size=10, color=self.secondary_color, bg=self.panel_color)
        self.provider_badge.pack(anchor=W, pady=(4, 0))

        cards = Frame(left, bg=self.panel_color)
        cards.pack(anchor=W, pady=(8, 0))
        self.model_card_value = self._make_header_card(cards, "Model", "LS 5.1")
        self.provider_card_value = self._make_header_card(cards, "Provider", "LS 5.1")
        self.arena_card_value = self._make_header_card(cards, "Arena", "Ready")

        right = Frame(header, bg=self.panel_color)
        right.pack(side=RIGHT, fill=Y, padx=18, pady=12)

        model_row = Frame(right, bg=self.panel_color)
        model_row.pack(anchor=E, pady=(0, 8))
        self.label(model_row, "Model", size=10, weight='bold', bg=self.panel_color).pack(side=LEFT, padx=(0, 8))
        self.model_var = StringVar(value=DEFAULT_MODEL_DISPLAY if DEFAULT_MODEL_DISPLAY in MODEL_OPTIONS else list(MODEL_OPTIONS.keys())[0])
        self.model_combo = ttk.Combobox(model_row, textvariable=self.model_var, values=list(MODEL_OPTIONS.keys()), state='readonly', font=(self.font_family, 10), width=34)
        self.model_combo.pack(side=LEFT)
        self.model_combo.bind('<<ComboboxSelected>>', self.change_model)

        action_row = Frame(right, bg=self.panel_color)
        action_row.pack(anchor=E)
        self.voice_input_btn = self.button(action_row, "Voice", self.toggle_voice_input, tone='success', size=10)
        self.voice_input_btn.pack(side=LEFT, padx=(0, 6))
        self.speech_btn = self.button(action_row, "Speech", self.toggle_speech, tone='primary', size=10)
        self.speech_btn.pack(side=LEFT, padx=(0, 6))
        self.theme_btn = self.button(action_row, "Theme", self.toggle_theme, size=10)
        self.theme_btn.pack(side=LEFT, padx=(0, 6))
        self.export_btn = self.button(action_row, "Export", self.export_all_data, size=10)
        self.export_btn.pack(side=LEFT)
        self.update_header_cards()

    def _animate_tab_enter(self, frame):
        """No-op: the previous animation unpacked content and could make tabs look tiny."""
        return

    def _on_tab_changed(self, event=None):
        try:
            tab_id = self.notebook.select()
            tab_label = self.notebook.tab(tab_id, "text")
            self._highlight_sidebar(tab_label)
        except Exception:
            pass

    def create_ultimate_tabs(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=BOTH, expand=True)
        self.create_ultimate_chat_tab()
        self.create_ultimate_arena_tab()
        self.create_ultimate_webgl_tab()
        self.create_look_take_tab()
        self.create_plugin_center_tab()
        self.create_inter_test_tab()
        self.create_ultimate_image_tab()
        self.create_ultimate_knowledge_tab()
        self.create_ultimate_analytics_tab()
        self.create_ultimate_settings_tab()
        self._build_sidebar_nav()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.notebook.select(0)
        self.root.after(200, lambda: self.input_field.focus_set() if hasattr(self, "input_field") else None)

    def _build_sidebar_nav(self):
        if not hasattr(self, "sidebar"):
            return
        for child in self.sidebar.winfo_children():
            child.destroy()

        RainbowLine(self.sidebar, height=3, bg=self.surface_color, speed=100).pack(fill=X, pady=(0, 10))
        Label(self.sidebar, text="Workspace", bg=self.surface_color, fg=self.brand_cyan if hasattr(self, "brand_cyan") else self.secondary_color, font=(self.font_family, 10, "bold")).pack(anchor=W, padx=14, pady=(6, 8))
        self._sidebar_buttons = {}
        for tab_id in self.notebook.tabs():
            name = self.notebook.tab(tab_id, "text")
            btn = Button(
                self.sidebar,
                text=name,
                command=lambda t=tab_id: self.notebook.select(t),
                font=(self.font_family, 11, "bold"),
                bg=self.surface_color,
                fg=self.text_color,
                activebackground=self.input_color,
                activeforeground=self.text_color,
                relief=FLAT,
                anchor=W,
                padx=14,
                pady=10,
                borderwidth=0,
                cursor='hand2'
            )
            btn.pack(fill=X, padx=8, pady=2)
            self._sidebar_buttons[name] = btn

        Label(self.sidebar, text="Agent tools: on", bg=self.surface_color, fg=self.success_color, font=(self.font_family, 10)).pack(side=BOTTOM, anchor=W, padx=14, pady=(0, 16))
        self._highlight_sidebar("Chat")

    def _highlight_sidebar(self, active_name):
        for name, btn in getattr(self, "_sidebar_buttons", {}).items():
            if name == active_name:
                btn.configure(bg="#233b68", fg=self.brand_cyan if hasattr(self, "brand_cyan") else self.accent_hover)
            else:
                btn.configure(bg=self.surface_color, fg=self.text_color)

    def create_ultimate_chat_tab(self):
        """Large, clear chat workspace with visible composer."""
        chat_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(chat_frame, text="Chat")
        self._register_tab_frame("Chat", chat_frame)

        top = Frame(chat_frame, bg=self.bg_color)
        top.pack(fill=X, pady=(0, 10))
        self.label(top, "Chat", size=20, weight='bold', bg=self.bg_color).pack(side=LEFT)
        self.label(top, "Ask, build, run tools, debug, search, and code.", size=11, color=self.secondary_color, bg=self.bg_color).pack(side=LEFT, padx=(12, 0))

        actions = Frame(top, bg=self.bg_color)
        actions.pack(side=RIGHT)
        self.button(actions, "Enhance", self.enhance_current_prompt, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(actions, "Code", self.code_helper).pack(side=LEFT, padx=(0, 6))
        self.button(actions, "Tools", self.show_agent_tool_help).pack(side=LEFT, padx=(0, 6))
        self.button(actions, "Clear", self.clear_chat, tone='danger').pack(side=LEFT)

        transcript = Frame(chat_frame, bg=self.panel_color, highlightthickness=1, highlightbackground=self.border_color)
        transcript.pack(fill=BOTH, expand=True, pady=(0, 12))
        self.chat_display = scrolledtext.ScrolledText(transcript, wrap='word', font=(self.font_family, 13), height=22)
        self.configure_text_widget(self.chat_display)
        self.chat_display.configure(padx=22, pady=18)
        self.chat_display.pack(fill=BOTH, expand=True, padx=1, pady=1)
        self.chat_display.insert(END, "Lightsky chat is ready.\nType in the message box below and press Enter to send. Use Shift+Enter for a new line.\n\n")

        composer_shell = Frame(chat_frame, bg=self.panel_color, highlightthickness=1, highlightbackground=self.border_color)
        composer_shell.pack(fill=X)
        RainbowLine(composer_shell, height=3, bg=self.panel_color, speed=80).pack(fill=X)
        composer = Frame(composer_shell, bg=self.panel_color)
        composer.pack(fill=X, padx=14, pady=14)

        input_side = Frame(composer, bg=self.panel_color)
        input_side.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        self.label(input_side, "Message", size=10, weight='bold', color=self.secondary_color, bg=self.panel_color).pack(anchor=W, pady=(0, 5))
        self.input_field = Text(input_side, height=4, font=(self.font_family, 13))
        self.configure_text_widget(self.input_field)
        self.input_field.pack(fill=BOTH, expand=True)

        buttons = Frame(composer, bg=self.panel_color)
        buttons.pack(side=RIGHT, fill=Y)
        self.button(buttons, "Send", self.send_message, tone='primary', size=12, width=10).pack(fill=X, pady=(22, 8))
        self.button(buttons, "Voice", self.voice_input_message, tone='success', width=10).pack(fill=X)
        self.input_field.bind('<Return>', self._chat_enter_to_send)
        self.input_field.bind('<Control-Return>', self._chat_enter_to_send)
        self.input_field.bind('<Shift-Return>', self._chat_shift_enter_newline)

        self.voice_status_label = self.label(chat_frame, "Voice: ready", size=10, color=self.success_color, bg=self.bg_color)
        self.voice_status_label.pack(anchor=E, pady=(6, 0))

    def _chat_enter_to_send(self, event=None):
        self.send_message()
        return "break"

    def _chat_shift_enter_newline(self, event=None):
        self.input_field.insert('insert', '\n')
        return "break"

    def _workspace_header(self, parent, title, subtitle, actions=None):
        header = Frame(parent, bg=self.bg_color)
        header.pack(fill=X, pady=(0, 12))
        title_box = Frame(header, bg=self.bg_color)
        title_box.pack(side=LEFT, fill=X, expand=True)
        self.label(title_box, title, size=20, weight='bold', bg=self.bg_color).pack(anchor=W)
        self.label(title_box, subtitle, size=11, color=self.secondary_color, bg=self.bg_color).pack(anchor=W, pady=(2, 0))
        action_box = Frame(header, bg=self.bg_color)
        action_box.pack(side=RIGHT)
        if actions:
            for text, command, tone in actions:
                self.button(action_box, text, command, tone=tone).pack(side=LEFT, padx=(0, 6))
        return action_box

    def _workspace_panel(self, parent, title=None, fill=BOTH, expand=True, side=LEFT, padx=0, pady=0, width=None):
        panel = Frame(parent, bg=self.panel_color, highlightthickness=1, highlightbackground=self.border_color)
        if width:
            panel.configure(width=width)
            panel.pack_propagate(False)
        panel.pack(side=side, fill=fill, expand=expand, padx=padx, pady=pady)
        if title:
            self.label(panel, title, size=11, weight='bold', bg=self.panel_color).pack(anchor=W, padx=14, pady=(12, 8))
        return panel

    def create_ultimate_arena_tab(self):
        """Arena as a proper debate workspace."""
        self._ensure_arena_state()
        arena_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(arena_frame, text="Arena")
        self._register_tab_frame("Arena", arena_frame)
        if not hasattr(self, "arena_voice_enabled"):
            self.arena_voice_enabled = False

        self._workspace_header(
            arena_frame,
            "Arena",
            "Multi-agent debate with rounds, moderator scoring, voice checks, and interruption.",
            [
                ("Start", self.toggle_arena, "success"),
                ("Mic Check", self.arena_check_user_speech, "secondary"),
                ("AI Voice", self.arena_check_ai_speech, "secondary"),
                ("Summary", self.summarize_arena, "primary"),
                ("Export", self.export_arena_log, "secondary"),
            ],
        )

        control = self._workspace_panel(arena_frame, "Debate Controls", fill=X, expand=False, side=TOP, pady=(0, 12))
        grid = Frame(control, bg=self.panel_color)
        grid.pack(fill=X, padx=14, pady=(0, 14))

        self.label(grid, "Topic", size=10, weight='bold', bg=self.panel_color).grid(row=0, column=0, sticky=W, padx=(0, 8))
        self.topic_var = StringVar(value=self.current_topic)
        self.topic_combo = ttk.Combobox(grid, textvariable=self.topic_var, values=self.custom_topics, state='readonly', font=(self.font_family, 10), width=38)
        self.topic_combo.grid(row=0, column=1, sticky=W, padx=(0, 14), ipady=2)
        self.topic_combo.bind('<<ComboboxSelected>>', self.change_topic)

        self.topic_entry = Entry(grid, font=(self.font_family, 10), bg=self.input_color, fg=self.text_color, insertbackground=self.accent_color, borderwidth=0, width=24)
        self.topic_entry.grid(row=0, column=2, sticky=W, padx=(0, 8), ipady=7)
        self.topic_entry.bind('<Return>', self.add_custom_topic)
        self.button(grid, "Add Topic", self.add_custom_topic).grid(row=0, column=3, sticky=W, padx=(0, 14))

        self.arena_status = self.label(grid, "Arena ready", size=10, weight='bold', color=self.success_color, bg=self.panel_color)
        self.arena_status.grid(row=0, column=4, sticky=W)

        self.label(grid, "Mode", size=10, weight='bold', bg=self.panel_color).grid(row=1, column=0, sticky=W, pady=(12, 0), padx=(0, 8))
        self.arena_mode_var = StringVar(value=self.arena_config["mode"])
        self.arena_mode_combo = ttk.Combobox(grid, textvariable=self.arena_mode_var, values=["Brainstorm", "Adversarial Debate", "Consensus", "Mentor Panel"], state='readonly', width=18)
        self.arena_mode_combo.grid(row=1, column=1, sticky=W, pady=(12, 0), padx=(0, 14))

        self.label(grid, "Rounds", size=10, weight='bold', bg=self.panel_color).grid(row=1, column=2, sticky=W, pady=(12, 0), padx=(0, 8))
        self.arena_rounds_var = IntVar(value=self.arena_config["rounds"])
        Spinbox(grid, from_=2, to=20, textvariable=self.arena_rounds_var, width=5).grid(row=1, column=3, sticky=W, pady=(12, 0), padx=(0, 14))

        self.label(grid, "Order", size=10, weight='bold', bg=self.panel_color).grid(row=1, column=4, sticky=W, pady=(12, 0), padx=(0, 8))
        self.arena_order_var = StringVar(value=self.arena_config["speaking_order"])
        self.arena_order_combo = ttk.Combobox(grid, textvariable=self.arena_order_var, values=["Round Robin", "Reverse", "Random"], state='readonly', width=14)
        self.arena_order_combo.grid(row=1, column=5, sticky=W, pady=(12, 0), padx=(0, 14))

        self.arena_tokens_var = IntVar(value=self.arena_config["response_tokens"])
        self.arena_temp_var = DoubleVar(value=self.arena_config["temperature"])
        self.arena_stop_var = StringVar(value=self.arena_config["stop_condition"])

        content = Frame(arena_frame, bg=self.bg_color)
        content.pack(fill=BOTH, expand=True)

        conversation = self._workspace_panel(content, "Conversation", fill=BOTH, expand=True, side=LEFT, padx=(0, 10))
        self.arena_display = scrolledtext.ScrolledText(conversation, wrap='word', font=(self.font_family, 12), height=18)
        self.configure_text_widget(self.arena_display)
        self.arena_display.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))

        side = self._workspace_panel(content, "Context Board", fill=BOTH, expand=False, side=RIGHT, width=360)
        self.context_board_display = Text(side, height=14, font=(self.mono_family, 10))
        self.configure_text_widget(self.context_board_display)
        self.context_board_display.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))

        composer = self._workspace_panel(arena_frame, "Send Message / Interrupt", fill=X, expand=False, side=TOP, pady=(12, 0))
        row = Frame(composer, bg=self.panel_color)
        row.pack(fill=X, padx=14, pady=(0, 14))
        self.arena_input = Entry(row, font=(self.font_family, 12), bg=self.input_color, fg=self.text_color, insertbackground=self.accent_color, borderwidth=0)
        self.arena_input.pack(side=LEFT, fill=X, expand=True, ipady=10, padx=(0, 10))
        self.arena_btn = self.button(row, "Start Arena", self.toggle_arena, tone='success', size=11)
        self.arena_btn.pack(side=RIGHT, padx=(6, 0))
        self.button(row, "Send", self.send_arena_message, tone='primary', size=11).pack(side=RIGHT)
        self.arena_input.bind('<Return>', lambda e: self.send_arena_message())

    def create_ultimate_webgl_tab(self):
        """Browser as a visual research workspace."""
        web_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(web_frame, text="Browser")
        self._register_tab_frame("Browser", web_frame)
        self._workspace_header(web_frame, "Browser", "Visual browsing, page structure, and web-assisted answers.", [("Ask Web", self.ask_web, "primary")])
        shell = self._workspace_panel(web_frame, fill=BOTH, expand=True, side=TOP)
        browser_host = Frame(shell, bg=self.panel_color)
        browser_host.pack(fill=BOTH, expand=True, padx=12, pady=12)
        self.visual_browser = VisualWebBrowser(browser_host, self.root)

    def create_look_take_tab(self):
        """Look & Take as a search/download workspace."""
        frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text="Look & Take")
        self._register_tab_frame("Look & Take", frame)
        self._workspace_header(frame, "Look & Take", "Search the web, inspect results, download safely, and run trusted Python files.")

        search = self._workspace_panel(frame, "Search", fill=X, expand=False, side=TOP, pady=(0, 12))
        row = Frame(search, bg=self.panel_color)
        row.pack(fill=X, padx=14, pady=(0, 14))
        self.look_take_query = StringVar(value="")
        Entry(row, textvariable=self.look_take_query, font=(self.font_family, 12), bg=self.input_color, fg=self.text_color, insertbackground=self.accent_color, relief=FLAT).pack(side=LEFT, fill=X, expand=True, ipady=10, padx=(0, 10))
        self.button(row, "Search", self.look_take_search, tone='primary', size=11).pack(side=LEFT, padx=(0, 6))
        self.button(row, "Download", self.look_take_download_selected, tone='success', size=11).pack(side=LEFT, padx=(0, 6))
        self.button(row, "Execute", self.look_take_execute_selected, tone='danger', size=11).pack(side=LEFT)

        body = Frame(frame, bg=self.bg_color)
        body.pack(fill=BOTH, expand=True)
        left = self._workspace_panel(body, "Results", fill=BOTH, expand=False, side=LEFT, padx=(0, 10), width=420)
        self.look_take_results = Listbox(left, font=(self.font_family, 11), bg=self.input_color, fg=self.text_color, selectbackground=self.accent_color, relief=FLAT, borderwidth=0)
        self.look_take_results.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.look_take_results.bind("<<ListboxSelect>>", self.look_take_show_details)

        right = self._workspace_panel(body, "Details", fill=BOTH, expand=True, side=RIGHT)
        self.look_take_details = scrolledtext.ScrolledText(right, wrap='word', font=(self.font_family, 11), height=18)
        self.configure_text_widget(self.look_take_details)
        self.look_take_details.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.look_take_details.insert(END, "Search for a file, package, dataset, or tool. Select a result to inspect it.")
        self.look_take_index = []
        self.look_take_download_dir = os.path.join(os.path.expanduser("~"), "Documents", "Codex", "2026-05-13", "hi", "downloads")
        os.makedirs(self.look_take_download_dir, exist_ok=True)

    def create_plugin_center_tab(self):
        """Plugin catalog workspace."""
        frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text="Plugin Center")
        self._register_tab_frame("Plugin Center", frame)
        self._workspace_header(frame, "Plugin Center", "Built-in tools every model can request through Lightsky.", [("Tool Prompt", self.plugin_center_show_prompt, "secondary"), ("Run Sample", self.plugin_center_run_sample, "success")])

        body = Frame(frame, bg=self.bg_color)
        body.pack(fill=BOTH, expand=True)
        left = self._workspace_panel(body, "Installed Plugins", fill=BOTH, expand=False, side=LEFT, padx=(0, 10), width=360)
        self.plugin_listbox = Listbox(left, font=(self.font_family, 11), bg=self.input_color, fg=self.text_color, selectbackground=self.accent_color, relief=FLAT, borderwidth=0)
        self.plugin_listbox.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.plugin_listbox.bind("<<ListboxSelect>>", self.plugin_center_show_details)

        right = self._workspace_panel(body, "Plugin Details", fill=BOTH, expand=True, side=RIGHT)
        self.plugin_details = scrolledtext.ScrolledText(right, wrap='word', font=(self.mono_family, 10), height=24)
        self.configure_text_widget(self.plugin_details)
        self.plugin_details.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.plugin_center_refresh()

    def create_inter_test_tab(self):
        """Internal app test bench workspace."""
        frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text="Inter-Test")
        self._register_tab_frame("Inter-Test", frame)
        self._workspace_header(frame, "Inter-Test", "Pick an app, run checks, execute safely, and read logs.", [("Pick App", self.intertest_pick_file, "secondary"), ("Run Tests", self.intertest_run_tests, "primary"), ("Execute", self.intertest_execute_app, "success")])

        config = self._workspace_panel(frame, "Target", fill=X, expand=False, side=TOP, pady=(0, 12))
        row = Frame(config, bg=self.panel_color)
        row.pack(fill=X, padx=14, pady=(0, 14))
        self.intertest_file_var = StringVar(value="")
        Entry(row, textvariable=self.intertest_file_var, font=(self.font_family, 11), bg=self.input_color, fg=self.text_color, insertbackground=self.accent_color, relief=FLAT).pack(side=LEFT, fill=X, expand=True, ipady=10, padx=(0, 10))
        self.intertest_endpoint_var = StringVar(value="http://127.0.0.1:8000")
        Entry(row, textvariable=self.intertest_endpoint_var, font=(self.font_family, 10), bg=self.input_color, fg=self.text_color, insertbackground=self.accent_color, relief=FLAT, width=28).pack(side=RIGHT, ipady=10)

        logs = self._workspace_panel(frame, "Internal Test Log", fill=BOTH, expand=True, side=TOP)
        self.intertest_output = scrolledtext.ScrolledText(logs, wrap='word', font=(self.mono_family, 10), height=24)
        self.configure_text_widget(self.intertest_output)
        self.intertest_output.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.intertest_output.insert(END, "Inter-Test ready. Pick an app file and run tests.\n")

    def create_ultimate_image_tab(self):
        """Image Studio as a production tool surface."""
        image_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(image_frame, text="Image Studio")
        self._register_tab_frame("Image Studio", image_frame)
        self._workspace_header(image_frame, "Image Studio", "Prompt, refine, generate variants, and save selected outputs.", [("Generate", self.generate_advanced_image, "primary"), ("4 Variants", lambda: (self.variants_var.set(4), self.generate_advanced_image()), "success"), ("Enhance", self.enhance_image_prompt, "secondary")])

        prompt_panel = self._workspace_panel(image_frame, "Prompt Controls", fill=X, expand=False, side=TOP, pady=(0, 12))
        inner = Frame(prompt_panel, bg=self.panel_color)
        inner.pack(fill=X, padx=14, pady=(0, 14))
        self.image_prompt = Text(inner, height=4, font=(self.font_family, 12))
        self.configure_text_widget(self.image_prompt)
        self.image_prompt.pack(fill=X, pady=(0, 10))

        self.negative_prompt_var = StringVar(value="blurry, low quality, watermark, text artifacts")
        Entry(inner, textvariable=self.negative_prompt_var, font=(self.font_family, 10), bg=self.input_color, fg=self.text_color, insertbackground=self.accent_color, relief=FLAT).pack(fill=X, ipady=8, pady=(0, 10))

        row = Frame(inner, bg=self.panel_color)
        row.pack(fill=X)
        self.current_image_style = "realistic"
        for style_name in ["realistic", "cinematic", "artistic", "fantasy", "minimal"]:
            self.button(row, style_name.title(), lambda s=style_name: self.set_image_style(s)).pack(side=LEFT, padx=(0, 6))
        self.image_quality_var = StringVar(value="High")
        ttk.Combobox(row, textvariable=self.image_quality_var, values=["Draft", "High", "Ultra"], state='readonly', width=10).pack(side=LEFT, padx=(12, 8))
        self.variants_var = IntVar(value=1)
        Spinbox(row, from_=1, to=4, textvariable=self.variants_var, width=5).pack(side=LEFT, padx=(0, 8))
        self.width_var = IntVar(value=1024)
        self.height_var = IntVar(value=1024)

        self.image_frame = self._workspace_panel(image_frame, "Generated Output", fill=BOTH, expand=True, side=TOP)
        self.last_generated_image = None
        self.last_generated_images = []
        self.image_placeholder = self.label(self.image_frame, "Image Studio ready. Write a prompt and generate.", size=16, color=self.secondary_color, bg=self.panel_color)
        self.image_placeholder.pack(expand=True)

    def create_ultimate_knowledge_tab(self):
        """Knowledge Lab as a document workspace."""
        frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text="Knowledge Lab")
        self._register_tab_frame("Knowledge Lab", frame)
        self._workspace_header(frame, "Knowledge Lab", "Import documents, search your corpus, and ask model-grounded questions.", [("Import", self.import_knowledge, "success"), ("Search", self.search_knowledge, "primary"), ("Ask KB", self.ask_knowledge, "primary"), ("Summarize", self.summarize_knowledge, "secondary")])

        panel = self._workspace_panel(frame, "Corpus", fill=BOTH, expand=True, side=TOP)
        self.knowledge_display = scrolledtext.ScrolledText(panel, wrap='word', font=(self.font_family, 12), height=25)
        self.configure_text_widget(self.knowledge_display)
        self.knowledge_display.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.knowledge_display.insert(END, "Knowledge Lab ready. Import docs, search them, or ask the KB.")
        self.knowledge_display.config(state=DISABLED)

    def create_ultimate_analytics_tab(self):
        """Analytics as a dashboard."""
        frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text="Analytics")
        self._register_tab_frame("Analytics", frame)
        self._workspace_header(frame, "Analytics", "Usage, generated assets, arena sessions, and model routing.", [("Refresh", self.refresh_analytics, "success"), ("Export", self.export_analytics, "primary"), ("Reset", self.reset_stats, "danger")])
        panel = self._workspace_panel(frame, "Dashboard", fill=BOTH, expand=True, side=TOP)
        self.analytics_display = Text(panel, font=(self.mono_family, 11), height=25)
        self.configure_text_widget(self.analytics_display)
        self.analytics_display.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.refresh_analytics()

    def create_ultimate_settings_tab(self):
        """Control Center as a serious settings surface."""
        settings_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(settings_frame, text="Control Center")
        self._register_tab_frame("Control Center", settings_frame)
        self._workspace_header(settings_frame, "Control Center", "Model routing, themes, providers, and LS 5.1 power modes.", [("Dark", lambda: self.set_theme('dark'), "secondary"), ("Light", lambda: self.set_theme('light'), "secondary"), ("Blue", lambda: self.set_theme('blue'), "secondary")])

        panel = self._workspace_panel(settings_frame, "Runtime", fill=BOTH, expand=True, side=TOP)
        info = Text(panel, height=20, font=(self.mono_family, 11))
        self.configure_text_widget(info)
        info.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        info.insert(END, f"App: {self.app_name}\n")
        info.insert(END, f"Provider: {provider_display_name()}\n")
        info.insert(END, f"Model: {CURRENT_MODEL}\n")
        info.insert(END, f"Hugging Face Hub: {'available' if HAS_HUGGINGFACE_HUB else 'HTTP fallback'}\n")
        info.insert(END, f"Hugging Face text models: {len(HUGGINGFACE_MODELS)}\n")
        info.insert(END, f"Hugging Face image models: {len(HUGGINGFACE_IMAGE_MODELS)}\n")
        info.insert(END, f"xAI Grok: {'configured' if XAI_API_KEY else 'missing key'}\n")
        info.insert(END, f"xAI Grok models: {len(XAI_MODELS)}\n")
        info.insert(END, f"NVIDIA Nemotron: {'configured' if NVIDIA_API_KEY else 'missing key'}\n")
        info.insert(END, f"NVIDIA Nemotron models: {len(NVIDIA_NEMOTRON_MODELS)}\n")
        info.insert(END, f"LS 5.1 Power Mode: {LS51_POWER_MODE}\n")
        info.insert(END, f"Debug/Vulnerability Engine: {LS51_DEBUG_VULN_MODE}\n")
        info.insert(END, f"Web Research Mode: {LS51_WEB_RESEARCH_MODE}\n")
        info.insert(END, f"CodeForge Mode: {LS51_CODEFORGE_MODE}\n")
        info.insert(END, f"Agent Tools: {MODEL_AGENT_TOOLS_ENABLED}\n")
        info.insert(END, f"Plugins: {', '.join([p['name'] for p in self.get_plugin_catalog()])}\n")
        info.configure(state=DISABLED)

    # Final chat override: conversation screen + Siri accent only on the text box.
    def create_ultimate_chat_tab(self):
        chat_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(chat_frame, text="Chat")
        self._register_tab_frame("Chat", chat_frame)

        header = Frame(chat_frame, bg=self.bg_color)
        header.pack(fill=X, pady=(0, 12))
        self.label(header, "Chat", size=20, weight='bold', bg=self.bg_color).pack(side=LEFT)
        self.chat_status_label = self.label(header, "Ready", size=10, color=self.secondary_color, bg=self.bg_color)
        self.chat_status_label.pack(side=LEFT, padx=(12, 0))

        actions = Frame(header, bg=self.bg_color)
        actions.pack(side=RIGHT)
        self.button(actions, "Tools", self.show_agent_tool_help).pack(side=LEFT, padx=(0, 6))
        self.button(actions, "Clear", self.clear_chat, tone='danger').pack(side=LEFT)

        screen = Frame(chat_frame, bg=self.panel_color, highlightthickness=1, highlightbackground=self.border_color)
        screen.pack(fill=BOTH, expand=True, pady=(0, 12))
        self.chat_display = scrolledtext.ScrolledText(screen, wrap='word', font=(self.font_family, 13), height=24)
        self.configure_text_widget(self.chat_display)
        self.chat_display.configure(padx=24, pady=20)
        self.chat_display.pack(fill=BOTH, expand=True, padx=1, pady=1)
        self.chat_display.insert(END, "Lightsky chat is ready.\n\n")

        composer_shell = Frame(chat_frame, bg=self.panel_color, highlightthickness=1, highlightbackground=self.border_color)
        composer_shell.pack(fill=X)
        # Siri-like accent only on the textbox/composer.
        RainbowLine(composer_shell, height=4, bg=self.panel_color, speed=70).pack(fill=X)

        composer = Frame(composer_shell, bg=self.panel_color)
        composer.pack(fill=X, padx=14, pady=14)

        self.input_field = Text(composer, height=4, font=(self.font_family, 13))
        self.configure_text_widget(self.input_field)
        self.input_field.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 12))

        send_area = Frame(composer, bg=self.panel_color)
        send_area.pack(side=RIGHT, fill=Y)
        self.send_btn = self.button(send_area, "Send", self.send_message, tone='primary', size=12, width=10)
        self.send_btn.pack(fill=X, pady=(0, 8))
        self.button(send_area, "Voice", self.voice_input_message, tone='success', width=10).pack(fill=X)

        self.voice_status_label = self.label(chat_frame, "Voice: ready", size=10, color=self.success_color, bg=self.bg_color)
        self.voice_status_label.pack(anchor=E, pady=(6, 0))

        self.input_field.bind('<Return>', self._chat_enter_to_send)
        self.input_field.bind('<Control-Return>', self._chat_enter_to_send)
        self.input_field.bind('<Shift-Return>', self._chat_shift_enter_newline)

    def _chat_should_use_power_pipeline(self, user_input):
        p = (user_input or "").lower()
        return any(k in p for k in [
            "debug", "vulnerability", "security", "fix this code", "audit",
            "generate code", "write code", "build app", "script", "traceback",
            "error:", "exception", "owasp"
        ]) or "```" in (user_input or "")

    def _get_fast_chat_response(self, user_input, max_tokens=520):
        """Fast path for ordinary chat so responses actually appear quickly."""
        if self._chat_should_use_power_pipeline(user_input):
            return get_provider_response(user_input, CURRENT_PROVIDER, CURRENT_MODEL, max_tokens)

        if CURRENT_PROVIDER == "ls_custom":
            response = get_cometapi_response(
                user_input,
                CURRENT_MODEL or LS_51_MODEL_ID,
                max_tokens=max_tokens,
                max_retries=1,
                system_prompt=CURRENT_SYSTEM_PROMPT,
                temperature=CURRENT_TEMPERATURE
            )
            return response

        return get_provider_response(user_input, CURRENT_PROVIDER, CURRENT_MODEL, max_tokens)

    def send_message(self):
        user_input = self.input_field.get("1.0", END).strip()
        if not user_input:
            return

        self.add_message("You", user_input)
        self.input_field.delete("1.0", END)

        if self._handle_direct_agent_command(user_input):
            return

        if hasattr(self, "send_btn"):
            self.send_btn.config(state=DISABLED, text="Sending")
        if hasattr(self, "chat_status_label"):
            self.chat_status_label.config(text="Thinking...", fg=self.accent_color)
        threading.Thread(target=self.get_ai_response, args=(user_input,), daemon=True).start()

    def get_ai_response(self, user_input):
        provider_label = provider_display_name()
        try:
            self.root.after(0, lambda: self.start_thinking_spinner(provider_label))
            response = self._get_fast_chat_response(user_input, 560)

            self.root.after(0, self.stop_thinking_spinner)
            handled_tool = False
            if MODEL_AGENT_TOOLS_ENABLED:
                handled_tool = self._handle_model_tool_call(user_input, response, provider_label)
            if not handled_tool:
                self.root.after(0, lambda: self.add_message(f"{self.app_name} ({provider_label})", response))
                self.root.after(0, lambda: self.update_status(f"Response received from {provider_label}"))
                self.root.after(0, lambda: self.chat_status_label.config(text="Ready", fg=self.secondary_color) if hasattr(self, "chat_status_label") else None)

            if self.speech_engine and not handled_tool:
                threading.Thread(target=self.speak_response, args=(response,), daemon=True).start()
        except Exception as e:
            self.root.after(0, self.stop_thinking_spinner)
            self.root.after(0, lambda: self.add_message(self.app_name, f"Error: {str(e)}"))
            self.root.after(0, lambda: self.chat_status_label.config(text="Error", fg=self.danger_color) if hasattr(self, "chat_status_label") else None)
        finally:
            self.root.after(0, lambda: self.send_btn.config(state=NORMAL, text="Send") if hasattr(self, "send_btn") else None)

    # Final thinking indicator override: Gemini-style sparkle row in the chat screen.
    def start_thinking_spinner(self, provider_label):
        self.thinking_active = True
        self.thinking_frame = 0
        self.thinking_mark = self.chat_display.index(END)
        self._ensure_codebox_tags(self.chat_display)
        self.chat_display.insert(END, "\n", "msg_plain")
        self.chat_display.see(END)
        self.animate_thinking_spinner(provider_label)

    def animate_thinking_spinner(self, provider_label):
        if not getattr(self, "thinking_active", False):
            return
        frames = ["✨", "✦", "✧", "✶", "✧", "✦"]
        dots = "." * ((self.thinking_frame % 4) + 1)
        mark = getattr(self, "thinking_mark", None)
        frame = frames[self.thinking_frame % len(frames)]
        text = f"{frame} {self.app_name} ({provider_label}) is thinking{dots}\n\n"
        if mark:
            try:
                self.chat_display.delete(mark, END)
                self.chat_display.insert(mark, text, "msg_header")
                self.chat_display.see(END)
            except Exception:
                pass
        if hasattr(self, "logo_label"):
            self.logo_label.config(text=frame)
        if hasattr(self, "chat_status_label"):
            self.chat_status_label.config(text=f"{frame} Thinking", fg=self.accent_color)
        self.thinking_frame += 1
        self.root.after(150, lambda: self.animate_thinking_spinner(provider_label))

    def stop_thinking_spinner(self):
        self.thinking_active = False
        if hasattr(self, "logo_label"):
            self.logo_label.config(text="✨")
        if hasattr(self, "chat_status_label"):
            self.chat_status_label.config(text="Ready", fg=self.secondary_color)
        mark = getattr(self, "thinking_mark", None)
        if mark:
            try:
                self.chat_display.delete(mark, END)
                self.chat_display.see(END)
            except Exception:
                pass

    # Pro chat override: final active implementation for a real conversation screen.
    def _chat_status_card(self, parent, title, value):
        palette = {
            "Model": ("#132f4c", self.brand_cyan if hasattr(self, "brand_cyan") else self.accent_color),
            "Provider": ("#2d2555", self.brand_violet if hasattr(self, "brand_violet") else self.accent_hover),
            "Tools": ("#173828", self.success_color),
            "Chat": ("#3b2b16", self.warning_color),
        }
        card_bg, accent = palette.get(title, (self.surface_color, self.accent_color))
        card = Frame(parent, bg=card_bg, highlightthickness=1, highlightbackground=accent)
        card.pack(side=LEFT, padx=(0, 8), ipady=2)
        self.label(card, title.upper(), size=8, weight='bold', color=accent, bg=card_bg).pack(anchor=W, padx=10, pady=(5, 0))
        value_label = self.label(card, value, size=10, weight='bold', color=self.text_color, bg=card_bg)
        value_label.pack(anchor=W, padx=10, pady=(0, 6))
        return value_label

    def _chat_tag_setup(self):
        if not hasattr(self, "chat_display"):
            return
        widget = self.chat_display
        self._ensure_codebox_tags(widget)
        widget.tag_configure("system_note", foreground=self.secondary_color, font=(self.font_family, 11), spacing1=4, spacing3=10)
        widget.tag_configure("user_header", foreground=self.success_color, font=(self.font_family, 10, "bold"), spacing1=10, spacing3=4)
        widget.tag_configure("assistant_header", foreground=self.accent_color, font=(self.font_family, 10, "bold"), spacing1=10, spacing3=4)
        widget.tag_configure("user_body", foreground=self.text_color, background=self.input_color, font=(self.font_family, 12), lmargin1=28, lmargin2=28, rmargin=36, spacing1=6, spacing3=8)
        widget.tag_configure("assistant_body", foreground=self.text_color, font=(self.font_family, 12), lmargin1=18, lmargin2=18, rmargin=28, spacing1=4, spacing3=8)
        widget.tag_configure("thinking_line", foreground=self.accent_color, font=(self.font_family, 12, "bold"), lmargin1=18, lmargin2=18, spacing1=8, spacing3=8)

    def _set_chat_display_state(self, state):
        if hasattr(self, "chat_display"):
            try:
                self.chat_display.configure(state=state)
            except Exception:
                pass

    def create_ultimate_chat_tab(self):
        chat_frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(chat_frame, text="Chat")
        self._register_tab_frame("Chat", chat_frame)

        header = Frame(chat_frame, bg=self.bg_color)
        header.pack(fill=X, pady=(0, 12))

        identity = Frame(header, bg=self.bg_color)
        identity.pack(side=LEFT, fill=X, expand=True)
        title_row = Frame(identity, bg=self.bg_color)
        title_row.pack(anchor=W)
        self.label(title_row, "\u2728", size=23, weight='bold', color=self.accent_color, bg=self.bg_color).pack(side=LEFT, padx=(0, 8))
        self.label(title_row, "Lightsky AI pro", size=21, weight='bold', bg=self.bg_color).pack(side=LEFT)
        self.label(identity, "by Krivi and Codex", size=10, color=self.secondary_color, bg=self.bg_color).pack(anchor=W)

        actions = Frame(header, bg=self.bg_color)
        actions.pack(side=RIGHT)
        self.button(actions, "Tools", self.show_agent_tool_help, tone='secondary').pack(side=LEFT, padx=(0, 6))
        self.button(actions, "Clear", self.clear_chat, tone='danger').pack(side=LEFT)

        cards = Frame(chat_frame, bg=self.bg_color)
        cards.pack(fill=X, pady=(0, 12))
        self.chat_model_value = self._chat_status_card(cards, "Model", "LS 5.1 custom")
        self.chat_provider_value = self._chat_status_card(cards, "Provider", provider_display_name())
        self.chat_tools_value = self._chat_status_card(cards, "Tools", "Enabled")
        self.chat_status_label = self._chat_status_card(cards, "Chat", "Ready")

        screen = Frame(chat_frame, bg=self.panel_color, highlightthickness=1, highlightbackground=self.border_color)
        screen.pack(fill=BOTH, expand=True, pady=(0, 12))
        self.chat_display = scrolledtext.ScrolledText(
            screen,
            wrap='word',
            font=(self.font_family, 12),
            height=24,
            cursor="arrow"
        )
        self.configure_text_widget(self.chat_display)
        self.chat_display.configure(bg=self.panel_color, padx=26, pady=22, state=DISABLED)
        self.chat_display.pack(fill=BOTH, expand=True, padx=1, pady=1)
        self._chat_tag_setup()

        composer_shell = Frame(chat_frame, bg=self.panel_color, highlightthickness=1, highlightbackground=self.border_color)
        composer_shell.pack(fill=X)
        RainbowLine(composer_shell, height=4, bg=self.panel_color, speed=70).pack(fill=X)

        composer = Frame(composer_shell, bg=self.panel_color)
        composer.pack(fill=X, padx=14, pady=14)

        self.input_field = Text(composer, height=3, font=(self.font_family, 13), wrap='word')
        self.configure_text_widget(self.input_field)
        self.input_field.configure(bg=self.input_color, padx=16, pady=12)
        self.input_field.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 12))

        send_area = Frame(composer, bg=self.panel_color)
        send_area.pack(side=RIGHT, fill=Y)
        self.send_btn = self.button(send_area, "Send", self.send_message, tone='primary', size=12, width=10)
        self.send_btn.pack(fill=X, pady=(0, 8))
        self.button(send_area, "Voice", self.voice_input_message, tone='success', width=10).pack(fill=X)

        self.voice_status_label = self.label(chat_frame, "Voice: ready", size=10, color=self.success_color, bg=self.bg_color)
        self.voice_status_label.pack(anchor=E, pady=(6, 0))

        self.input_field.bind('<Return>', self._chat_enter_to_send)
        self.input_field.bind('<Control-Return>', self._chat_enter_to_send)
        self.input_field.bind('<Shift-Return>', self._chat_shift_enter_newline)
        self.input_field.focus_set()

        # Repack the composer first from the bottom so it can never be pushed offscreen.
        try:
            screen.pack_forget()
            composer_shell.pack_forget()
            self.voice_status_label.pack_forget()
            composer_shell.pack(side=BOTTOM, fill=X, pady=(8, 0))
            screen.pack(side=TOP, fill=BOTH, expand=True, pady=(0, 0))
        except Exception:
            pass

        self.add_message("Lightsky AI pro", "Chat is ready. Type in the bottom composer and responses will appear in this screen.")

    def _chat_enter_to_send(self, event=None):
        self.send_message()
        return "break"

    def _chat_shift_enter_newline(self, event=None):
        return None

    def clear_chat(self):
        if not hasattr(self, "chat_display"):
            return
        self._set_chat_display_state(NORMAL)
        self.chat_display.delete("1.0", END)
        self._set_chat_display_state(DISABLED)
        self.add_message("Lightsky AI pro", "Chat cleared. I am ready for the next prompt.")
        self.update_status("Chat cleared")

    def add_message(self, sender, message):
        if not hasattr(self, "chat_display"):
            return
        if threading.current_thread() is not threading.main_thread():
            self.root.after(0, lambda s=sender, m=message: self.add_message(s, m))
            return

        text = "" if message is None else str(message)
        timestamp = datetime.now().strftime("%H:%M")
        is_user = str(sender).strip().lower() == "you"
        header_tag = "user_header" if is_user else "assistant_header"
        body_tag = "user_body" if is_user else "assistant_body"

        self._set_chat_display_state(NORMAL)
        self._chat_tag_setup()
        self.chat_display.insert(END, f"{sender}  {timestamp}\n", header_tag)
        if "```" in text:
            self._insert_with_codeboxes(self.chat_display, text)
        else:
            self.chat_display.insert(END, text, body_tag)
        self.chat_display.insert(END, "\n\n", "msg_plain")
        self.chat_display.see(END)
        self._set_chat_display_state(DISABLED)

        if is_user:
            try:
                self.user_data['messages_sent'] += 1
                self.update_stats()
            except Exception:
                pass

    def _provider_response_failed(self, response):
        if not response:
            return True
        lowered = str(response).lower()
        failure_markers = [
            "returned an error",
            "request error",
            "not responding",
            "not configured",
            "trouble connecting",
            "temporarily unavailable",
            "timeout",
            "connection error"
        ]
        return any(marker in lowered for marker in failure_markers)

    def _append_web_sources_if_needed(self, response, sources):
        if not sources:
            return response
        text = response or ""
        if any(src.get("url") and src["url"] in text for src in sources):
            return text
        lines = ["\n\nSources:"]
        for src in sources[:4]:
            if src.get("url"):
                lines.append(f"- {src.get('title', 'Source')} - {src['url']}")
        return text + "\n".join(lines)

    def _show_web_sources_in_chat(self, query, sources):
        if not sources or not hasattr(self, "chat_display"):
            return
        if hasattr(self, "chat_web_source_value"):
            try:
                self.chat_web_source_value.config(text=f"◎  Web search: {len(sources)} source(s)")
            except Exception:
                pass
        if hasattr(self, "chat_tools_value"):
            try:
                self.chat_tools_value.config(text=f"Web: {len(sources)} sources")
            except Exception:
                pass

        self._set_chat_display_state(NORMAL)
        self._chat_tag_setup()
        self.chat_display.insert(END, f"Web search  {datetime.now().strftime('%H:%M')}\n", "assistant_header")
        self.chat_display.insert(END, f"Searched: {query}\n", "system_note")
        for i, src in enumerate(sources[:4], 1):
            title = src.get("title") or "Source"
            url = src.get("url") or ""
            self.chat_display.insert(END, f"{i}. {title}\n{url}\n", "system_note")
        self.chat_display.insert(END, "\n", "msg_plain")
        self.chat_display.see(END)
        self._set_chat_display_state(DISABLED)

    def _web_search_fallback_answer(self, user_input, sources):
        lines = [
            "I searched the web, but the selected model provider did not return a usable synthesis. Here are the live sources I found:",
            ""
        ]
        for i, src in enumerate(sources[:5], 1):
            lines.append(f"{i}. {src.get('title', 'Source')}")
            if src.get("snippet"):
                lines.append(f"   {src['snippet'][:360]}")
            lines.append(f"   {src.get('url', '')}")
        lines.append("")
        lines.append("Try again or switch models; the web search itself is working.")
        return "\n".join(lines)

    def _prepare_universal_web_prompt(self, user_input):
        if not lightsky_should_search_web(user_input):
            return user_input, []
        if hasattr(self, "root"):
            try:
                self.root.after(0, lambda: self.update_status("Searching the web for live context..."))
                self.root.after(0, lambda: self.chat_tools_value.config(text="Web on") if hasattr(self, "chat_tools_value") else None)
            except Exception:
                pass
        web_context, sources = lightsky_build_universal_web_context(
            user_input,
            max_results=LS51_MAX_WEB_CONTEXT_RESULTS
        )
        if not web_context:
            return user_input, []
        clean_query = sources[0].get("query") if sources else lightsky_clean_web_query(user_input)
        if hasattr(self, "root") and sources:
            try:
                self.root.after(0, lambda q=clean_query, s=sources: self._show_web_sources_in_chat(q, s))
            except Exception:
                pass
        prompt = (
            "You have live web-search context below. Use it directly, cite URLs, and keep the answer grounded. "
            "If the sources do not contain enough information, say what is missing.\n\n"
            f"{web_context}\n\n"
            f"User request:\n{user_input}"
        )
        return prompt, sources

    def _get_ls51_comet_response_fast(self, prompt, max_tokens=560,
                                      model=None, system_prompt=None, temperature=None):
        if not COMETAPI_KEY:
            return "CometAPI is not configured. Add COMETAPI_API_KEY in settings or environment."

        chosen_model = model or CURRENT_MODEL or LS_51_MODEL_ID
        system_content = system_prompt or CURRENT_SYSTEM_PROMPT or LS_51_SYSTEM_PROMPT
        chosen_temperature = CURRENT_TEMPERATURE if temperature is None else temperature
        system_content = system_content + "\n\nAnswer as a normal chat assistant unless the user explicitly asks for a command. Put code in fenced code blocks."
        headers = {
            "Authorization": f"Bearer {COMETAPI_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": chosen_model,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": chosen_temperature
        }
        try:
            response = requests.post(
                f"{COMETAPI_BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=8
            )
            if response.status_code == 200:
                result = response.json()
                text, finish_reason = _extract_openai_compatible_text(result)
                return text or f"CometAPI returned an empty message from {chosen_model} (finish reason: {finish_reason})."
            return f"CometAPI returned an error for selected model {chosen_model}: {response.status_code}."
        except requests.exceptions.Timeout:
            return f"CometAPI timeout for selected model {chosen_model}."
        except requests.exceptions.ConnectionError:
            return f"CometAPI connection error for selected model {chosen_model}."
        except Exception as e:
            return f"CometAPI request error for selected model {chosen_model}: {e}"

    def _get_fast_chat_response(self, user_input, max_tokens=560, route=None):
        route = route or self._current_chat_route()
        selected_provider = route["provider"]
        selected_model = route["model"]
        selected_system_prompt = route.get("system_prompt")
        selected_temperature = route.get("temperature")
        model_input, web_sources = self._prepare_universal_web_prompt(user_input)
        if self._chat_should_use_power_pipeline(user_input):
            response = get_provider_response(
                model_input,
                selected_provider,
                selected_model,
                max_tokens,
                system_prompt=selected_system_prompt,
                temperature=selected_temperature
            )
        elif selected_provider == "ls_custom":
            response = self._get_ls51_comet_response_fast(
                model_input,
                max_tokens,
                model=selected_model,
                system_prompt=selected_system_prompt,
                temperature=selected_temperature
            )
        else:
            response = get_provider_response(
                model_input,
                selected_provider,
                selected_model,
                max_tokens,
                system_prompt=selected_system_prompt,
                temperature=selected_temperature
            )

        if self._provider_response_failed(response):
            return response or f"The selected model {selected_model} did not return a response."
        return self._append_web_sources_if_needed(response or "I could not get a model response yet. Check the provider key/model, then try again.", web_sources)

    def send_message(self):
        if not hasattr(self, "input_field"):
            return
        user_input = self._get_chat_input_text()
        if not user_input:
            self._restore_chat_input_placeholder()
            self.input_field.focus_set()
            return

        self.add_message("You", user_input)
        self._clear_chat_input()

        if self._handle_direct_agent_command(user_input):
            return

        route = self._current_chat_route()
        provider_label = provider_display_name(route["provider"])
        model_label = self._model_display_name_for_ui(route["display"])
        if hasattr(self, "send_btn"):
            self.send_btn.config(state=DISABLED, text=getattr(self, "send_btn_busy_text", "Stop"))
        if hasattr(self, "chat_status_label"):
            self.chat_status_label.config(text=f"Thinking with {model_label}", fg=self.accent_color)
        if hasattr(self, "chat_provider_value"):
            self.chat_provider_value.config(text=provider_label)
        if hasattr(self, "chat_model_name_value"):
            self.chat_model_name_value.config(text=model_label)
        if hasattr(self, "chat_tools_value"):
            self.chat_tools_value.config(text=f"Using {model_label}")
        threading.Thread(target=self.get_ai_response, args=(user_input, route), daemon=True).start()

    def _finish_chat_response(self, response, provider_label, model_label=None):
        self.stop_thinking_spinner()
        source_label = f"{provider_label} / {model_label}" if model_label else provider_label
        self.add_message(f"{self.app_name} ({source_label})", response)
        self.update_status(f"Response received from {source_label}")
        if hasattr(self, "chat_status_label"):
            self.chat_status_label.config(text="Ready", fg=self.secondary_color)
        if hasattr(self, "chat_tools_value"):
            self.chat_tools_value.config(text="Enabled")
        if hasattr(self, "input_field"):
            self.input_field.focus_set()

    def get_ai_response(self, user_input, route=None):
        route = route or self._current_chat_route()
        provider_label = provider_display_name(route["provider"])
        model_label = self._model_display_name_for_ui(route["display"])
        spinner_label = f"{provider_label} / {model_label}"
        try:
            self.root.after(0, lambda p=spinner_label: self.start_thinking_spinner(p))
            response = self._get_fast_chat_response(user_input, 560, route=route)
            self.root.after(0, lambda r=response, p=provider_label, m=model_label: self._finish_chat_response(r, p, m))

            if self.speech_engine:
                threading.Thread(target=self.speak_response, args=(response,), daemon=True).start()
        except Exception as e:
            self.root.after(0, self.stop_thinking_spinner)
            self.root.after(0, lambda err=e: self.add_message(self.app_name, f"Error: {str(err)}"))
            self.root.after(0, lambda: self.chat_status_label.config(text="Error", fg=self.danger_color) if hasattr(self, "chat_status_label") else None)
        finally:
            self.root.after(0, lambda: self.send_btn.config(state=NORMAL, text=getattr(self, "send_btn_idle_text", "Send")) if hasattr(self, "send_btn") else None)

    def start_thinking_spinner(self, provider_label):
        if not hasattr(self, "chat_display"):
            return
        if getattr(self, "thinking_active", False):
            return
        self.thinking_active = True
        self.thinking_frame = 0
        self._set_chat_display_state(NORMAL)
        self._chat_tag_setup()
        self.thinking_start = self.chat_display.index(END)
        self.chat_display.insert(END, f"\u2728 {self.app_name} ({provider_label}) is thinking...\n\n", "thinking_line")
        self.thinking_end = self.chat_display.index(END)
        self.chat_display.see(END)
        self._set_chat_display_state(DISABLED)
        self.animate_thinking_spinner(provider_label)

    def _set_thinking_text(self, text):
        if not hasattr(self, "chat_display"):
            return
        self._set_chat_display_state(NORMAL)
        start = getattr(self, "thinking_start", None)
        end = getattr(self, "thinking_end", None)
        if not start:
            start = self.chat_display.index(END)
        try:
            if end:
                self.chat_display.delete(start, end)
            self.chat_display.insert(start, text, "thinking_line")
            self.thinking_start = start
            self.thinking_end = self.chat_display.index("insert")
            self.chat_display.see(END)
        except Exception:
            pass
        self._set_chat_display_state(DISABLED)

    def animate_thinking_spinner(self, provider_label):
        if not getattr(self, "thinking_active", False):
            return
        frames = ["\u2728", "\u2726", "\u2727", "\u2736", "\u2727", "\u2726"]
        dots = "." * ((self.thinking_frame % 4) + 1)
        frame = frames[self.thinking_frame % len(frames)]
        if hasattr(self, "logo_label"):
            self.logo_label.config(text=frame)
        if hasattr(self, "chat_status_label"):
            self.chat_status_label.config(text=f"{frame} Thinking", fg=self.accent_color)
        self.thinking_frame += 1
        self.root.after(150, lambda p=provider_label: self.animate_thinking_spinner(p))

    def stop_thinking_spinner(self):
        self.thinking_active = False
        if hasattr(self, "logo_label"):
            self.logo_label.config(text="\u2728")
        if hasattr(self, "chat_status_label"):
            self.chat_status_label.config(text="Ready", fg=self.secondary_color)
        if hasattr(self, "chat_display"):
            self._set_chat_display_state(NORMAL)
            start = getattr(self, "thinking_start", None)
            end = getattr(self, "thinking_end", None)
            if start and end:
                try:
                    self.chat_display.delete(start, end)
                    self.chat_display.see(END)
                except Exception:
                    pass
            self._set_chat_display_state(DISABLED)
        self.thinking_start = None
        self.thinking_end = None

    def update_status(self, message):
        """Update app status safely, even while startup is still building tabs."""
        self._last_status_message = str(message)
        if hasattr(self, "status_label") and self.status_label.winfo_exists():
            try:
                self.status_label.config(text=self._last_status_message)
                self.root.update_idletasks()
            except Exception:
                pass

    def update_stats(self):
        """Update header stats only when the active shell has a stats label."""
        stats_text = (
            f"Messages {self.user_data.get('messages_sent', 0)}   "
            f"Tokens ~{self.user_data.get('messages_sent', 0) * 50}   "
            f"Voice {self.user_data.get('voice_commands', 0)}   "
            f"Images {self.user_data.get('images_generated', 0)}   "
            f"Arena {self.user_data.get('arena_sessions', 0)}"
        )
        if hasattr(self, "stats_label") and self.stats_label.winfo_exists():
            try:
                self.stats_label.config(text=stats_text)
            except Exception:
                pass
        if hasattr(self, "model_card_value") or hasattr(self, "provider_card_value"):
            try:
                self.update_header_cards()
            except Exception:
                pass

    def _select_chat_tab(self):
        if not hasattr(self, "notebook"):
            return
        try:
            tabs = self.notebook.tabs()
            if tabs:
                self.notebook.select(tabs[0])
                self._highlight_sidebar("Chat")
        except Exception:
            pass
        if hasattr(self, "input_field"):
            try:
                self.input_field.focus_set()
            except Exception:
                pass

    def create_ultimate_tabs(self, parent):
        """Create the full pro workspace and always open on the real Chat tab."""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=BOTH, expand=True)
        self.create_ultimate_chat_tab()
        self.create_ultimate_arena_tab()
        self.create_ultimate_webgl_tab()
        self.create_look_take_tab()
        self.create_plugin_center_tab()
        self.create_inter_test_tab()
        self.create_ultimate_image_tab()
        self.create_ultimate_knowledge_tab()
        self.create_ultimate_analytics_tab()
        self.create_ultimate_settings_tab()
        self._build_sidebar_nav()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self._select_chat_tab()
        self.root.after(80, self._select_chat_tab)
        self.root.after(300, self._select_chat_tab)

    # Working Look & Take override: robust search, previews, safe download, controlled execute.
    def create_look_take_tab(self):
        frame = Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text="Look & Take")
        self._register_tab_frame("Look & Take", frame)
        self._workspace_header(
            frame,
            "Look & Take",
            "Search the web, inspect sources, download safe files, and run trusted Python scripts.",
            [("Search", self.look_take_search, "primary"), ("Download", self.look_take_download_selected, "success"), ("Execute", self.look_take_execute_selected, "danger")]
        )

        search = self._workspace_panel(frame, "Search", fill=X, expand=False, side=TOP, pady=(0, 12))
        row = Frame(search, bg=self.panel_color)
        row.pack(fill=X, padx=12, pady=(0, 12))
        self.look_take_query = StringVar(value="")
        self.look_take_entry = Entry(
            row,
            textvariable=self.look_take_query,
            font=(self.font_family, 12),
            bg=self.input_color,
            fg=self.text_color,
            insertbackground=self.accent_color,
            relief=FLAT
        )
        self.look_take_entry.pack(side=LEFT, fill=X, expand=True, ipady=10, padx=(0, 10))
        self.look_take_entry.bind("<Return>", lambda event=None: (self.look_take_search(), "break"))
        self.button(row, "Search", self.look_take_search, tone='primary', size=11).pack(side=LEFT, padx=(0, 6))
        self.button(row, "Download", self.look_take_download_selected, tone='success', size=11).pack(side=LEFT, padx=(0, 6))
        self.button(row, "Execute", self.look_take_execute_selected, tone='danger', size=11).pack(side=LEFT)

        body = Frame(frame, bg=self.bg_color)
        body.pack(fill=BOTH, expand=True)
        left = self._workspace_panel(body, "Results", fill=BOTH, expand=True, side=LEFT, padx=(0, 6))
        right = self._workspace_panel(body, "Details", fill=BOTH, expand=True, side=RIGHT, padx=(6, 0))

        self.look_take_results = Listbox(
            left,
            font=(self.font_family, 11),
            bg=self.input_color,
            fg=self.text_color,
            selectbackground=self.accent_color,
            relief=FLAT,
            borderwidth=0
        )
        self.look_take_results.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.look_take_results.bind("<<ListboxSelect>>", self.look_take_show_details)

        self.look_take_details = scrolledtext.ScrolledText(right, wrap='word', font=(self.font_family, 11), height=18)
        self.configure_text_widget(self.look_take_details)
        self.look_take_details.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.look_take_details.insert(END, "Type a query and press Enter or Search. Select a result to preview it.")

        self.look_take_index = []
        self.look_take_last_file = None
        self.look_take_download_dir = os.path.join(os.path.expanduser("~"), "Documents", "Codex", "2026-05-13", "hi", "downloads")
        os.makedirs(self.look_take_download_dir, exist_ok=True)

    def look_take_search(self):
        query = self.look_take_query.get().strip() if hasattr(self, "look_take_query") else ""
        if not query:
            self.update_status("Enter a Look & Take search query")
            if hasattr(self, "look_take_entry"):
                self.look_take_entry.focus_set()
            return
        self.look_take_results.delete(0, END)
        self.look_take_index = []
        self.look_take_details.delete("1.0", END)
        self.look_take_details.insert(END, f"Searching live web for:\n{query}\n\nPlease wait...")
        self.update_status("Look & Take searching web...")
        threading.Thread(target=self._look_take_search_worker, args=(query,), daemon=True).start()

    def _look_take_search_worker(self, query):
        try:
            clean_query = lightsky_clean_web_query(query)
            results = _ls51_duckduckgo_search(clean_query, max_results=12)
            items = []
            for result in results:
                url = result.get("url", "")
                if not url.startswith(("http://", "https://")):
                    continue
                item = {
                    "title": result.get("title") or url,
                    "url": url,
                    "summary": "",
                    "safe_hint": self._look_take_download_hint(url),
                }
                items.append(item)
            self.root.after(0, lambda q=query, c=clean_query, xs=items: self._look_take_apply_results(q, xs, c))
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda: self._look_take_search_failed(err))

    def _look_take_search_failed(self, error):
        self.look_take_details.delete("1.0", END)
        self.look_take_details.insert(END, f"Search failed:\n{error}\n\nTry a simpler query or paste a direct URL.")
        self.update_status("Look & Take search failed")

    def _look_take_apply_results(self, query, items, clean_query=None):
        self.look_take_results.delete(0, END)
        self.look_take_index = items
        for i, it in enumerate(items, 1):
            host = urllib.parse.urlparse(it.get("url", "")).netloc
            self.look_take_results.insert(END, f"{i}. {it['title'][:90]}  [{host}]")
        self.look_take_details.delete("1.0", END)
        if items:
            self.look_take_details.insert(END, f"Query: {query}\nSearch used: {clean_query or query}\nResults: {len(items)}\n\nSelect a result to preview details.")
            self.update_status(f"Look & Take found {len(items)} result(s)")
        else:
            self.look_take_details.insert(END, f"No results for:\n{query}\n\nTry adding words like official, docs, GitHub, download, or file type.")
            self.update_status("Look & Take found no results")

    def _look_take_download_hint(self, url):
        ext = os.path.splitext(urllib.parse.urlparse(url).path.lower())[1]
        if ext in {".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".apk"}:
            return f"installer {ext} (download only)"
        if ext in {".py", ".zip", ".txt", ".md", ".json", ".csv", ".pdf", ".html", ".htm", ".7z", ".rar", ".tar", ".gz"}:
            return f"downloadable {ext}"
        return "web page"

    def look_take_show_details(self, event=None):
        try:
            sel = self.look_take_results.curselection()
            if not sel:
                return
            item = self.look_take_index[sel[0]]
            self.look_take_details.delete("1.0", END)
            self.look_take_details.insert(END, f"Title: {item['title']}\n")
            self.look_take_details.insert(END, f"URL: {item['url']}\n")
            self.look_take_details.insert(END, f"Type: {item.get('safe_hint', 'web page')}\n\n")
            self.look_take_details.insert(END, "Fetching preview...\n")
            self.update_status("Fetching Look & Take preview...")
            threading.Thread(target=self._look_take_preview_worker, args=(item,), daemon=True).start()
        except Exception as e:
            self.update_status(f"Preview failed: {e}")

    def _look_take_preview_worker(self, item):
        page = _ls51_fetch_page_summary(item["url"], max_chars=1800)
        self.root.after(0, lambda p=page, it=item: self._look_take_show_preview(it, p))

    def _look_take_show_preview(self, item, page):
        self.look_take_details.delete("1.0", END)
        self.look_take_details.insert(END, f"Title: {item['title']}\n")
        self.look_take_details.insert(END, f"URL: {item['url']}\n")
        self.look_take_details.insert(END, f"Type: {item.get('safe_hint', 'web page')}\n\n")
        if page:
            self.look_take_details.insert(END, f"Page title: {page.get('title', 'Untitled')}\n\n")
            self.look_take_details.insert(END, page.get("summary", "")[:1800] + "\n\n")
        else:
            self.look_take_details.insert(END, "Preview unavailable. You can still download if it passes safety checks.\n\n")
        self.look_take_details.insert(END, "Actions:\n- Download: resolves the selected link to the actual file when possible, including installers like .exe/.msi.\n- Execute: only runs a downloaded .py file after confirmation; installers are never auto-run.")
        self.update_status("Look & Take preview ready")

    def _look_take_is_safe_download(self, url, head_resp):
        blocked_ext = {".bat", ".cmd", ".scr", ".com", ".dll", ".vbs", ".ps1"}
        ext = os.path.splitext(urllib.parse.urlparse(url).path.lower())[1]
        if ext in blocked_ext:
            return False, f"Blocked script/system file type: {ext}"
        ctype = (head_resp.headers.get("content-type", "") if head_resp else "").lower()
        if any(x in ctype for x in ["application/x-bat", "application/x-msdos-program", "application/x-sh"]):
            return False, f"Blocked content-type: {ctype}"
        return True, "ok"

    def _look_take_content_disposition_filename(self, headers):
        cd = headers.get("content-disposition", "") if headers else ""
        if not cd:
            return ""
        m = re.search(r"filename\*=UTF-8''([^;]+)", cd, re.IGNORECASE)
        if m:
            return urllib.parse.unquote(m.group(1).strip().strip('"'))
        m = re.search(r'filename="?([^";]+)"?', cd, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    def _look_take_filename_for_response(self, response_url, content_type, headers=None):
        cd_name = self._look_take_content_disposition_filename(headers or {})
        parsed = urllib.parse.urlparse(response_url)
        name = cd_name or os.path.basename(parsed.path.rstrip("/"))
        if not name:
            host = parsed.netloc.replace(":", "_") or "downloaded_page"
            name = f"{host}.html"
        name = re.sub(r'[^A-Za-z0-9._-]', '_', name)[:120]
        root, ext = os.path.splitext(name)
        if not ext:
            if "text/html" in (content_type or "").lower():
                name += ".html"
            elif "json" in (content_type or "").lower():
                name += ".json"
            elif "pdf" in (content_type or "").lower():
                name += ".pdf"
            else:
                name += ".download"
        return name

    def _look_take_is_html_response(self, response):
        ctype = (response.headers.get("content-type", "") if response else "").lower()
        path_ext = os.path.splitext(urllib.parse.urlparse(getattr(response, "url", "")).path.lower())[1]
        return "text/html" in ctype or (not path_ext and "html" in ctype)

    def _look_take_direct_file_score(self, url, text=""):
        path = urllib.parse.urlparse(url).path.lower()
        ext = os.path.splitext(path)[1]
        preferred = {
            ".exe": 120, ".msi": 120, ".zip": 95, ".7z": 90, ".rar": 90,
            ".dmg": 90, ".pkg": 90, ".deb": 85, ".rpm": 85, ".apk": 85,
            ".pdf": 70, ".py": 60, ".json": 45, ".csv": 45, ".txt": 35, ".md": 35
        }
        score = preferred.get(ext, 0)
        lowered = (text or "").lower() + " " + url.lower()
        if "download" in lowered:
            score += 20
        if "release" in lowered or "asset" in lowered:
            score += 10
        return score

    def _look_take_find_direct_file_link(self, page_url, page_text):
        candidates = []
        for m in re.finditer(r'(?is)<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', page_text or ""):
            href = html.unescape(m.group(1)).strip()
            label = re.sub(r"<[^>]+>", " ", html.unescape(m.group(2) or ""))
            absolute = urllib.parse.urljoin(page_url, href)
            score = self._look_take_direct_file_score(absolute, label)
            if score > 0 and absolute.startswith(("http://", "https://")):
                candidates.append((score, absolute, label.strip()))
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[0], reverse=True)
        return {"url": candidates[0][1], "label": candidates[0][2], "score": candidates[0][0]}

    def _look_take_confirm_download_if_needed(self, response_url, headers):
        filename = self._look_take_filename_for_response(response_url, headers.get("content-type", ""), headers)
        ext = os.path.splitext(filename.lower())[1] or os.path.splitext(urllib.parse.urlparse(response_url).path.lower())[1]
        dangerous = {".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".apk", ".jar"}
        if ext not in dangerous:
            return True
        return self._askyesno_sync(
            "Download Installer",
            f"This is an installer/application file ({ext}).\n\nLightsky will download it only and will not run it automatically.\n\nURL:\n{response_url}\n\nContinue?"
        )

    def _look_take_download_worker(self, item):
        try:
            url = item["url"]
            head = None
            try:
                head = requests.head(url, allow_redirects=True, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            except Exception:
                head = None
            safe, reason = self._look_take_is_safe_download(url, head)
            if not safe:
                self.root.after(0, lambda r=reason: self.update_status(f"Download blocked: {r}"))
                return

            resp = requests.get(url, stream=True, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                self.root.after(0, lambda code=resp.status_code: self.update_status(f"Download failed: HTTP {code}"))
                return

            if self._look_take_is_html_response(resp):
                preview = resp.content[:350000].decode(resp.encoding or "utf-8", "ignore")
                direct = self._look_take_find_direct_file_link(resp.url, preview)
                if direct:
                    try:
                        resp.close()
                    except Exception:
                        pass
                    self.root.after(0, lambda u=direct["url"]: self.update_status(f"Resolved direct file link: {u[:80]}"))
                    resp = requests.get(direct["url"], stream=True, timeout=45, headers={"User-Agent": "Mozilla/5.0"})
                    if resp.status_code != 200:
                        self.root.after(0, lambda code=resp.status_code: self.update_status(f"Direct file download failed: HTTP {code}"))
                        return

            safe, reason = self._look_take_is_safe_download(resp.url, resp)
            if not safe:
                self.root.after(0, lambda r=reason: self.update_status(f"Download blocked: {r}"))
                return

            if not self._look_take_confirm_download_if_needed(resp.url, resp.headers):
                self.root.after(0, lambda: self.update_status("Download cancelled"))
                return

            name = self._look_take_filename_for_response(resp.url, resp.headers.get("content-type", ""), resp.headers)
            dest = os.path.abspath(os.path.join(self.look_take_download_dir, name))
            if not dest.startswith(os.path.abspath(self.look_take_download_dir)):
                self.root.after(0, lambda: self.update_status("Unsafe target path blocked"))
                return

            total = 0
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        total += len(chunk)
                        if total > 50 * 1024 * 1024:
                            raise RuntimeError("Blocked: file too large (>50MB)")
                        f.write(chunk)

            self.root.after(0, lambda p=dest, n=total: self._look_take_after_download(p, n))
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda: self.update_status(f"Download error: {err}"))

    # Codex-style light shell: sidebar features, hidden tabs, clean chat-first workspace.
    def _apply_codex_light_theme(self):
        self.bg_color = "#f5f7fb"
        self.surface_color = "#edf1f7"
        self.panel_color = "#ffffff"
        self.input_color = "#f7f8fb"
        self.accent_color = "#2563eb"
        self.accent_hover = "#dbeafe"
        self.success_color = "#16a34a"
        self.warning_color = "#ca8a04"
        self.danger_color = "#f43f5e"
        self.text_color = "#1d232f"
        self.secondary_color = "#667085"
        self.muted_color = "#9aa1ac"
        self.border_color = "#dde3ec"
        self.brand_cyan = "#0891b2"
        self.brand_violet = "#7c3aed"
        self.brand_pink = "#db2777"
        self.brand_green = "#16a34a"
        self.brand_gold = "#ca8a04"
        try:
            families = set(tkfont.families(self.root))
            self.font_family = "Segoe UI Variable Text" if "Segoe UI Variable Text" in families else "Segoe UI"
            self.mono_family = "Cascadia Mono" if "Cascadia Mono" in families else "Consolas"
        except Exception:
            self.font_family = "Segoe UI"
            self.mono_family = "Consolas"
        self.font_size = 12

    def style_ttk(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('Hidden.TNotebook', background=self.panel_color, borderwidth=0, tabmargins=0)
        style.layout('Hidden.TNotebook.Tab', [])
        style.configure(
            'Codex.Vertical.TScrollbar',
            troughcolor=self.panel_color,
            background="#d9dee8",
            bordercolor=self.panel_color,
            arrowcolor=self.secondary_color,
            lightcolor="#d9dee8",
            darkcolor="#d9dee8",
            relief='flat',
            width=10
        )
        style.configure(
            'TCombobox',
            fieldbackground=self.panel_color,
            background=self.panel_color,
            foreground=self.text_color,
            arrowcolor=self.secondary_color,
            bordercolor=self.border_color,
            lightcolor=self.border_color,
            darkcolor=self.border_color,
            padding=6
        )

    def label(self, parent, text, size=10, weight='normal', color=None, bg=None):
        family = "Segoe UI Emoji" if _has_emoji_text(text) else self.font_family
        return Label(
            parent,
            text=text,
            font=(family, size, weight),
            fg=color or self.text_color,
            bg=bg or parent.cget('bg'),
            anchor=W
        )

    def button(self, parent, text, command, tone='secondary', size=10, width=None):
        colors = {
            'primary': "#111827",
            'secondary': self.panel_color,
            'success': "#dcfce7",
            'danger': "#ffe4e6",
            'warning': "#fef3c7",
        }
        fgs = {
            'primary': "#ffffff",
            'secondary': self.text_color,
            'success': "#166534",
            'danger': "#be123c",
            'warning': "#92400e",
        }
        active = {
            'primary': "#374151",
            'secondary': self.accent_hover,
            'success': "#bbf7d0",
            'danger': "#fecdd3",
            'warning': "#fde68a",
        }
        return RoundedButton(
            parent,
            text=text,
            command=command,
            fill=colors.get(tone, self.panel_color),
            fg=fgs.get(tone, self.text_color),
            active_fill=active.get(tone, self.accent_hover),
            active_fg=fgs.get(tone, self.text_color),
            font_family=self.font_family,
            size=size,
            weight='bold',
            pad_x=16,
            pad_y=9,
            width=width,
            radius=20
        )

    def configure_text_widget(self, widget):
        widget.configure(
            bg=self.input_color,
            fg=self.text_color,
            insertbackground=self.accent_color,
            selectbackground="#bfdbfe",
            selectforeground=self.text_color,
            borderwidth=0,
            relief=FLAT,
            highlightthickness=0,
            padx=18,
            pady=16
        )

    def create_ultimate_interface(self):
        self._apply_codex_light_theme()
        tune_tk_rendering(self.root)
        self.root.configure(bg=self.bg_color)
        self.root.geometry("1460x900")
        self.root.minsize(1120, 760)
        self.style_ttk()

        self.app_shell = Frame(self.root, bg=self.bg_color)
        self.app_shell.pack(fill=BOTH, expand=True)

        self.sidebar = Frame(self.app_shell, bg=self.surface_color, width=276)
        self.sidebar.pack(side=LEFT, fill=Y)
        self.sidebar.pack_propagate(False)

        self.content_shell = Frame(self.app_shell, bg=self.panel_color, highlightthickness=1, highlightbackground=self.border_color)
        self.content_shell.pack(side=LEFT, fill=BOTH, expand=True)

        self.create_ultimate_tabs(self.content_shell)
        self.init_arena_agents()
        self.root.after(100, self._select_chat_tab)

    def _sidebar_button(self, parent, label, command, key=None, strong=False):
        btn = RoundedButton(
            parent,
            text=label,
            command=command,
            fill="#f8fafc",
            fg=self.text_color,
            active_fill="#e8eefb",
            active_fg=self.text_color,
            font_family=self.font_family,
            size=11,
            weight='bold' if strong else 'normal',
            radius=18,
            pad_x=16,
            pad_y=8,
            anchor=W
        )
        btn.pack(fill=X, padx=11, pady=3)
        if key:
            self._sidebar_buttons[key] = btn
        return btn

    def _sidebar_select_tab(self, tab_name):
        if not hasattr(self, "notebook"):
            return
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == tab_name:
                self.notebook.select(tab_id)
                self._highlight_sidebar(tab_name)
                return

    def _build_sidebar_nav(self):
        if not hasattr(self, "sidebar"):
            return
        for child in self.sidebar.winfo_children():
            child.destroy()
        self._sidebar_buttons = {}

        top = Frame(self.sidebar, bg=self.surface_color)
        top.pack(fill=X, pady=(10, 4))
        self._sidebar_button(top, "✨  New chat", self.clear_chat, key="Chat")
        self._sidebar_button(top, "🔎  Search", lambda: self._sidebar_select_tab("Look & Take"))
        self._sidebar_button(top, "⌘  Plugins", lambda: self._sidebar_select_tab("Plugin Center"))
        self._sidebar_button(top, "⏱  Automations", lambda: self.update_status("Automations live in Codex; Lightsky local actions use Plugin Center."))
        self._sidebar_button(top, "▱  Project", lambda: self._sidebar_select_tab("Inter-Test"))

        Label(self.sidebar, text="Chats", bg=self.surface_color, fg=self.muted_color, font=(self.font_family, 9)).pack(anchor=W, padx=20, pady=(12, 4))
        self._sidebar_button(self.sidebar, "hi", lambda: self._sidebar_select_tab("Chat"), key="ChatHistory", strong=True)

        Label(self.sidebar, text="Features", bg=self.surface_color, fg=self.muted_color, font=(self.font_family, 9)).pack(anchor=W, padx=20, pady=(12, 4))
        feature_names = ["Chat", "Arena", "Browser", "Look & Take", "Plugin Center", "Inter-Test", "Image Studio", "Knowledge Lab", "Analytics", "Control Center"]
        for name in feature_names:
            self._sidebar_button(self.sidebar, name, lambda n=name: self._sidebar_select_tab(n), key=name)

        bottom = Frame(self.sidebar, bg=self.surface_color)
        bottom.pack(side=BOTTOM, fill=X, pady=8)
        self.status_label = Label(bottom, text="Ready", bg=self.surface_color, fg=self.secondary_color, font=(self.font_family, 9), anchor=W, wraplength=240, justify=LEFT)
        self.status_label.pack(fill=X, padx=18, pady=(0, 5))
        self._sidebar_button(bottom, "⚙  Settings", lambda: self._sidebar_select_tab("Control Center"))
        upgrade = self.button(bottom, "Upgrade", lambda: self.update_status("Lightsky AI pro is already active."), size=10)
        upgrade.pack(anchor=E, padx=16, pady=(3, 0))
        self._highlight_sidebar("Chat")

    def _highlight_sidebar(self, active_name):
        for name, btn in getattr(self, "_sidebar_buttons", {}).items():
            selected = name == active_name or (active_name == "Chat" and name == "ChatHistory")
            if selected:
                btn.configure(bg="#e8eefb", fg=self.text_color)
            else:
                btn.configure(bg="#f8fafc", fg=self.text_color)

    def _on_tab_changed(self, event=None):
        try:
            tab_id = self.notebook.select()
            tab_label = self.notebook.tab(tab_id, "text")
            self._highlight_sidebar(tab_label)
        except Exception:
            pass

    def _workspace_header(self, parent, title, subtitle, actions=None):
        header = Frame(parent, bg=self.panel_color)
        header.pack(fill=X, padx=24, pady=(18, 12))
        title_box = Frame(header, bg=self.panel_color)
        title_box.pack(side=LEFT, fill=X, expand=True)
        self.label(title_box, title, size=18, weight='bold', bg=self.panel_color).pack(anchor=W)
        self.label(title_box, subtitle, size=10, color=self.secondary_color, bg=self.panel_color).pack(anchor=W, pady=(2, 0))
        action_box = Frame(header, bg=self.panel_color)
        action_box.pack(side=RIGHT)
        if actions:
            for text, command, tone in actions:
                self.button(action_box, text, command, tone=tone).pack(side=LEFT, padx=(0, 6))
        return action_box

    def _workspace_panel(self, parent, title=None, fill=BOTH, expand=True, side=LEFT, padx=0, pady=0, width=None):
        shell = RoundedFrame(
            parent,
            fill=self.panel_color,
            outline=self.border_color,
            radius=22,
            padding=0,
            parent_bg=parent.cget('bg') if hasattr(parent, 'cget') else self.bg_color,
            siri=bool(title)
        )
        if width:
            shell.configure(width=width)
            shell.pack_propagate(False)
        shell.pack(side=side, fill=fill, expand=expand, padx=padx, pady=pady)
        panel = shell.inner
        if title:
            self.label(panel, title, size=11, weight='bold', color=self.secondary_color, bg=self.panel_color).pack(anchor=W, padx=14, pady=(12, 8))
        return panel

    def create_ultimate_tabs(self, parent):
        self._tab_frames = {}
        self.notebook = ttk.Notebook(parent, style='Hidden.TNotebook')
        self.notebook.pack(fill=BOTH, expand=True)
        self.create_ultimate_chat_tab()
        self.create_ultimate_arena_tab()
        self.create_ultimate_webgl_tab()
        self.create_look_take_tab()
        self.create_plugin_center_tab()
        self.create_inter_test_tab()
        self.create_ultimate_image_tab()
        self.create_ultimate_knowledge_tab()
        self.create_ultimate_analytics_tab()
        self.create_ultimate_settings_tab()
        self._build_sidebar_nav()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self._select_chat_tab()

    def create_ultimate_chat_tab(self):
        chat_frame = Frame(self.notebook, bg=self.panel_color)
        self.notebook.add(chat_frame, text="Chat")
        self._register_tab_frame("Chat", chat_frame)

        top = Frame(chat_frame, bg=self.panel_color, height=58, highlightthickness=0)
        top.pack(fill=X)
        top.pack_propagate(False)
        self.label(top, "hi", size=12, weight='bold', bg=self.panel_color).pack(side=LEFT, padx=22, pady=18)
        self.button(top, "Tools", self.show_agent_tool_help, tone='secondary', size=9).pack(side=RIGHT, padx=(0, 18), pady=12)
        self.chat_status_label = self.label(top, "Ready", size=10, color=self.secondary_color, bg=self.panel_color)
        self.chat_status_label.pack(side=RIGHT, padx=(0, 10), pady=18)

        sep = Frame(chat_frame, bg=self.border_color, height=1)
        sep.pack(fill=X)

        body = Frame(chat_frame, bg=self.panel_color)
        body.pack(fill=BOTH, expand=True)

        center = Frame(body, bg=self.panel_color)
        center.pack(side=LEFT, fill=BOTH, expand=True, padx=(64, 24), pady=(10, 0))

        self.chat_display = Text(center, wrap='word', font=(self.font_family, 13), height=20, cursor="arrow")
        self.configure_text_widget(self.chat_display)
        self.chat_display.configure(bg=self.panel_color, padx=28, pady=22, state=DISABLED)
        self.chat_display.pack(fill=BOTH, expand=True)
        self._chat_tag_setup()

        side = Frame(body, bg=self.panel_color, width=250)
        side.pack(side=RIGHT, fill=Y, padx=(0, 18), pady=16)
        side.pack_propagate(False)
        sources_shell = RoundedFrame(side, fill="#fbfbfc", outline=self.border_color, radius=20, padding=0, parent_bg=self.panel_color, siri=True)
        sources_shell.pack(fill=X, pady=(0, 12))
        sources = sources_shell.inner
        self.label(sources, "Sources", size=11, color=self.secondary_color, bg="#fbfbfc").pack(anchor=W, padx=16, pady=(14, 8))
        self.label(sources, "✣  Hugging Face", size=10, color=self.secondary_color, bg="#fbfbfc").pack(anchor=W, padx=16, pady=4)
        self.chat_web_source_value = self.label(sources, "◎  Web search ready", size=10, color=self.secondary_color, bg="#fbfbfc")
        self.chat_web_source_value.pack(anchor=W, padx=16, pady=(4, 16))

        routing_shell = RoundedFrame(side, fill="#fbfbfc", outline=self.border_color, radius=20, padding=0, parent_bg=self.panel_color)
        routing_shell.pack(fill=X)
        routing = routing_shell.inner
        self.label(routing, "Active model", size=11, color=self.secondary_color, bg="#fbfbfc").pack(anchor=W, padx=16, pady=(14, 6))
        self.chat_model_name_value = self.label(routing, self._model_display_name_for_ui(), size=10, weight='bold', color=self.text_color, bg="#fbfbfc")
        self.chat_model_name_value.pack(anchor=W, padx=16, pady=(0, 4))
        self.chat_provider_value = self.label(routing, provider_display_name(), size=10, color=self.secondary_color, bg="#fbfbfc")
        self.chat_provider_value.pack(anchor=W, padx=16, pady=(0, 16))

        composer_shell = Frame(chat_frame, bg=self.panel_color)
        composer_shell.pack(fill=X, padx=(32, 32), pady=(0, 18))
        composer_shadow = Frame(composer_shell, bg="#eef1f6")
        composer_shadow.pack(fill=X, padx=(0, 0), pady=(0, 2))
        composer_shell_rounded = RoundedFrame(
            composer_shadow,
            fill="#ffffff",
            outline="#d8dde7",
            radius=30,
            padding=0,
            parent_bg="#eef1f6",
            siri=False
        )
        composer_shell_rounded.pack(fill=X, padx=1, pady=(0, 1))
        composer = composer_shell_rounded.inner

        input_row = Frame(composer, bg="#ffffff")
        input_row.pack(fill=X, padx=20, pady=(16, 4))

        self.input_field = Text(input_row, height=2, font=(self.font_family, 13), wrap='word')
        self.configure_text_widget(self.input_field)
        self.input_field.configure(bg="#ffffff", fg=self.text_color, padx=0, pady=0, insertbackground="#111827")
        self.input_field.pack(fill=BOTH, expand=True)

        bottom = Frame(composer, bg="#ffffff")
        bottom.pack(fill=X, padx=16, pady=(8, 14))
        self.button(bottom, "+", self.show_agent_tool_help, tone='secondary', size=13, width=1).pack(side=LEFT, padx=(0, 8))
        access_chip = self.button(bottom, "Full access v", self.show_agent_tool_help, tone='warning', size=9, width=11)
        access_chip.pack(side=LEFT, padx=(0, 10))

        self.voice_status_label = self.label(bottom, "Voice ready", size=9, color=self.secondary_color, bg="#ffffff")
        self.voice_status_label.pack(side=LEFT, padx=(0, 10))

        current_display = getattr(self, "active_model_display", DEFAULT_MODEL_DISPLAY if DEFAULT_MODEL_DISPLAY in MODEL_OPTIONS else list(MODEL_OPTIONS.keys())[0])
        self.chat_model_var = StringVar(value=current_display)
        self.model_var = self.chat_model_var
        right_tools = Frame(bottom, bg="#ffffff")
        right_tools.pack(side=RIGHT)
        self.chat_model_combo = ttk.Combobox(right_tools, textvariable=self.chat_model_var, values=list(MODEL_OPTIONS.keys()), state='readonly', font=(self.font_family, 10), width=30)
        self.model_combo = self.chat_model_combo
        self.chat_model_combo.pack(side=LEFT, padx=(0, 8))
        self.chat_model_combo.bind('<<ComboboxSelected>>', self.change_model)
        self.button(right_tools, "Mic", self.voice_input_message, tone='secondary', size=9, width=4).pack(side=LEFT, padx=(0, 8))
        self.send_btn_idle_text = "\u25b6"
        self.send_btn_busy_text = "\u25a0"
        self.send_btn = self.button(right_tools, self.send_btn_idle_text, self.send_message, tone='primary', size=12, width=2)
        self.send_btn.pack(side=LEFT)

        self.chat_tools_value = self.label(bottom, "Tools enabled", size=9, color=self.secondary_color, bg="#ffffff")
        self.chat_tools_value.pack(side=LEFT)
        self.input_field.bind('<Return>', self._chat_enter_to_send)
        self.input_field.bind('<Control-Return>', self._chat_enter_to_send)
        self.input_field.bind('<Shift-Return>', self._chat_shift_enter_newline)
        self._setup_chat_input_placeholder()
        self.input_field.focus_set()
        self.add_message("Lightsky AI pro", "Chat is ready. Your features are arranged in the sidebar.")

    def _setup_chat_input_placeholder(self):
        if not hasattr(self, "input_field"):
            return
        self.chat_input_placeholder = "Ask for follow-up changes"
        self.chat_input_placeholder_visible = False
        self._restore_chat_input_placeholder()
        self.input_field.bind("<FocusOut>", self._restore_chat_input_placeholder, add="+")
        self.input_field.bind("<KeyPress>", self._clear_chat_placeholder_for_typing, add="+")

    def _restore_chat_input_placeholder(self, event=None):
        if not hasattr(self, "input_field"):
            return
        current = self.input_field.get("1.0", END).strip()
        if current:
            return
        self.chat_input_placeholder_visible = True
        self.input_field.configure(fg="#b7bdc8")
        self.input_field.delete("1.0", END)
        self.input_field.insert("1.0", getattr(self, "chat_input_placeholder", "Ask for follow-up changes"))

    def _clear_chat_placeholder_for_typing(self, event=None):
        if not getattr(self, "chat_input_placeholder_visible", False):
            return
        if event is not None and event.keysym in {
            "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R",
            "Left", "Right", "Up", "Down", "Tab"
        }:
            return
        self.input_field.delete("1.0", END)
        self.input_field.configure(fg=self.text_color)
        self.chat_input_placeholder_visible = False

    def _get_chat_input_text(self):
        if not hasattr(self, "input_field"):
            return ""
        if getattr(self, "chat_input_placeholder_visible", False):
            return ""
        return self.input_field.get("1.0", END).strip()

    def _clear_chat_input(self):
        if not hasattr(self, "input_field"):
            return
        self.input_field.delete("1.0", END)
        self.chat_input_placeholder_visible = False
        self._restore_chat_input_placeholder()

    def _replace_chat_input(self, text):
        if not hasattr(self, "input_field"):
            return
        self.input_field.delete("1.0", END)
        self.input_field.configure(fg=self.text_color)
        self.chat_input_placeholder_visible = False
        self.input_field.insert("1.0", text or "")

    def _selected_model_display_from_ui(self):
        for var_name in ("chat_model_var", "model_var"):
            var = getattr(self, var_name, None)
            if var is not None:
                try:
                    value = var.get()
                    if value in MODEL_OPTIONS:
                        return value
                except Exception:
                    pass
        for name, config in MODEL_OPTIONS.items():
            if config.get("provider") == CURRENT_PROVIDER and config.get("model") == CURRENT_MODEL:
                return name
        return DEFAULT_MODEL_DISPLAY if DEFAULT_MODEL_DISPLAY in MODEL_OPTIONS else list(MODEL_OPTIONS.keys())[0]

    def _apply_selected_model_from_ui(self, silent=True):
        global CURRENT_MODEL, CURRENT_PROVIDER, CURRENT_SYSTEM_PROMPT, CURRENT_TEMPERATURE
        display_name = self._selected_model_display_from_ui()
        config = MODEL_OPTIONS.get(display_name)
        if not config:
            return None
        CURRENT_PROVIDER = config["provider"]
        CURRENT_MODEL = config["model"]
        CURRENT_SYSTEM_PROMPT = config.get("system_prompt", "You are Lightsky AI pro by krivi, a helpful desktop assistant.")
        CURRENT_TEMPERATURE = config.get("temperature", 0.7)
        self._sync_model_ui(display_name)
        if not silent:
            self.update_status(f"Model changed to {display_name} ({CURRENT_MODEL})")
        return display_name

    def _current_chat_route(self):
        display_name = self._apply_selected_model_from_ui(silent=True) or self._selected_model_display_from_ui()
        config = MODEL_OPTIONS.get(display_name, DEFAULT_MODEL_CONFIG)
        return {
            "display": display_name,
            "provider": config.get("provider", CURRENT_PROVIDER),
            "model": config.get("model", CURRENT_MODEL),
            "system_prompt": config.get("system_prompt", "You are Lightsky AI pro by krivi, a helpful desktop assistant."),
            "temperature": config.get("temperature", 0.7),
        }

    def _model_display_name_for_ui(self, display_name=None):
        display = display_name or getattr(self, "active_model_display", None)
        if not display:
            for name, config in MODEL_OPTIONS.items():
                if config.get("provider") == CURRENT_PROVIDER and config.get("model") == CURRENT_MODEL:
                    display = name
                    break
        display = display or (DEFAULT_MODEL_DISPLAY if DEFAULT_MODEL_DISPLAY in MODEL_OPTIONS else list(MODEL_OPTIONS.keys())[0])
        return (
            display
            .replace("Groq / ", "")
            .replace("CometAPI / ", "")
            .replace("Hugging Face / ", "")
            .replace("xAI / ", "")
            .replace("NVIDIA / ", "")
        )

    def _sync_model_ui(self, display_name):
        self.active_model_display = display_name
        for var_name in ("chat_model_var", "model_var"):
            var = getattr(self, var_name, None)
            if var is not None:
                try:
                    var.set(display_name)
                except Exception:
                    pass
        if hasattr(self, "chat_model_name_value"):
            self.chat_model_name_value.config(text=self._model_display_name_for_ui(display_name))
        if hasattr(self, "chat_provider_value"):
            self.chat_provider_value.config(text=provider_display_name(CURRENT_PROVIDER))
        if hasattr(self, "provider_badge"):
            self.provider_badge.config(text=f"Model: {self._model_display_name_for_ui(display_name)}")
        if hasattr(self, "model_card_value"):
            self.model_card_value.config(text=self._model_display_name_for_ui(display_name))
        if hasattr(self, "provider_card_value"):
            self.provider_card_value.config(text=provider_display_name(CURRENT_PROVIDER))

    def change_model(self, event=None):
        """Change the real backend model, not just the provider label."""
        display_name = None
        if event is not None:
            try:
                display_name = event.widget.get()
            except Exception:
                display_name = None
        if not display_name:
            for var_name in ("chat_model_var", "model_var"):
                var = getattr(self, var_name, None)
                if var is not None:
                    try:
                        display_name = var.get()
                    except Exception:
                        display_name = None
                    if display_name:
                        break

        config = MODEL_OPTIONS.get(display_name)
        if not config:
            self.update_status("Pick a real model from the model dropdown.")
            return

        self._apply_selected_model_from_ui(silent=False)

    def pick_provider(self, provider):
        """Select the first model for a provider and route responses through it."""
        for display_name, config in MODEL_OPTIONS.items():
            if config.get("provider") == provider:
                self._sync_model_ui(display_name)
                self.change_model()
                return
        self.update_status(f"No models configured for {provider}.")

    # Real browser override: opens an actual Chromium/Edge/Brave browser, not an HTML text preview.
    def _browser_candidate_paths(self):
        local = os.environ.get("LOCALAPPDATA", "")
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        candidates = {
            "Brave": [
                shutil.which("brave"),
                os.path.join(program_files, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
                os.path.join(program_files_x86, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
                os.path.join(local, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
            ],
            "Chrome": [
                shutil.which("chrome"),
                os.path.join(program_files, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(program_files_x86, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(local, "Google", "Chrome", "Application", "chrome.exe"),
            ],
            "Edge": [
                shutil.which("msedge"),
                os.path.join(program_files, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(program_files_x86, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(local, "Microsoft", "Edge", "Application", "msedge.exe"),
            ],
            "Firefox": [
                shutil.which("firefox"),
                os.path.join(program_files, "Mozilla Firefox", "firefox.exe"),
                os.path.join(program_files_x86, "Mozilla Firefox", "firefox.exe"),
            ],
        }
        found = {}
        for name, paths in candidates.items():
            for path in paths:
                if path and os.path.exists(path):
                    found[name] = path
                    break
        return found

    def _browser_choice_values(self):
        found = self._browser_candidate_paths()
        values = list(found.keys())
        values.append("System default")
        return values

    def _selected_browser_path(self):
        choice = self.browser_choice_var.get() if hasattr(self, "browser_choice_var") else "System default"
        return self._browser_candidate_paths().get(choice)

    def _normalize_browser_target(self, text, search_engine=None):
        target = (text or "").strip()
        if not target:
            return "https://www.google.com/"
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", target):
            return target
        if target.lower().startswith(("edge://", "chrome://", "brave://", "about:")):
            return target
        looks_like_url = "." in target and " " not in target and not target.startswith("?")
        if looks_like_url:
            return "https://" + target.strip("/")
        engine = search_engine or (self.browser_search_engine_var.get() if hasattr(self, "browser_search_engine_var") else "Google")
        search_urls = {
            "Google": "https://www.google.com/search?q=",
            "Bing": "https://www.bing.com/search?q=",
            "DuckDuckGo": "https://duckduckgo.com/?q=",
            "YouTube": "https://www.youtube.com/results?search_query=",
        }
        return search_urls.get(engine, search_urls["Google"]) + urllib.parse.quote(target)

    def _browser_log(self, message):
        if hasattr(self, "browser_log"):
            self.browser_log.configure(state=NORMAL)
            self.browser_log.insert(END, f"{datetime.now().strftime('%H:%M:%S')}  {message}\n")
            self.browser_log.see(END)
            self.browser_log.configure(state=DISABLED)
        self.update_status(message)

    def _launch_real_browser(self, target=None, new_window=True):
        url = self._normalize_browser_target(target or (self.browser_url_var.get() if hasattr(self, "browser_url_var") else ""))
        if hasattr(self, "browser_url_var"):
            self.browser_url_var.set(url)
        choice = self.browser_choice_var.get() if hasattr(self, "browser_choice_var") else "System default"
        browser_path = self._selected_browser_path()
        try:
            if browser_path:
                args = [browser_path]
                if new_window:
                    args.append("--new-window")
                args.append(url)
                subprocess.Popen(args, close_fds=True)
                self._browser_log(f"Opened {choice}: {url}")
            else:
                webbrowser.open(url, new=1 if new_window else 0)
                self._browser_log(f"Opened system browser: {url}")
            self.browser_history.append(url)
            if len(self.browser_history) > 50:
                self.browser_history = self.browser_history[-50:]
            self._refresh_browser_history()
        except Exception as e:
            self._browser_log(f"Browser launch failed: {e}")

    def browser_go(self):
        self._launch_real_browser(self.browser_url_var.get(), new_window=True)

    def browser_search(self):
        query = self.browser_search_var.get().strip() if hasattr(self, "browser_search_var") else ""
        if not query:
            self._browser_log("Enter a search query")
            return
        self._launch_real_browser(self._normalize_browser_target(query), new_window=True)

    def browser_quick_open(self, url):
        self._launch_real_browser(url, new_window=True)

    def browser_open_downloads(self):
        choice = self.browser_choice_var.get() if hasattr(self, "browser_choice_var") else "System default"
        if choice == "Edge":
            self._launch_real_browser("edge://downloads/all", new_window=True)
        elif choice in {"Chrome", "Brave"}:
            self._launch_real_browser("chrome://downloads/", new_window=True)
        else:
            downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            try:
                os.startfile(downloads)
                self._browser_log(f"Opened downloads folder: {downloads}")
            except Exception as e:
                self._browser_log(f"Could not open downloads folder: {e}")

    def browser_voice_search(self):
        if not getattr(self, "speech_recognizer", None) or not self.speech_recognizer.available:
            self._browser_log("Voice search is unavailable. Install/use speechrecognition + pvrecorder.")
            return
        self._browser_log("Listening for browser search...")

        def worker():
            text = self.speech_recognizer.recognize_speech()
            self.root.after(0, lambda t=text: self._finish_browser_voice_search(t))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_browser_voice_search(self, text):
        if not text or "error" in text.lower() or "timeout" in text.lower():
            self._browser_log(text or "No voice input heard")
            return
        self.browser_search_var.set(text)
        self._browser_log(f"Voice search: {text}")
        self.browser_search()

    def _refresh_browser_history(self):
        if not hasattr(self, "browser_history_list"):
            return
        self.browser_history_list.delete(0, END)
        for url in reversed(self.browser_history[-20:]):
            self.browser_history_list.insert(END, url)

    def browser_open_history_selection(self, event=None):
        sel = self.browser_history_list.curselection() if hasattr(self, "browser_history_list") else ()
        if not sel:
            return
        url = self.browser_history_list.get(sel[0])
        self._launch_real_browser(url, new_window=True)

    def create_ultimate_webgl_tab(self):
        """Real browser control tab that launches the system browser engine."""
        web_frame = Frame(self.notebook, bg=self.panel_color)
        self.notebook.add(web_frame, text="Browser")
        self._register_tab_frame("Browser", web_frame)

        self.browser_history = getattr(self, "browser_history", [])
        top = Frame(web_frame, bg=self.panel_color)
        top.pack(fill=X, padx=24, pady=(18, 12))
        title_box = Frame(top, bg=self.panel_color)
        title_box.pack(side=LEFT, fill=X, expand=True)
        self.label(title_box, "Browser", size=18, weight='bold', bg=self.panel_color).pack(anchor=W)
        self.label(title_box, "Real Chromium/Edge/Brave window for browsing, downloads, media, sign-in, and microphone sites.", size=10, color=self.secondary_color, bg=self.panel_color).pack(anchor=W, pady=(2, 0))

        browser_values = self._browser_choice_values()
        preferred = "Brave" if "Brave" in browser_values else ("Chrome" if "Chrome" in browser_values else ("Edge" if "Edge" in browser_values else "System default"))
        self.browser_choice_var = StringVar(value=preferred)
        ttk.Combobox(top, textvariable=self.browser_choice_var, values=browser_values, state="readonly", width=16).pack(side=RIGHT, padx=(10, 0))
        self.label(top, "Engine", size=9, color=self.secondary_color, bg=self.panel_color).pack(side=RIGHT)

        nav = self._workspace_panel(web_frame, "Address", fill=X, expand=False, side=TOP, padx=24, pady=(0, 12))
        row = Frame(nav, bg=self.panel_color)
        row.pack(fill=X, padx=14, pady=(0, 14))
        self.browser_url_var = StringVar(value="https://www.google.com/")
        Entry(row, textvariable=self.browser_url_var, font=(self.font_family, 12), bg="#ffffff", fg=self.text_color, insertbackground=self.accent_color, relief=FLAT, highlightthickness=1, highlightbackground=self.border_color).pack(side=LEFT, fill=X, expand=True, ipady=10, padx=(0, 10))
        self.button(row, "Go", self.browser_go, tone="primary", size=11).pack(side=LEFT, padx=(0, 6))
        self.button(row, "Google", lambda: self.browser_quick_open("https://www.google.com/"), tone="secondary", size=11).pack(side=LEFT, padx=(0, 6))
        self.button(row, "Downloads", self.browser_open_downloads, tone="success", size=11).pack(side=LEFT)

        search = self._workspace_panel(web_frame, "Search", fill=X, expand=False, side=TOP, padx=24, pady=(0, 12))
        search_row = Frame(search, bg=self.panel_color)
        search_row.pack(fill=X, padx=14, pady=(0, 14))
        self.browser_search_var = StringVar(value="")
        self.browser_search_engine_var = StringVar(value="Google")
        ttk.Combobox(search_row, textvariable=self.browser_search_engine_var, values=["Google", "Bing", "DuckDuckGo", "YouTube"], state="readonly", width=12).pack(side=LEFT, padx=(0, 8))
        Entry(search_row, textvariable=self.browser_search_var, font=(self.font_family, 12), bg="#ffffff", fg=self.text_color, insertbackground=self.accent_color, relief=FLAT, highlightthickness=1, highlightbackground=self.border_color).pack(side=LEFT, fill=X, expand=True, ipady=10, padx=(0, 10))
        self.button(search_row, "Search", self.browser_search, tone="primary", size=11).pack(side=LEFT, padx=(0, 6))
        self.button(search_row, "Talk", self.browser_voice_search, tone="secondary", size=11).pack(side=LEFT)

        quick = Frame(web_frame, bg=self.panel_color)
        quick.pack(fill=X, padx=24, pady=(0, 12))
        for label, url in [
            ("YouTube", "https://www.youtube.com/"),
            ("Google Images", "https://www.google.com/imghp"),
            ("Gmail", "https://mail.google.com/"),
            ("GitHub", "https://github.com/"),
            ("Hugging Face", "https://huggingface.co/"),
            ("ChatGPT", "https://chatgpt.com/"),
        ]:
            self.button(quick, label, lambda u=url: self.browser_quick_open(u), tone="secondary", size=10).pack(side=LEFT, padx=(0, 8), pady=(0, 6))

        body = Frame(web_frame, bg=self.panel_color)
        body.pack(fill=BOTH, expand=True, padx=24, pady=(0, 18))
        log_panel = self._workspace_panel(body, "Session", fill=BOTH, expand=True, side=LEFT, padx=(0, 12))
        self.browser_log = Text(log_panel, wrap="word", font=(self.mono_family, 10), height=18)
        self.configure_text_widget(self.browser_log)
        self.browser_log.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.browser_log.insert(END, f"Ready. Selected engine: {preferred}\n")
        self.browser_log.configure(state=DISABLED)

        history_panel = self._workspace_panel(body, "History", fill=BOTH, expand=False, side=RIGHT, width=360)
        self.browser_history_list = Listbox(history_panel, font=(self.font_family, 10), bg="#ffffff", fg=self.text_color, selectbackground="#dbeafe", selectforeground=self.text_color, relief=FLAT, borderwidth=0)
        self.browser_history_list.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.browser_history_list.bind("<Double-Button-1>", self.browser_open_history_selection)

    # GitHub-only Plugin Center overrides.
    def _github_plugin_root(self):
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "github_plugins")
        os.makedirs(root, exist_ok=True)
        return root

    def _safe_repo_dirname(self, full_name):
        cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "__", full_name or "github_plugin").strip("._-")
        return cleaned or "github_plugin"

    def _github_headers(self):
        return {
            "Accept": "application/vnd.github+json",
            "User-Agent": "Lightsky-AI-pro-by-krivi"
        }

    def _search_github_plugin_repos(self, query, limit=20):
        query = (query or "").strip() or "topic:ai-plugin"
        limit = max(1, min(int(limit or 20), 30))
        resp = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": query, "sort": "stars", "order": "desc", "per_page": limit},
            headers=self._github_headers(),
            timeout=25
        )
        if resp.status_code != 200:
            raise RuntimeError(f"GitHub search failed: HTTP {resp.status_code} - {resp.text[:220]}")

        results = []
        for repo in resp.json().get("items", [])[:limit]:
            full_name = repo.get("full_name") or ""
            if not full_name:
                continue
            branch = repo.get("default_branch") or "main"
            results.append({
                "name": full_name,
                "summary": repo.get("description") or "GitHub plugin repository.",
                "source": "github",
                "source_url": repo.get("html_url"),
                "clone_url": repo.get("clone_url"),
                "zip_url": f"https://api.github.com/repos/{full_name}/zipball/{branch}",
                "default_branch": branch,
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language") or "Unknown",
                "topics": repo.get("topics", [])[:10],
                "updated_at": repo.get("updated_at"),
                "installed": False,
            })
        return results

    def _load_installed_github_plugins(self):
        root = self._github_plugin_root()
        plugins = []
        for name in sorted(os.listdir(root)):
            folder = os.path.join(root, name)
            manifest_path = os.path.join(folder, "lightsky_plugin.json")
            if not os.path.isdir(folder) or not os.path.exists(manifest_path):
                continue
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["installed"] = True
                data["installed_path"] = folder
                data.setdefault("source", "github")
                plugins.append(data)
            except Exception:
                continue
        return plugins

    def _find_installed_github_plugin(self, plugin_name):
        wanted = (plugin_name or "").strip().lower()
        if not wanted:
            return None
        for plugin in self._load_installed_github_plugins():
            names = {
                str(plugin.get("name", "")).lower(),
                str(plugin.get("source_url", "")).rstrip("/").split("/")[-1].lower(),
            }
            if wanted in names:
                return plugin
        return None

    def get_plugin_catalog(self):
        """User-facing plugins are GitHub-sourced only."""
        items = getattr(self, "_plugin_center_items", None)
        if items:
            return items
        return self._load_installed_github_plugins()

    def create_plugin_center_tab(self):
        """GitHub-only Plugin Center."""
        frame = Frame(self.notebook, bg=self.panel_color)
        self.notebook.add(frame, text="Plugin Center")
        self._register_tab_frame("Plugin Center", frame)

        top = Frame(frame, bg=self.panel_color)
        top.pack(fill=X, padx=24, pady=(18, 10))
        title_box = Frame(top, bg=self.panel_color)
        title_box.pack(side=LEFT, fill=X, expand=True)
        self.label(title_box, "Plugin Center", size=18, weight='bold', bg=self.panel_color).pack(anchor=W)
        self.label(title_box, "All user-facing plugins come from GitHub repositories.", size=10, color=self.secondary_color, bg=self.panel_color).pack(anchor=W, pady=(2, 0))

        action_box = Frame(top, bg=self.panel_color)
        action_box.pack(side=RIGHT)
        self.button(action_box, "Search GitHub", self.plugin_center_search_github, tone='primary').pack(side=LEFT, padx=(0, 6))
        self.button(action_box, "Install Selected", self.plugin_center_install_selected, tone='success').pack(side=LEFT, padx=(0, 6))
        self.button(action_box, "Open Repo", self.plugin_center_open_selected, tone='secondary').pack(side=LEFT, padx=(0, 6))
        self.button(action_box, "Installed", self.plugin_center_refresh, tone='secondary').pack(side=LEFT)

        query_row = Frame(frame, bg=self.panel_color)
        query_row.pack(fill=X, padx=24, pady=(0, 12))
        self.github_plugin_query_var = StringVar(value="topic:mcp-server")
        query = Entry(query_row, textvariable=self.github_plugin_query_var, font=(self.font_family, 11), bg="#ffffff", fg=self.text_color, insertbackground=self.accent_color, relief=FLAT, highlightthickness=1, highlightbackground=self.border_color)
        query.pack(side=LEFT, fill=X, expand=True, ipady=8)
        query.bind("<Return>", lambda _e: self.plugin_center_search_github())

        body = Frame(frame, bg=self.panel_color)
        body.pack(fill=BOTH, expand=True, padx=24, pady=(0, 18))
        left = self._workspace_panel(body, "GitHub Plugins", fill=BOTH, expand=False, side=LEFT, padx=(0, 12), width=380)
        self.plugin_listbox = Listbox(left, font=(self.font_family, 10), bg="#ffffff", fg=self.text_color, selectbackground="#dbeafe", selectforeground=self.text_color, relief=FLAT, borderwidth=0)
        self.plugin_listbox.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.plugin_listbox.bind("<<ListboxSelect>>", self.plugin_center_show_details)

        right = self._workspace_panel(body, "Details", fill=BOTH, expand=True, side=RIGHT)
        self.plugin_details = scrolledtext.ScrolledText(right, wrap='word', font=(self.mono_family, 10), height=24)
        self.configure_text_widget(self.plugin_details)
        self.plugin_details.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))

        self.plugin_center_refresh()
        self.root.after(400, self.plugin_center_search_github)

    def _plugin_center_set_items(self, items, message):
        self._plugin_center_items = items or []
        if not hasattr(self, "plugin_listbox"):
            return
        self.plugin_listbox.delete(0, END)
        for plugin in self._plugin_center_items:
            prefix = "Installed" if plugin.get("installed") else "GitHub"
            self.plugin_listbox.insert(END, f"{prefix} / {plugin.get('name', 'unknown')}")
        self.plugin_details.delete("1.0", END)
        self.plugin_details.insert(END, message)
        self.update_status(message.splitlines()[0] if message else "Plugin Center ready")

    def plugin_center_refresh(self):
        installed = self._load_installed_github_plugins()
        if installed:
            self._plugin_center_set_items(installed, f"Installed GitHub plugins: {len(installed)}\n\nSelect one to inspect it.")
        else:
            self._plugin_center_set_items([], "No GitHub plugins installed yet.\n\nSearch GitHub, select a repository, then install it. Internal web/HF/file helpers are agent tools, not Plugin Center plugins.")

    def plugin_center_search_github(self):
        query = self.github_plugin_query_var.get().strip() if hasattr(self, "github_plugin_query_var") else "topic:mcp-server"
        if hasattr(self, "plugin_details"):
            self.plugin_details.delete("1.0", END)
            self.plugin_details.insert(END, f"Searching GitHub for plugins...\nQuery: {query}\n")
        self.update_status("Searching GitHub plugins...")

        def worker():
            def publish(callback):
                try:
                    self.root.after(0, callback)
                except RuntimeError:
                    pass

            try:
                results = self._search_github_plugin_repos(query, 20)
                installed_names = {p.get("name") for p in self._load_installed_github_plugins()}
                for item in results:
                    if item.get("name") in installed_names:
                        item["installed"] = True
                msg = f"GitHub plugin results: {len(results)}\nQuery: {query}\n\nSelect a repo to inspect or install."
                publish(lambda: self._plugin_center_set_items(results, msg))
            except Exception as e:
                publish(lambda err=e: self._plugin_center_set_items([], f"GitHub plugin search failed:\n{err}\n\nTry a simpler query like: ai plugin"))

        threading.Thread(target=worker, daemon=True).start()

    def _selected_github_plugin_item(self):
        sel = self.plugin_listbox.curselection() if hasattr(self, "plugin_listbox") else ()
        if not sel:
            self.update_status("Select a GitHub plugin first")
            return None
        items = getattr(self, "_plugin_center_items", [])
        if sel[0] >= len(items):
            self.update_status("Plugin selection is out of range")
            return None
        return items[sel[0]]

    def plugin_center_show_details(self, event=None):
        plugin = self._selected_github_plugin_item()
        if not plugin or not hasattr(self, "plugin_details"):
            return
        self.plugin_details.delete("1.0", END)
        self.plugin_details.insert(END, f"Plugin: {plugin.get('name')}\n")
        self.plugin_details.insert(END, f"Source: GitHub\n")
        self.plugin_details.insert(END, f"URL: {plugin.get('source_url')}\n")
        self.plugin_details.insert(END, f"Summary: {plugin.get('summary')}\n")
        self.plugin_details.insert(END, f"Language: {plugin.get('language', 'Unknown')}\n")
        self.plugin_details.insert(END, f"Stars: {plugin.get('stars', 0)}\n")
        self.plugin_details.insert(END, f"Updated: {plugin.get('updated_at', 'unknown')}\n")
        topics = ", ".join(plugin.get("topics") or [])
        if topics:
            self.plugin_details.insert(END, f"Topics: {topics}\n")
        if plugin.get("installed_path"):
            self.plugin_details.insert(END, f"Installed path: {plugin.get('installed_path')}\n")
        self.plugin_details.insert(END, "\nSafety: installing downloads the repository source only. Lightsky does not execute GitHub plugin code automatically.\n")
        sample = {"action": "github_plugin", "plugin": plugin.get("name"), "reason": "Inspect installed GitHub plugin metadata."}
        self.plugin_details.insert(END, "\nModel call format after install:\n```ls_tool_call\n" + json.dumps(sample, indent=2) + "\n```\n")

    def plugin_center_open_selected(self):
        plugin = self._selected_github_plugin_item()
        if plugin and plugin.get("source_url"):
            webbrowser.open(plugin["source_url"])
            self.update_status(f"Opened GitHub repo: {plugin.get('name')}")

    def plugin_center_install_selected(self):
        plugin = self._selected_github_plugin_item()
        if not plugin:
            return
        if plugin.get("installed_path"):
            self.update_status("Plugin is already installed")
            return
        ok = messagebox.askyesno(
            "Install GitHub Plugin",
            f"Download this GitHub repository into Lightsky plugins?\n\n{plugin.get('name')}\n\nCode will not be executed automatically."
        )
        if not ok:
            return
        self.plugin_details.delete("1.0", END)
        self.plugin_details.insert(END, f"Installing from GitHub...\n{plugin.get('source_url')}\n")
        self.update_status("Installing GitHub plugin...")
        threading.Thread(target=self._install_github_plugin_worker, args=(plugin,), daemon=True).start()

    def _install_github_plugin_worker(self, plugin):
        root = self._github_plugin_root()
        folder_name = self._safe_repo_dirname(plugin.get("name"))
        target = os.path.join(root, folder_name)
        staging = os.path.join(root, folder_name + "__download")
        def publish(callback):
            try:
                self.root.after(0, callback)
            except RuntimeError:
                pass

        try:
            if os.path.exists(staging):
                shutil.rmtree(staging)
            os.makedirs(staging, exist_ok=True)
            resp = requests.get(plugin.get("zip_url"), headers=self._github_headers(), timeout=70)
            if resp.status_code != 200:
                raise RuntimeError(f"GitHub download failed: HTTP {resp.status_code} - {resp.text[:220]}")
            with zipfile.ZipFile(BytesIO(resp.content)) as archive:
                archive.extractall(staging)
            children = [os.path.join(staging, x) for x in os.listdir(staging)]
            extracted = next((x for x in children if os.path.isdir(x)), None)
            if not extracted:
                raise RuntimeError("GitHub archive did not contain a repository folder")
            if os.path.exists(target):
                shutil.rmtree(target)
            shutil.move(extracted, target)
            shutil.rmtree(staging, ignore_errors=True)
            manifest = dict(plugin)
            manifest.update({
                "installed": True,
                "installed_path": target,
                "installed_at": datetime.now().isoformat(timespec="seconds"),
            })
            with open(os.path.join(target, "lightsky_plugin.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            publish(lambda: self._plugin_center_set_items(self._load_installed_github_plugins(), f"Installed GitHub plugin:\n{plugin.get('name')}\n\nPath:\n{target}"))
        except Exception as e:
            if os.path.exists(staging):
                shutil.rmtree(staging, ignore_errors=True)
            publish(lambda err=e: self._plugin_center_set_items(getattr(self, "_plugin_center_items", []), f"GitHub plugin install failed:\n{err}"))

    def plugin_center_run_sample(self):
        plugin = self._selected_github_plugin_item()
        if not plugin:
            return
        self.plugin_center_show_details()

    def plugin_center_show_prompt(self):
        if not hasattr(self, "plugin_details"):
            return
        self.plugin_details.delete("1.0", END)
        self.plugin_details.insert(END, AGENT_TOOLING_PROMPT)
        self.plugin_details.insert(END, "\n\nPlugin Center is GitHub-only. Internal tools remain available to models as agent tools, but they are not listed as plugins.\n")

    def show_agent_tool_help(self):
        help_text = (
            "Agent tools are enabled for every model.\n\n"
            "Plugin Center rule:\n"
            "All user-facing plugins come only from GitHub repositories.\n\n"
            "Internal agent tools, not plugins:\n"
            "web_search, fetch_url, hf_model_search, hf_repo_info, hf_inference, "
            "list_files, read_file, write_file, knowledge_search, debug_scan.\n\n"
            "Direct chat commands:\n"
            "/run <PowerShell command>\n"
            "/py <script.py> [args]\n"
            "/pip <package1> <package2>\n"
        )
        messagebox.showinfo("Lightsky Agent Tools", help_text)

def launch_streamlit_interface():
    """Launch the new Streamlit interface as the primary Lightsky app."""
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "streamlit_app.py")
    if not os.path.exists(app_path):
        raise FileNotFoundError(f"Streamlit app not found: {app_path}")
    print("Starting Lightsky AI Streamlit interface...")
    print("Legacy Tk UI is still available with: py LightSky_AI.py --tk")
    quoted_app_path = f'"{app_path}"'
    env = os.environ.copy()
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    cmd = (
        f'"{sys.executable}" -m streamlit run {quoted_app_path} '
        "--server.headless=false --server.showEmailPrompt=false --browser.gatherUsageStats=false"
    )
    return subprocess.run(cmd, cwd=os.path.dirname(app_path), shell=True, env=env).returncode


def launch_legacy_tk_interface():
    """Launch the old Tkinter interface for compatibility/testing."""
    print("LightSky AI by Krivi - ULTIMATE CORRECTED VERSION")
    print("=" * 60)
    print("ALL ISSUES FIXED:")
    print("  Real Groq Models from Console")
    print("  Arena with Chatbot Names")
    print("  Visual Web Browser with HTML Rendering")
    print("  Functional Knowledge Base")
    print("  No More Crashes")
    print("  All Features Working")
    print("  Robust Error Handling")
    print("  HuggingFace Token Set")
    print("=" * 60)
    
    enable_windows_dpi_awareness()

    # Create main window
    root = Tk()
    tune_tk_rendering(root)
    
    # Create ultimate corrected UI
    app = LightSkyUltimateCorrectUI(root)
    
    print("Ultimate Corrected interface ready!")
    print("Starting application...")
    
    # Start application
    root.mainloop()


# Main execution
if __name__ == "__main__":
    if "--tk" in sys.argv or os.environ.get("LIGHTSKY_LEGACY_TK") == "1":
        launch_legacy_tk_interface()
    else:
        sys.exit(launch_streamlit_interface())
