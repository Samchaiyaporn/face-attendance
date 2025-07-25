"""
Progress Dialog Component
แสดง loading progress และสถานะการทำงาน
"""

import tkinter as tk
import threading
import time


class ProgressDialog:
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
        self.progress_var = None
        self.status_var = None
        self.is_cancelled = False
        
    def show(self, title="กำลังโหลด...", message="กรุณารอสักครู่..."):
        """แสดง progress dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(title)
        self.dialog.geometry("450x200")
        self.dialog.resizable(False, False)
        
        # Center the dialog on screen (not parent)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center on screen instead of parent window
        self.dialog.update_idletasks()
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width // 2) - (450 // 2)
        y = (screen_height // 2) - (200 // 2)
        self.dialog.geometry(f"450x200+{x}+{y}")
        
        # Keep on top
        self.dialog.attributes('-topmost', True)
        
        # Create main frame
        main_frame = tk.Frame(self.dialog, bg="#f0f2f5", padx=30, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title label
        title_label = tk.Label(
            main_frame, 
            text=title,
            font=("Segoe UI", 16, "bold"),
            bg="#f0f2f5",
            fg="#1a1a1a"
        )
        title_label.pack(pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value=message)
        status_label = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 11),
            bg="#f0f2f5",
            fg="#555555"
        )
        status_label.pack(pady=(0, 20))
        
        # Progress bar (using Canvas instead of ttk.Progressbar)
        progress_frame = tk.Frame(main_frame, bg="#f0f2f5")
        progress_frame.pack(pady=(0, 15))
        
        self.progress_canvas = tk.Canvas(
            progress_frame,
            width=350,
            height=20,
            bg="#e0e0e0",
            highlightthickness=1,
            highlightcolor="#cccccc",
            relief="flat"
        )
        self.progress_canvas.pack()
        
        # Create progress bar rectangle
        self.progress_var = tk.DoubleVar()
        self.progress_rect = self.progress_canvas.create_rectangle(
            0, 0, 0, 20, 
            fill="#4CAF50", 
            outline=""
        )
        
        # Percentage label
        self.percent_var = tk.StringVar(value="0%")
        percent_label = tk.Label(
            main_frame,
            textvariable=self.percent_var,
            font=("Segoe UI", 10),
            bg="#f0f2f5",
            fg="#666666"
        )
        percent_label.pack()
        
        # Cancel button (optional)
        cancel_frame = tk.Frame(main_frame, bg="#f0f2f5")
        cancel_frame.pack(pady=(15, 0))
        
        cancel_btn = tk.Button(
            cancel_frame,
            text="ยกเลิก",
            command=self.cancel,
            font=("Segoe UI", 10),
            bg="#f44336",
            fg="white",
            relief="flat",
            padx=20,
            pady=5,
            cursor="hand2"
        )
        cancel_btn.pack()
        
        # Bind close event
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        
        return self.dialog
    
    def update_progress(self, message, progress):
        """อัปเดตความคืบหน้า"""
        if self.dialog and self.dialog.winfo_exists():
            try:
                self.status_var.set(message)
                self.progress_var.set(progress)
                self.percent_var.set(f"{int(progress)}%")
                
                # Update canvas progress bar
                if hasattr(self, 'progress_canvas') and hasattr(self, 'progress_rect'):
                    progress_width = int((progress / 100) * 350)
                    self.progress_canvas.coords(self.progress_rect, 0, 0, progress_width, 20)
                
                self.dialog.update()
            except tk.TclError:
                pass  # Dialog was destroyed
    
    def cancel(self):
        """ยกเลิกการทำงาน"""
        self.is_cancelled = True
        self.close()
    
    def close(self):
        """ปิด dialog"""
        if self.dialog and self.dialog.winfo_exists():
            try:
                self.dialog.grab_release()
                self.dialog.destroy()
            except tk.TclError:
                pass
        self.dialog = None
    
    def is_dialog_open(self):
        """ตรวจสอบว่า dialog ยังเปิดอยู่หรือไม่"""
        return self.dialog is not None and self.dialog.winfo_exists()


class LoadingManager:
    """จัดการ loading progress สำหรับการโหลดข้อมูลนักเรียน"""
    
    def __init__(self, parent):
        self.parent = parent
        self.progress_dialog = ProgressDialog(parent)
        self.loading_thread = None
        
    def start_loading(self, load_function, callback=None, title="กำลังโหลดข้อมูล", message="กรุณารอสักครู่..."):
        """เริ่มการโหลดข้อมูลพร้อม progress dialog"""
        
        # แสดง progress dialog
        self.progress_dialog.show(title, message)
        
        def progress_callback(message, progress):
            """Callback สำหรับอัปเดต progress"""
            if self.progress_dialog.is_dialog_open():
                self.progress_dialog.update_progress(message, progress)
            return not self.progress_dialog.is_cancelled
        
        def loading_worker():
            """Worker thread สำหรับโหลดข้อมูล"""
            try:
                result = load_function(progress_callback)
                
                # อัปเดต progress เป็น 100% ก่อนปิด
                if self.progress_dialog.is_dialog_open():
                    self.progress_dialog.update_progress("เสร็จสิ้นการโหลดข้อมูล!", 100)
                    time.sleep(0.5)  # แสดงผล 100% สักครู่
                
                # ปิด dialog หลังเสร็จสิ้น (เสมอ)
                if self.progress_dialog.is_dialog_open():
                    self.progress_dialog.close()
                
                # เรียก callback ถ้ามี
                if callback and not self.progress_dialog.is_cancelled:
                    self.parent.after(100, lambda: callback(result))
                        
            except Exception as e:
                print(f"Loading error: {e}")
                import traceback
                traceback.print_exc()
                
                # ปิด dialog แม้เกิด error
                if self.progress_dialog.is_dialog_open():
                    self.progress_dialog.update_progress(f"เกิดข้อผิดพลาด: {str(e)}", 0)
                    self.parent.after(2000, self.progress_dialog.close)  # ปิดหลัง 2 วินาที
        
        # เริ่ม loading thread
        self.loading_thread = threading.Thread(target=loading_worker, daemon=True)
        self.loading_thread.start()
    
    def is_loading(self):
        """ตรวจสอบว่ากำลัง loading อยู่หรือไม่"""
        return self.progress_dialog.is_dialog_open()
