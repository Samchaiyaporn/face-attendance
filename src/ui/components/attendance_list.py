import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from datetime import datetime
from customtkinter import CTkImage  # เพิ่มการ import CTkImage
from ..styles import COLORS, FONTS  # สมมุติว่า styles ยังคงอยู่
import os

class AttendanceList(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=COLORS["background"], corner_radius=10)
        
        # Title
        # title = ctk.CTkLabel(self, text="Attendance List", font=FONTS["section_title"], text_color=COLORS["text"])
        # title.pack(anchor="w", padx=10, pady=(10, 0))

        # Scrollable Frame
        self.scrollable_frame = ctk.CTkFrame(self, fg_color=COLORS["background"])
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # เก็บภาพป้องกัน garbage collection
        self._image_refs = {}

    def add_entry(self, attendance_datas):
        """เพิ่มรายการเข้าเรียนแบบ Custom UI (ไม่ใช้ Treeview)"""
        
        # ลบ widget เดิมออกก่อน
        for widget in self.scrollable_frame.winfo_children():
            widget.pack_forget()


        for attendance_data in attendance_datas:
            print("Adding entry:", attendance_data)
            name = attendance_data.get("name", "Unknown")
            time = attendance_data.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            member = attendance_data.get("member_id", "Unknown")
            original_image = attendance_data.get("original_image", Image.new("RGB", (100, 150), "white"))
            capture_image = attendance_data.get("capture_image", Image.new("RGB", (100, 150), "white"))

            # สร้าง container สำหรับรายการ
           

            # เพิ่ม card ด้านบนสุด
            card = ctk.CTkFrame(self.scrollable_frame, fg_color=COLORS["white"], corner_radius=15)
            card.pack(pady=5, padx=5, fill="x")

            # ===== รูปภาพใบหน้า 2 รูป =====
            images_frame = ctk.CTkFrame(card, fg_color="transparent")
            images_frame.grid(row=0, column=0, padx=15, pady=15, sticky="w")

            ori_img = original_image.resize((100, 130))
            cap_img = capture_image.resize((100, 130))
            ori_ctk = CTkImage(ori_img, size=(100, 130))  # ใช้ CTkImage
            cap_ctk = CTkImage(cap_img, size=(100, 130))  # ใช้ CTkImage

            ctk.CTkLabel(images_frame, image=ori_ctk, text="").pack(side="left", padx=5)
            ctk.CTkLabel(images_frame, image=cap_ctk, text="").pack(side="left", padx=5)

            # ===== เครื่องหมายถูก =====
            # สร้างเส้นทางแบบสัมพัทธ์
            current_dir = os.path.dirname(__file__)
            check_icon_path = os.path.join(current_dir, "../images/check_icon.png")

            try:
                check_img = Image.open(check_icon_path).resize((25, 25))
                check_ctk = CTkImage(check_img, size=(25, 25))  # ใช้ CTkImage
                ctk.CTkLabel(card, image=check_ctk, text="").grid(row=0, column=2, padx=10)
            except FileNotFoundError:
                print(f"⚠️ ไม่พบ {check_icon_path}")
            # ===== ฝั่งซ้าย: ข้อความ =====
            text_frame = ctk.CTkFrame(card, fg_color="transparent")
            text_frame.grid(row=0, column=1, padx=10, pady=10, sticky="w")

            id_label = ctk.CTkLabel(text_frame, text=member, font=FONTS["header"], text_color=COLORS["blue"])
            id_label.pack(anchor="w")

            name_label = ctk.CTkLabel(text_frame, text=name, font=FONTS["section_title"], text_color=COLORS["text"])
            name_label.pack(anchor="w")

            time_label = ctk.CTkLabel(text_frame, text=time, font=FONTS["section_title"], text_color=COLORS["secondary"])
            time_label.pack(anchor="w")

            

    def clear(self):
        """ล้างรายการทั้งหมด"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self._image_refs.clear()