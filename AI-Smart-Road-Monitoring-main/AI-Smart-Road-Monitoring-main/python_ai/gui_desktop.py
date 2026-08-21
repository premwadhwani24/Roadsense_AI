import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import requests
import json
import os

API_BASE = "http://127.0.0.1:5000"


class SmartRoadGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("AI Smart Road Monitoring - API GUI")
        self.root.geometry("1200x720")
        self.root.configure(bg="#eef2f7")

        self.images = []
        self.sensor_file = None
        self.preview_img = None

        self.build_ui()

    # ================= UI =================
    def build_ui(self):

        # ---------- Header ----------
        header = tk.Frame(self.root, bg="#1f6feb", height=60)
        header.pack(fill="x")

        tk.Label(
            header,
            text="🚧 AI Smart Road Monitoring System",
            font=("Segoe UI", 20, "bold"),
            fg="white",
            bg="#1f6feb"
        ).pack(pady=10)

        # ---------- Buttons ----------
        btn_frame = tk.Frame(self.root, bg="#eef2f7")
        btn_frame.pack(pady=10)

        def color_button(text, color, cmd, col):
            tk.Button(
                btn_frame,
                text=text,
                bg=color,
                fg="white",
                font=("Segoe UI", 10, "bold"),
                width=20,
                relief="flat",
                command=cmd
            ).grid(row=0, column=col, padx=6)

        color_button("📂 Pick Images", "#16a34a", self.pick_images, 0)
        color_button("📊 Pick Sensor CSV", "#0ea5e9", self.pick_sensor, 1)
        color_button("🧠 Upload Images & Predict", "#7c3aed", self.upload_images, 2)
        color_button("📈 Upload Sensor & Analyze", "#f97316", self.upload_sensor, 3)
        color_button("✅ Check API Status", "#dc2626", self.check_status, 4)

        # ---------- Main Panels ----------
        main = tk.Frame(self.root, bg="#eef2f7")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # ---------- Left Panel ----------
        left = tk.LabelFrame(
            main, text="📷 Selected Images",
            bg="white", fg="#1f2937",
            font=("Segoe UI", 10, "bold"),
            width=260
        )
        left.pack(side="left", fill="y", padx=5)

        self.image_list = tk.Listbox(left, height=22)
        self.image_list.pack(fill="both", expand=True)
        self.image_list.bind("<<ListboxSelect>>", self.show_preview)

        # ---------- Center Preview ----------
        center = tk.LabelFrame(
            main, text="🖼 Image Preview",
            bg="white", fg="#1f2937",
            font=("Segoe UI", 10, "bold")
        )
        center.pack(side="left", fill="both", expand=True, padx=5)

        self.preview_label = tk.Label(center, bg="white")
        self.preview_label.pack(expand=True)

        # ---------- Right Panel ----------
        right = tk.LabelFrame(
            main, text="📡 Sensor CSV",
            bg="white", fg="#1f2937",
            font=("Segoe UI", 10, "bold"),
            width=250
        )
        right.pack(side="left", fill="y", padx=5)

        self.sensor_label = tk.Label(
            right,
            text="No file selected",
            fg="#64748b",
            bg="white",
            font=("Segoe UI", 10)
        )
        self.sensor_label.pack(pady=30)

        # ---------- API Response (TABLE) ----------
        output_frame = tk.LabelFrame(
            self.root, text="📊 API Response (Table View)",
            bg="white", fg="#1f2937",
            font=("Segoe UI", 10, "bold")
        )
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Field", "Value")
        self.table = ttk.Treeview(
            output_frame,
            columns=columns,
            show="headings",
            height=8
        )

        self.table.heading("Field", text="Field")
        self.table.heading("Value", text="Value")

        self.table.column("Field", width=220, anchor="w")
        self.table.column("Value", width=700, anchor="w")

        self.table.pack(fill="both", expand=True)

        # ---------- Status Bar ----------
        self.status = tk.Label(
            self.root,
            text="Status: READY",
            bg="#1e293b",
            fg="white",
            anchor="w",
            padx=10
        )
        self.status.pack(fill="x", side="bottom")

    # ================= Actions =================
    def pick_images(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Images", "*.jpg *.png *.jpeg")]
        )
        if files:
            self.images = list(files)
            self.image_list.delete(0, tk.END)
            for f in self.images:
                self.image_list.insert(tk.END, os.path.basename(f))

    def pick_sensor(self):
        file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file:
            self.sensor_file = file
            self.sensor_label.config(text=os.path.basename(file))

    def show_preview(self, event):
        if not self.image_list.curselection():
            return
        index = self.image_list.curselection()[0]
        path = self.images[index]

        img = Image.open(path)
        img.thumbnail((500, 350))
        self.preview_img = ImageTk.PhotoImage(img)
        self.preview_label.config(image=self.preview_img)

    def upload_images(self):
        if not self.images:
            messagebox.showwarning("Warning", "Please select images")
            return
        try:
            files = [("image", open(p, "rb")) for p in self.images]
            r = requests.post(f"{API_BASE}/api/predict_potholes", files=files)
            self.show_response(r)
        except Exception as e:
            self.show_error(e)

    def upload_sensor(self):
        if not self.sensor_file:
            messagebox.showwarning("Warning", "Please select sensor CSV")
            return
        try:
            with open(self.sensor_file, "rb") as f:
                r = requests.post(
                    f"{API_BASE}/api/analyze_surface",
                    files={"sensor": f}
                )
            self.show_response(r)
        except Exception as e:
            self.show_error(e)

    def check_status(self):
        try:
            r = requests.get(f"{API_BASE}/api/status")
            self.show_response(r)
        except Exception as e:
            self.show_error(e)

    # ================= Helpers =================
    def show_response(self, response):
        for row in self.table.get_children():
            self.table.delete(row)

        try:
            data = response.json()

            if isinstance(data, list):
                for item in data:
                    for key, value in item.items():
                        self.table.insert("", "end", values=(key, value))
                    self.table.insert("", "end", values=("", ""))

            elif isinstance(data, dict):
                for key, value in data.items():
                    self.table.insert("", "end", values=(key, value))

            self.status.config(text="Status: SUCCESS")

        except Exception as e:
            self.table.insert("", "end", values=("ERROR", str(e)))
            self.status.config(text="Status: ERROR")

    def show_error(self, e):
        for row in self.table.get_children():
            self.table.delete(row)
        self.table.insert("", "end", values=("ERROR", str(e)))
        self.status.config(text="Status: ERROR")


# ================= Run =================
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartRoadGUI(root)
    root.mainloop()
