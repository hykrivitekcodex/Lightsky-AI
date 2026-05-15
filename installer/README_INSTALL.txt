Lightsky AI pro by Krivi

This installer packages the Streamlit app and a Windows launcher in Program Files.

First launch:
1. The launcher creates a private .venv in LocalAppData.
2. It installs the packages from requirements.txt.
3. It opens Lightsky AI in a dedicated Windows app window and starts Streamlit in the background.

Python requirement:
- Python 3.11+ with the Windows "py" launcher must be installed.

Private runtime data:
- lightsky_accounts.json and lightsky_sessions.json are created only on the user's machine.
- Runtime data is stored under LocalAppData, not Program Files.
- API keys should be set with environment variables or Streamlit secrets.
- Secrets, accounts, downloads, generated files, and sessions are not bundled in the installer.
