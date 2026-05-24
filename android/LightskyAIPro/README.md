# Lightsky AI Pro for Android

Native Android WebView shell for Lightsky AI pro by Krivi.

## Build Debug APK

Run from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File android/LightskyAIPro/build-apk.ps1
```

Output:

```text
dist/LightskyAIPro-android-debug.apk
```

The script uses the installed Android SDK directly. If `javac` is missing, it downloads the Eclipse Java compiler into `android/LightskyAIPro/tools/`.

## Install On A Connected Device

Enable USB debugging, connect the phone, then run:

```powershell
powershell -ExecutionPolicy Bypass -File android/LightskyAIPro/install-apk.ps1
```

## App

- Opens `https://lightsky-ai-krivi.streamlit.app/?startup=done`
- Supports JavaScript, DOM storage, Android downloads, back navigation, file chooser uploads, and external links.
- Package name: `com.lightsky.aipro`
