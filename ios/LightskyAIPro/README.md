# Lightsky AI pro for iOS

Source package for the Lightsky AI pro by Krivi mobile app.

## What It Does

- Opens Lightsky AI in a dedicated mobile app web view.
- Keeps a native-style tab shell for Chat, Labs, Downloads, and Settings.
- Uses the Lightsky sparkle branding and release download links.
- Points at the hosted app: `https://lightsky-ai-krivi.streamlit.app/`

## Windows Source Check

Run this on Windows to validate the source package:

```powershell
powershell -ExecutionPolicy Bypass -File ios/LightskyAIPro/Validate-Source.ps1
```

This checks source files, asset catalogs, app icons, Info.plist, and app configuration.

## VS Code Workflow

Open the repository folder in VS Code and run:

```text
Terminal > Run Task > Lightsky iOS: validate and package
```

That task validates this mobile source package and rebuilds `dist/LightskyAIPro-iOS-source.zip`.

## Make A Source Zip On Windows

Run:

```powershell
powershell -ExecutionPolicy Bypass -File ios/LightskyAIPro/Package-Source.ps1
```

The zip is written to:

```text
dist/LightskyAIPro-iOS-source.zip
```

## Notes

This folder is a source package. It does not include an installable phone binary.
