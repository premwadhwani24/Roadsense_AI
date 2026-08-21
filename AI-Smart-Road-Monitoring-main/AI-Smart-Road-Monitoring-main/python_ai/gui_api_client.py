import tkinter as tk
import requests
import webbrowser

API_BASE = "http://127.0.0.1:5000"


def check_status():
    try:
        r = requests.get(f"{API_BASE}/api/status", timeout=5)
        output.set(f"✅ API Status: {r.json()['status']}")
    except Exception as e:
        output.set(f"❌ Error: {e}")


def send_sensor():
    try:
        files = {
            "sensor": ("sample_sensor.csv", "vibration,speed\n5.2,40")
        }
        r = requests.post(f"{API_BASE}/api/analyze_surface", files=files, timeout=5)
        output.set(r.json())
    except Exception as e:
        output.set(f"❌ Error: {e}")


def open_dashboard():
    webbrowser.open(f"{API_BASE}/gui")


# ---------------- UI ----------------
root = tk.Tk()
root.title("AI Smart Road Monitoring – Mini Client")
root.geometry("520x360")
root.configure(bg="#f8fafc")

output = tk.StringVar()

tk.Label(
    root,
    text="🚦 Python AI Desktop Client",
    font=("Segoe UI", 16, "bold"),
    fg="#1f6feb",
    bg="#f8fafc"
).pack(pady=15)

def color_btn(text, color, cmd):
    tk.Button(
        root,
        text=text,
        bg=color,
        fg="white",
        font=("Segoe UI", 11, "bold"),
        width=32,
        relief="flat",
        command=cmd
    ).pack(pady=6)

color_btn("✅ Check API Status", "#22c55e", check_status)
color_btn("📡 Send Sensor Data", "#0ea5e9", send_sensor)
color_btn("🌐 Open Web Dashboard", "#f97316", open_dashboard)

tk.Label(
    root,
    textvariable=output,
    wraplength=480,
    fg="#0f172a",
    bg="#f8fafc",
    font=("Consolas", 10)
).pack(pady=20)

root.mainloop()
