import os

BASE = os.path.dirname(os.path.abspath(__file__))

folders = [
    BASE,
    os.path.join(BASE, "api"),
    os.path.join(BASE, "models"),
    os.path.join(BASE, "utils"),
    os.path.join(BASE, "uploads"),
    os.path.join(BASE, "uploads", "images"),
    os.path.join(BASE, "uploads", "sensor"),
]

print("\nAUTO REPAIR IMPORTS — FIXING __init__.py FILES\n")

for f in folders:
    init_file = os.path.join(f, "__init__.py")
    if not os.path.exists(init_file):
        open(init_file, "w").close()
        print("✔ Created:", init_file)
    else:
        print("✔ Exists:", init_file)

print("\nALL IMPORT PATHS FIXED SUCCESSFULLY.\n")
