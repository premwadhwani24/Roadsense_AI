"""
auto_sync_to_python_ai.py
Copy all images from a folder into python_ai/uploads/images
"""

import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE, "python_ai", "uploads", "images")

VALID_EXT = [".jpg", ".jpeg", ".png", ".bmp"]


def sync_from(source_dir):
    if not os.path.exists(source_dir):
        print("[ERROR] Source folder does not exist")
        return

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    copied = 0

    for f in os.listdir(source_dir):
        ext = os.path.splitext(f)[1].lower()
        if ext not in VALID_EXT:
            continue

        src = os.path.join(source_dir, f)
        dst = os.path.join(UPLOAD_DIR, f)

        if os.path.exists(dst):
            print(f"[SKIP] Already exists: {f}")
            continue

        shutil.copy2(src, dst)
        copied += 1
        print(f"[COPIED] {f}")

    print(f"\nSync complete ✓ ({copied} new images added)")


if __name__ == "__main__":
    folder = input("Enter folder path to sync images: ").strip()
    sync_from(folder)
