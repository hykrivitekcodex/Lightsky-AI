Lightsky AI pro by Krivi

This installer packages the Streamlit app and a Windows launcher.

First launch:
1. The launcher creates a private .venv inside the install folder.
2. It installs the packages from requirements.txt.
3. It opens http://127.0.0.1:8501/?startup=done and starts Streamlit.

Python requirement:
- Python 3.11+ with the Windows "py" launcher must be installed.

Private runtime data:
- lightsky_accounts.json and lightsky_sessions.json are created only on the user's machine.
- API keys should be set with environment variables or Streamlit secrets.
- Secrets, accounts, downloads, generated files, and sessions are not bundled in the installer.
