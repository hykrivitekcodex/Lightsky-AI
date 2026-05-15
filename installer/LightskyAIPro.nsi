Unicode true

!define APP_NAME "Lightsky AI pro by Krivi"
!define APP_SHORT "Lightsky AI pro"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Krivi"
!define APP_REGKEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\LightskyAIPro"
!define SRC_DIR ".."
!define DIST_DIR "..\dist"
!define LAUNCHER_EXE "${DIST_DIR}\LightskyAIProLauncher.exe"

Name "${APP_NAME}"
OutFile "${DIST_DIR}\LightskyAIProSetup.exe"
InstallDir "$PROGRAMFILES64\Lightsky AI pro by Krivi"
RequestExecutionLevel admin
ShowInstDetails show
ShowUninstDetails show

!include "MUI2.nsh"
!include "x64.nsh"

!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\LightskyAIPro.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch Lightsky AI pro"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Lightsky AI pro" SecMain
  SetShellVarContext all
  ${IfNot} ${RunningX64}
    StrCpy $INSTDIR "$PROGRAMFILES\Lightsky AI pro by Krivi"
  ${EndIf}
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer

  File "${SRC_DIR}\streamlit_app.py"
  File "${SRC_DIR}\lightsky_core.py"
  File "${SRC_DIR}\desktop_launcher.py"
  File "${SRC_DIR}\requirements.txt"
  File "${SRC_DIR}\README.md"
  File "${SRC_DIR}\LICENSE"
  File "/oname=LightskyAIPro.exe" "${LAUNCHER_EXE}"
  File "${SRC_DIR}\installer\LaunchLightskyAI.cmd"
  File "${SRC_DIR}\installer\README_INSTALL.txt"

  SetOutPath "$INSTDIR\.streamlit"
  File "${SRC_DIR}\.streamlit\config.toml"

  SetOutPath "$INSTDIR"
  CreateDirectory "$SMPROGRAMS\${APP_SHORT}"
  CreateShortcut "$SMPROGRAMS\${APP_SHORT}\${APP_SHORT}.lnk" "$INSTDIR\LightskyAIPro.exe" "" "$INSTDIR\LightskyAIPro.exe" 0
  CreateShortcut "$SMPROGRAMS\${APP_SHORT}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  CreateShortcut "$DESKTOP\${APP_SHORT}.lnk" "$INSTDIR\LightskyAIPro.exe" "" "$INSTDIR\LightskyAIPro.exe" 0

  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "${APP_REGKEY}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "${APP_REGKEY}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "${APP_REGKEY}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKLM "${APP_REGKEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "${APP_REGKEY}" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegDWORD HKLM "${APP_REGKEY}" "NoModify" 1
  WriteRegDWORD HKLM "${APP_REGKEY}" "NoRepair" 1
SectionEnd

Section "Uninstall"
  SetShellVarContext all

  Delete "$DESKTOP\${APP_SHORT}.lnk"
  Delete "$SMPROGRAMS\${APP_SHORT}\${APP_SHORT}.lnk"
  Delete "$SMPROGRAMS\${APP_SHORT}\Uninstall.lnk"
  RMDir "$SMPROGRAMS\${APP_SHORT}"

  DeleteRegKey HKLM "${APP_REGKEY}"
  RMDir /r "$INSTDIR"
SectionEnd
