Unicode true

!define APP_NAME "Lightsky AI pro by Krivi"
!define DIST_DIR "..\dist"

Name "${APP_NAME}"
OutFile "${DIST_DIR}\LightskyAIProLauncher.exe"
RequestExecutionLevel user
SilentInstall silent
AutoCloseWindow true
ShowInstDetails nevershow

Icon "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"

Section "Launch Lightsky AI pro"
  CreateDirectory "$LOCALAPPDATA\Lightsky AI pro by Krivi\Runtime"
  SetOutPath "$LOCALAPPDATA\Lightsky AI pro by Krivi\Runtime"

  IfFileExists "$LOCALAPPDATA\Lightsky AI pro by Krivi\Runtime\.venv\Scripts\pythonw.exe" venv_ready
    MessageBox MB_OK "Lightsky AI is preparing its private Python environment. This can take a few minutes on first launch."
    nsExec::ExecToStack 'py -m venv "$LOCALAPPDATA\Lightsky AI pro by Krivi\Runtime\.venv"'
    Pop $0
    Pop $1
    StrCmp $0 0 +3
      MessageBox MB_ICONSTOP "Python launcher was not found or the private environment could not be created. Install Python 3.11+ with the py launcher enabled."
      Abort

  venv_ready:
  IfFileExists "$LOCALAPPDATA\Lightsky AI pro by Krivi\Runtime\.venv\.lightsky_deps_installed" deps_ready
    MessageBox MB_OK "Lightsky AI is installing its app dependencies. This can take a few minutes on first launch."
    nsExec::ExecToStack '"$LOCALAPPDATA\Lightsky AI pro by Krivi\Runtime\.venv\Scripts\python.exe" -m pip install --upgrade pip'
    Pop $0
    Pop $1
    StrCmp $0 0 +3
      MessageBox MB_ICONSTOP "Could not update pip for Lightsky AI."
      Abort
    nsExec::ExecToStack '"$LOCALAPPDATA\Lightsky AI pro by Krivi\Runtime\.venv\Scripts\python.exe" -m pip install -r "$EXEDIR\requirements.txt"'
    Pop $0
    Pop $1
    StrCmp $0 0 +3
      MessageBox MB_ICONSTOP "Could not install Lightsky AI dependencies."
      Abort
    FileOpen $2 "$LOCALAPPDATA\Lightsky AI pro by Krivi\Runtime\.venv\.lightsky_deps_installed" w
    FileWrite $2 "installed"
    FileClose $2

  deps_ready:
  Exec '"$LOCALAPPDATA\Lightsky AI pro by Krivi\Runtime\.venv\Scripts\pythonw.exe" "$EXEDIR\desktop_launcher.py"'
SectionEnd
