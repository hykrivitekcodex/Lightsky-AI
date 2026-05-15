import io
import json
import os
import re
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

import LightSky_AI as core


APP_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = APP_DIR / "downloads"
PLUGIN_DIR = APP_DIR / "github_plugins"
GENERATED_DIR = APP_DIR / "generated_images"

for folder in (DOWNLOAD_DIR, PLUGIN_DIR, GENERATED_DIR):
    folder.mkdir(exist_ok=True)


st.set_page_config(
    page_title="Lightsky AI pro by krivi",
    page_icon="✨",
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
}
.stApp {
  background: radial-gradient(circle at 30% -10%, rgba(37,99,235,.10), transparent 34%),
              radial-gradient(circle at 90% 10%, rgba(219,39,119,.08), transparent 30%),
              var(--bg);
  color: var(--text);
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #eef2f8 0%, #f8fafc 100%);
  border-right: 1px solid var(--line);
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
.brand {
  display: flex;
  align-items: center;
  gap: 14px;
}
.logo {
  width: 48px;
  height: 48px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  color: #111827;
  background: linear-gradient(135deg, #ecfeff, #fdf2f8 45%, #eef2ff);
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
  border: 1px solid var(--line);
  border-radius: 22px;
  background: rgba(255,255,255,.88);
  box-shadow: 0 14px 34px rgba(17, 24, 39, .055);
}
.status-card {
  padding: 12px 14px;
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
  height: 4px;
  border-radius: 999px;
  margin: 12px 0 4px;
  background: linear-gradient(90deg, #67e8f9, #7c9cff, #c084fc, #f472b6, #fb7185, #facc15, #4ade80);
}
.stButton > button, .stDownloadButton > button {
  border-radius: 999px !important;
  border: 1px solid #d8e0ec !important;
  background: #ffffff !important;
  color: #172033 !important;
  font-weight: 700 !important;
  box-shadow: 0 8px 22px rgba(17, 24, 39, .055);
}
.stButton > button:hover, .stDownloadButton > button:hover {
  border-color: #b9c7dc !important;
  background: #f8fbff !important;
}
[data-testid="stChatInput"] {
  border-radius: 30px;
}
[data-testid="stChatInput"] textarea {
  border-radius: 30px !important;
  border: 1px solid #d8dde7 !important;
  box-shadow: 0 18px 48px rgba(17, 24, 39, .09) !important;
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


def status_cards(route):
    st.markdown(
        f"""
        <div class="status-grid">
          <div class="status-card"><div class="status-label">Model</div><div class="status-value">{model_clean(route['display'])}</div></div>
          <div class="status-card"><div class="status-label">Provider</div><div class="status-value">{provider_display(route['provider'])}</div></div>
          <div class="status-card"><div class="status-label">Web</div><div class="status-value">available to all models</div></div>
          <div class="status-card"><div class="status-label">Tools</div><div class="status-value">agent mode enabled</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header(route):
    st.markdown(
        f"""
        <div class="hero">
          <div class="brand">
            <div class="logo">✨</div>
            <div>
              <div class="brand-title">Lightsky AI pro</div>
              <div class="brand-subtitle">by Krivi and codex</div>
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

    prompt = st.chat_input("Ask for follow-up changes")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt, "source": "You", "sources": []})
        with st.spinner(f"✨ {provider_display(route['provider'])} / {model_clean(route['display'])} is thinking..."):
            response, sources = call_selected_model(prompt, route, max_tokens=760, web=True)
            response = append_sources(response or "The selected model did not return a response.", sources)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "source": f"{provider_display(route['provider'])} / {model_clean(route['display'])}",
            "sources": sources,
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
        with st.spinner("✨ Arena running..."):
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


def browser_screen(route):
    render_header(route)
    st.markdown("### Browser")
    target = st.text_input("URL or search", value="https://www.google.com")
    url = normalize_url(target)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.link_button("Open in real browser", url)
    with c2:
        st.caption("Embedded browsing works only when the site allows iframes.")
    components.iframe(url, height=680, scrolling=True)


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
            with st.spinner("✨ Generating image..."):
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
    cwd = st.text_input("Working directory", value=str(APP_DIR))
    file_path = st.text_input("Python file to run with py")
    args = st.text_input("Args", value="")
    command = st.text_area("Or PowerShell command", height=110)
    if st.button("Run Python file"):
        if not file_path:
            st.warning("Enter a Python file path.")
        else:
            cmd = ["py", file_path] + ([args] if args else [])
            result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=120)
            st.code((result.stdout or "") + (result.stderr or ""), language="text")
    if st.button("Run command"):
        if not command.strip():
            st.warning("Enter a command.")
        else:
            result = subprocess.run(["powershell", "-NoProfile", "-Command", command], cwd=cwd, text=True, capture_output=True, timeout=120)
            st.code((result.stdout or "") + (result.stderr or ""), language="text")


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
            with st.spinner("✨ Running selected model quick-fix..."):
                response, sources = call_selected_model(prompt.strip(), route, max_tokens=1100, web=False)
            st.markdown(response)


def settings_screen(route):
    render_header(route)
    st.markdown("### Settings")
    st.write("Launch legacy Tk UI with:")
    st.code("py LightSky_AI.py --tk", language="powershell")
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
        st.markdown("## ✨ Lightsky AI")
        st.caption("pro by Krivi and codex")
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
