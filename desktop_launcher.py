import os
import socket
import subprocess
import sys
import time
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
APP_TITLE = "Lightsky AI pro by Krivi"
HOST = "127.0.0.1"
PORT_START = int(os.environ.get("LIGHTSKY_PORT", "8501"))
PORT_LIMIT = PORT_START + 20
DATA_DIR = Path(
    os.environ.get(
        "LIGHTSKY_USER_DATA_DIR",
        str(Path(os.environ.get("LOCALAPPDATA", str(APP_DIR))) / "Lightsky AI pro by Krivi" / "UserData"),
    )
).resolve()


def candidate_app_browsers():
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    program_files = os.environ.get("PROGRAMFILES", "")
    program_files_x86 = os.environ.get("PROGRAMFILES(X86)", "")
    return [
        Path(local_app_data) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(program_files_x86) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(program_files) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(program_files) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(program_files_x86) / "Google" / "Chrome" / "Application" / "chrome.exe",
    ]


def find_app_browser():
    for candidate in candidate_app_browsers():
        if candidate and candidate.exists():
            return candidate
    return None


def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((HOST, port)) == 0


def find_free_port():
    for port in range(PORT_START, PORT_LIMIT):
        if not is_port_open(port):
            return port
    raise RuntimeError("No free local port found for Lightsky AI.")


def wait_for_server(port, timeout=45):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_port_open(port):
            return True
        time.sleep(0.35)
    return False


def start_streamlit(port):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    log_dir = DATA_DIR / "runtime_logs"
    log_dir.mkdir(exist_ok=True)
    stdout = open(log_dir / "streamlit_stdout.log", "a", encoding="utf-8")
    stderr = open(log_dir / "streamlit_stderr.log", "a", encoding="utf-8")
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP_DIR / "streamlit_app.py"),
        "--server.headless",
        "true",
        "--server.port",
        str(port),
        "--browser.gatherUsageStats",
        "false",
    ]
    env = os.environ.copy()
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    env["LIGHTSKY_USER_DATA_DIR"] = str(DATA_DIR)
    return subprocess.Popen(command, cwd=APP_DIR, env=env, stdout=stdout, stderr=stderr)


def open_native_app_window(url):
    app_browser = find_app_browser()
    if not app_browser:
        raise RuntimeError("Microsoft Edge or Chrome is required for the Lightsky AI desktop window.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    profile_dir = DATA_DIR / "native_window_profile"
    profile_dir.mkdir(exist_ok=True)
    command = [
        str(app_browser),
        f"--app={url}",
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--disable-translate",
        "--window-size=1320,860",
    ]
    return subprocess.Popen(command, cwd=APP_DIR)


def main():
    os.chdir(APP_DIR)
    port = find_free_port()
    process = start_streamlit(port)
    if not wait_for_server(port):
        process.terminate()
        raise RuntimeError("Lightsky AI did not start. Check runtime_logs for details.")

    url = f"http://{HOST}:{port}/?startup=done"
    window_process = open_native_app_window(url)
    try:
        window_process.wait()
    finally:
        process.terminate()


if __name__ == "__main__":
    main()
