# Lightsky AI pro by Krivi

Streamlit-first Lightsky AI app with chat, arena, visual browser, Look & Take,
image generation, GitHub plugin discovery, internal testing, and LS 5.1 debug
tools.

## Run Locally

```powershell
py -m pip install -r requirements.txt
py LightSky_AI.py
```

The Streamlit app runs on:

```text
http://localhost:8501/
```

The legacy Tk UI is still available only for local compatibility:

```powershell
py LightSky_AI.py --tk
```

## Hosted Streamlit

Use `streamlit_app.py` as the entrypoint. The hosted app must not import Tk.
Provider keys should be set as environment variables or Streamlit secrets.

Supported secret names:

- `GROQ_API_KEY` or `GROQ_API_KEYS`
- `COMETAPI_API_KEY`
- `HF_TOKEN` or `HUGGINGFACE_TOKEN`
- `XAI_API_KEY`
- `NVIDIA_API_KEY`

Do not commit `.streamlit/secrets.toml`, logs, downloads, generated images, or
local cookies.
