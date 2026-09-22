#!/usr/bin/env python3
"""Launcher for Like-AI demo environment.

Usage:
    python Meta_pa.py

This script starts the backend and prints the URLs to open.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent


def main():
    print("Starting Like-AI backend...")
    env = os.environ.copy()
    env.setdefault("PORT", "8000")
    process = subprocess.Popen([sys.executable, str(BASE / "server.py")], cwd=str(BASE), env=env)
    time.sleep(2)
    print("\nLike-AI is running.")
    print("Backend: http://localhost:8000")
    print("Portal: http://localhost:8000/")
    print("Streamlit: streamlit run app.py")
    print("\nPress Ctrl+C to stop the backend process.")
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()
        print("\nStopped Like-AI backend.")


if __name__ == "__main__":
    main()
