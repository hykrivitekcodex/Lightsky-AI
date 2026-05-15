from __future__ import annotations

import json
import plistlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
IOS_ROOT = REPO_ROOT / "ios" / "LightskyAIPro"
APP_ROOT = IOS_ROOT / "LightskyAIPro"

REQUIRED_FILES = [
    IOS_ROOT / "README.md",
    IOS_ROOT / "Package-Source.ps1",
    IOS_ROOT / "Validate-Source.ps1",
    APP_ROOT / "Info.plist",
    APP_ROOT / "LightskyAIProApp.swift",
    APP_ROOT / "AppConfig.swift",
    APP_ROOT / "RootView.swift",
    APP_ROOT / "LightskyWebView.swift",
    APP_ROOT / "WebAppScreen.swift",
    APP_ROOT / "LabsScreen.swift",
    APP_ROOT / "DownloadsScreen.swift",
    APP_ROOT / "SettingsScreen.swift",
    APP_ROOT / "BrandComponents.swift",
    APP_ROOT / "Assets.xcassets" / "Contents.json",
    APP_ROOT / "Assets.xcassets" / "AccentColor.colorset" / "Contents.json",
    APP_ROOT / "Assets.xcassets" / "LaunchBackground.colorset" / "Contents.json",
    APP_ROOT / "Assets.xcassets" / "AppIcon.appiconset" / "Contents.json",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_required_files() -> None:
    missing = [str(path.relative_to(REPO_ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        fail("Missing required files: " + ", ".join(missing))


def check_json_files() -> None:
    for path in (APP_ROOT / "Assets.xcassets").rglob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"Invalid JSON in {path.relative_to(REPO_ROOT)}: {exc}")


def check_plist() -> None:
    try:
        info = plistlib.loads((APP_ROOT / "Info.plist").read_bytes())
    except Exception as exc:
        fail(f"Invalid Info.plist: {exc}")

    expected = {
        "CFBundleDisplayName": "Lightsky AI",
        "CFBundleIdentifier": "$(PRODUCT_BUNDLE_IDENTIFIER)",
    }
    for key, value in expected.items():
        if info.get(key) != value:
            fail(f"Info.plist {key} expected {value!r}, got {info.get(key)!r}")

    launch_screen = info.get("UILaunchScreen")
    if not isinstance(launch_screen, dict):
        fail("Info.plist UILaunchScreen must be a dictionary")
    if launch_screen.get("UIColorName") != "LaunchBackground":
        fail("Info.plist launch screen must use the LaunchBackground color asset")


def check_swift_sources() -> None:
    swift_files = sorted(APP_ROOT.glob("*.swift"))
    if not swift_files:
        fail("No Swift source files found")

    app_entry = APP_ROOT / "LightskyAIProApp.swift"
    entry_text = app_entry.read_text(encoding="utf-8")
    if "@main" not in entry_text:
        fail("LightskyAIProApp.swift must contain the app entry point")

    config = (APP_ROOT / "AppConfig.swift").read_text(encoding="utf-8")
    expected_values = [
        "lightsky-ai-krivi.streamlit.app",
        "github.com/hykrivitekcodex/Lightsky-AI/releases/tag/v3.0",
        "krivi.ezhil@gmail.com",
    ]
    for value in expected_values:
        if value not in config:
            fail(f"AppConfig.swift missing expected value: {value}")


def check_app_icons() -> None:
    icon_root = APP_ROOT / "Assets.xcassets" / "AppIcon.appiconset"
    icon_json = json.loads((icon_root / "Contents.json").read_text(encoding="utf-8"))
    images = icon_json.get("images", [])
    if not images:
        fail("AppIcon asset catalog has no images")

    for image in images:
        filename = image.get("filename")
        if not filename:
            continue
        path = icon_root / filename
        if not path.exists():
            fail(f"App icon file missing: {path.relative_to(REPO_ROOT)}")
        if path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            fail(f"App icon is not a PNG: {path.relative_to(REPO_ROOT)}")


def main() -> None:
    check_required_files()
    check_json_files()
    check_plist()
    check_swift_sources()
    check_app_icons()

    print("OK: iOS source validation passed.")
    print("Created package can be shared as source; it is not an installable phone binary.")


if __name__ == "__main__":
    main()
