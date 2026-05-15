Unicode true

!define APP_NAME "Lightsky AI pro by Krivi"
!define SRC_DIR ".."
!define DIST_DIR "..\dist"

Name "${APP_NAME}"
OutFile "${DIST_DIR}\LightskyAIPro.exe"
InstallDir "$LOCALAPPDATA\Lightsky AI pro by Krivi"
RequestExecutionLevel user
SilentInstall silent
AutoCloseWindow true
ShowInstDetails nevershow

Icon "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"

Section "Run Lightsky AI pro"
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer

  File "${SRC_DIR}\streamlit_app.py"
  File "${SRC_DIR}\lightsky_core.py"
  File "${SRC_DIR}\desktop_launcher.py"
  File "${SRC_DIR}\requirements.txt"
  File "${SRC_DIR}\README.md"
  File "${SRC_DIR}\LICENSE"
  File "${SRC_DIR}\installer\LaunchLightskyAI.cmd"
  File "${SRC_DIR}\installer\README_INSTALL.txt"

  SetOutPath "$INSTDIR\.streamlit"
  File "${SRC_DIR}\.streamlit\config.toml"

  SetOutPath "$INSTDIR"
  IfFileExists "$INSTDIR\.venv\Scripts\pythonw.exe" venv_ready
    nsExec::ExecToStack 'py -m venv "$INSTDIR\.venv"'
    Pop $0
    Pop $1
    StrCmp $0 0 +3
      MessageBox MB_ICONSTOP "Python launcher was not found or the private environment could not be created. Install Python 3.11+ with the py launcher enabled."
      Abort

  venv_ready:
  IfFileExists "$INSTDIR\.venv\.lightsky_deps_installed" deps_ready
    nsExec::ExecToStack '"$INSTDIR\.venv\Scripts\python.exe" -m pip install --upgrade pip'
    Pop $0
    Pop $1
    StrCmp $0 0 +3
      MessageBox MB_ICONSTOP "Could not update pip for Lightsky AI."
      Abort
    nsExec::ExecToStack '"$INSTDIR\.venv\Scripts\python.exe" -m pip install -r "$INSTDIR\requirements.txt"'
    Pop $0
    Pop $1
    StrCmp $0 0 +3
      MessageBox MB_ICONSTOP "Could not install Lightsky AI dependencies."
      Abort
    FileOpen $2 "$INSTDIR\.venv\.lightsky_deps_installed" w
    FileWrite $2 "installed"
    FileClose $2

  deps_ready:
  Exec '"$INSTDIR\.venv\Scripts\pythonw.exe" "$INSTDIR\desktop_launcher.py"'
SectionEnd
