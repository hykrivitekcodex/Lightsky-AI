$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ProjectDir "..\..")
$ApkPath = Join-Path $RepoRoot "dist\LightskyAIPro-android-debug.apk"
$SdkRoot = $env:ANDROID_SDK_ROOT

if (-not $SdkRoot) {
    $SdkRoot = $env:ANDROID_HOME
}
if (-not $SdkRoot) {
    $SdkRoot = Join-Path $env:LOCALAPPDATA "Android\Sdk"
}

$Adb = Join-Path $SdkRoot "platform-tools\adb.exe"
if (-not (Test-Path $Adb)) {
    throw "adb.exe was not found. Install Android SDK platform-tools."
}
if (-not (Test-Path $ApkPath)) {
    throw "APK not found. Run android/LightskyAIPro/build-apk.ps1 first."
}

& $Adb devices
& $Adb install -r $ApkPath
