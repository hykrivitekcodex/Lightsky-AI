# Lightsky AI pro by Krivi

Streamlit-first Lightsky AI app with chat image generation, arena, visual
browser, Look & Take, GitHub plugin discovery, internal testing, and LS 5.1
debug tools. Labs collaboration is shown at `https://lightsky-ai-krivi.streamlit.app/labs`.

## Run Locally

```powershell
py -m pip install -r requirements.txt
py -m streamlit run streamlit_app.py
```

The Streamlit app runs on:

```text
http://localhost:8501/
```

## Hosted Streamlit

Use `streamlit_app.py` as the entrypoint. The hosted app must not import Tk.
Provider keys should be set as environment variables or Streamlit secrets.
For local desktop use, you can also open Settings -> Provider keys and save a
Gemini key to the local ignored `lightsky_provider_keys.json` file.

Supported secret names:

- `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- `HF_TOKEN` or `HUGGINGFACE_TOKEN`
- `XAI_API_KEY`
- `NVIDIA_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`

For Google sign-in, create a Google OAuth client for a web application and set
`GOOGLE_REDIRECT_URI` to the exact app URL, for example
`http://localhost:8501/` or your hosted Streamlit URL.

Email/password sign-in stores local account records in `lightsky_accounts.json`
using salted PBKDF2 password hashes. Browser refresh persistence uses
device-specific session tokens saved in `lightsky_sessions.json`. Both files are
ignored by git.

Do not commit `.streamlit/secrets.toml`, `lightsky_provider_keys.json`, logs,
downloads, generated images, or local cookies.

## Windows Installer

The NSIS installer is built from `installer/LightskyAIPro.nsi`:

```powershell
& "C:\Program Files (x86)\NSIS\makensis.exe" installer\LightskyAIPro.nsi
```

The generated installer is `dist/LightskyAIProSetup.exe`. It installs the app
per user, creates Start Menu/Desktop shortcuts, and launches Streamlit through
`LaunchLightskyAI.cmd`.

## Android APK

The Android WebView shell lives in `android/LightskyAIPro` and opens the hosted
Lightsky app with downloads, file picker uploads, back navigation, and an
offline reload screen.

Build the debug APK:

```powershell
powershell -ExecutionPolicy Bypass -File android/LightskyAIPro/build-apk.ps1
```

Output:

```text
dist/LightskyAIPro-android-debug.apk
```

Install on a connected Android device:

```powershell
powershell -ExecutionPolicy Bypass -File android/LightskyAIPro/install-apk.ps1
```
