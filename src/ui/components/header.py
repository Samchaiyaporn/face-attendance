import tkinter as tk
from PIL import Image, ImageTk
from ..styles import COLORS, FONTS
import os
import time

class Header(tk.Frame):
    def __init__(self, parent, camera_section=None):
        super().__init__(parent)
        self.configure(bg=COLORS["background"])
        self.camera_section = camera_section

        # Gradient Background
        self.gradient_canvas = tk.Canvas(self, height=80, width=1920, highlightthickness=0)
        self.gradient_canvas.pack(fill="both", expand=True)
        self.create_gradient(self.gradient_canvas, COLORS["gradient_start"], COLORS["gradient_end"])

        # Logo
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, "../images/logo-bdpath.png")
        image_path = os.path.normpath(image_path)
        image = Image.open(image_path)
        desired_height = 48
        w, h = image.size
        new_width = int(w * desired_height / h)
        image = image.resize((new_width, desired_height), Image.LANCZOS)
        self.logo_imgtk = ImageTk.PhotoImage(image)
        canvas_height = 80
        padding_y = (canvas_height - desired_height) // 2
        self.gradient_canvas.create_image(20, padding_y, anchor="nw", image=self.logo_imgtk)

        # User count display
        self.user_count_text_id = self.gradient_canvas.create_text(
            300, canvas_height // 2,
            anchor="w",
            text="กำลังโหลดข้อมูลผู้ใช้...",
            font=("Segoe UI", 12, "bold"),
            fill="white"
        )
        
        # Refresh button
        self.refresh_btn = tk.Button(
            self,
            text="🔄 รีเฟรชข้อมูล",
            command=self.refresh_users,
            font=("Segoe UI", 10),
            bg="#4CAF50",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        # Place refresh button on canvas (moved to right side of user count)
        self.gradient_canvas.create_window(650, canvas_height // 2, window=self.refresh_btn)

        # Time Display (real time & align right, วาดบน Canvas)
        # self.time_text_id = self.gradient_canvas.create_text(
        #     1900, canvas_height // 2,  # 1900 = 1920 - 20 (padding ขวา)
        #     anchor="e",
        #     text="",
        #     font=FONTS["time"],
        #     fill=COLORS["header_text"]
        # )
        # self.update_time()

    # def update_time(self):
    #     now = time.strftime("%H:%M:%S")
    #     self.gradient_canvas.itemconfig(self.time_text_id, text=now)
    #     self.after(1000, self.update_time)

    def create_gradient(self, canvas, start_color, end_color):
        """สร้าง gradient บน Canvas"""
        width = canvas.winfo_reqwidth()
        height = canvas.winfo_reqheight()
        steps = 100  # จำนวนขั้นของ gradient
        r1, g1, b1 = self.hex_to_rgb(start_color)
        r2, g2, b2 = self.hex_to_rgb(end_color)

        for i in range(steps):
            r = int(r1 + (r2 - r1) * i / steps)
            g = int(g1 + (g2 - g1) * i / steps)
            b = int(b1 + (b2 - b1) * i / steps)
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(0, i * height / steps, width, i * height / steps, fill=color, width=2)

    @staticmethod
    def hex_to_rgb(hex_color):
        """แปลงสี HEX เป็น RGB"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def update_user_count(self, count):
        """อัปเดตจำนวนผู้ใช้"""
        if hasattr(self, 'user_count_text_id'):
            text = f"👥 ผู้ใช้ในระบบ: {count} คน"
            self.gradient_canvas.itemconfig(self.user_count_text_id, text=text)
    
    def refresh_users(self):
        """รีเฟรชข้อมูลผู้ใช้"""
        if self.camera_section and hasattr(self.camera_section, 'refresh_user_data'):
            self.camera_section.refresh_user_data()
        else:
            print("Camera section not available for refresh")