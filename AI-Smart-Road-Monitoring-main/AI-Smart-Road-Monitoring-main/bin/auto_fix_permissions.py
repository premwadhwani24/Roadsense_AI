"""
auto_fix_permissions.py
Fix folder permissions for Windows + Linux/Mac
"""

import os
import platform
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
TARGETS = [
    "python_ai",
    "python_ai/uploads",
    "python_ai/uploads/images",
    "python_ai/uploads/sensor",
    "python_ai/logs",
    "python_ai/models"
]


def windows_permissions(path):
    try:
        subprocess.run(
            ["icacls", path, "/grant", "Everyone:(OI)(CI)F"],
            capture_output=True,
            text=True
        )
        print(f"[OK] Windows permissions fixed → {path}")
    except Exception as e:
        print(f"[ERROR] Windows permission fix failed: {e}")


def linux_permissions(path):
    try:
        subprocess.run(
            ["chmod", "-R", "755", path],
            capture_output=True,
            text=True
        )
        print(f"[OK] Linux/Mac permissions fixed → {path}")
    except Exception as e:
        print(f"[ERROR] Linux/Mac permission fix failed: {e}")


def main():
    system = platform.system().lower()
    print(f"\nDetected OS → {system.upper()}")

    for folder in TARGETS:
        full = os.path.join(BASE, folder)
        if not os.path.exists(full):
            print(f"[SKIP] Missing folder → {full}")
            continue

        if "windows" in system:
            windows_permissions(full)
        else:
            linux_permissions(full)

    print("\nPermission repair complete ✓")


if __name__ == "__main__":
    main()
