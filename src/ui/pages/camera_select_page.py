"""
Camera Selection Page Component
หน้าเลือกกล้องพร้อมฟีเจอร์สแกนเครือข่าย
"""

import tkinter as tk
import threading
from utils.network_scanner import NetworkScanner


class CameraSelectPage(tk.Frame):
    def __init__(self, parent, on_select):
        super().__init__(parent, bg="#f0f2f5")
        self.on_select = on_select
        self.network_scanner = NetworkScanner()
        self.scanned_cameras = []
        self.scanning = False
        
        # Create gradient background
        self.gradient_canvas = tk.Canvas(self, highlightthickness=0, bg="#26659f")
        self.gradient_canvas.pack(fill="both", expand=True)
        self.gradient_canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Force initial update
        self.after(100, self.force_initial_update)
        
    def force_initial_update(self):
        """บังคับให้ canvas update ครั้งแรก"""
        if self.gradient_canvas.winfo_width() > 1 and self.gradient_canvas.winfo_height() > 1:
            self.update_display()
        else:
            self.after(50, self.force_initial_update)
        
    def on_canvas_configure(self, event):
        """Update when canvas is resized"""
        self.after_idle(self.update_display)
        
    def update_display(self):
        """Update display"""
        self.gradient_canvas.delete("all")
        
        width = self.gradient_canvas.winfo_width()
        height = self.gradient_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Create gradient
        self.create_gradient(self.gradient_canvas, "#26659f", "#00c5ad", width, height)
        
        # Draw camera selection
        self.draw_camera_selection(width, height)
        
    def create_gradient(self, canvas, start_color, end_color, width, height):
        """สร้าง gradient บน Canvas"""
        steps = 50
        r1, g1, b1 = self.hex_to_rgb(start_color)
        r2, g2, b2 = self.hex_to_rgb(end_color)
        
        for i in range(steps):
            r = int(r1 + (r2 - r1) * i / steps)
            g = int(g1 + (g2 - g1) * i / steps)
            b = int(b1 + (b2 - b1) * i / steps)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y1 = i * height / steps
            y2 = (i + 1) * height / steps
            canvas.create_rectangle(0, y1, width, y2, fill=color, outline=color)
    
    def hex_to_rgb(self, hex_color):
        """แปลงสี HEX เป็น RGB"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    def draw_camera_selection(self, canvas_width, canvas_height):
        """วาด camera selection"""
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Title
        self.gradient_canvas.create_text(
            center_x, 80,
            text="เลือกกล้องที่ต้องการใช้งาน", 
            font=("Arial", 20, "bold"), 
            fill="white", anchor="center"
        )
        
        # Scan network button
        if not self.scanning:
            scan_btn = tk.Button(
                self.gradient_canvas,
                text="🔍 สแกนหากล้องในเครือข่าย",
                command=self.start_network_scan,
                font=("Arial", 12, "bold"),
                bg="#4CAF50",
                fg="white",
                relief="flat",
                bd=0,
                padx=20,
                pady=8,
                cursor="hand2"
            )
            self.gradient_canvas.create_window(center_x, 120, window=scan_btn)
        else:
            # Show scanning status
            self.gradient_canvas.create_text(
                center_x, 120,
                text="🔍 กำลังสแกนเครือข่าย...", 
                font=("Arial", 12, "bold"), 
                fill="#4CAF50", anchor="center"
            )
        
        start_y = 170
        current_y = start_y
        
        # Show cameras from API
        import __main__
        if hasattr(__main__, 'current_data_camera') and __main__.current_data_camera and len(__main__.current_data_camera) > 0:
            # API Cameras section
            self.gradient_canvas.create_text(
                center_x, current_y,
                text="📋 กล้องจากระบบ", 
                font=("Arial", 14, "bold"), 
                fill="#FFD700", anchor="center"
            )
            current_y += 40
            
            for i, camera in enumerate(__main__.current_data_camera):
                camera_name = camera.get("title", "Unnamed Camera")
                camera_url = camera.get("ip", "")
                
                if camera_url:
                    button = tk.Button(
                        self.gradient_canvas,
                        text=f"📷 {camera_name}",
                        command=lambda url=camera_url, name=camera_name: self.on_select(url, name),
                        font=("Arial", 12, "bold"),
                        bg="white",
                        fg="#333333",
                        relief="flat",
                        bd=0,
                        width=45,
                        height=2,
                        cursor="hand2"
                    )
                    
                    self.gradient_canvas.create_window(center_x, current_y, window=button)
                    current_y += 60
        
        # Show scanned cameras
        if self.scanned_cameras:
            current_y += 20
            self.gradient_canvas.create_text(
                center_x, current_y,
                text=f"🔍 กล้องที่พบในเครือข่าย ({len(self.scanned_cameras)} ตัว)", 
                font=("Arial", 14, "bold"), 
                fill="#00FF7F", anchor="center"
            )
            current_y += 40
            
            for camera in self.scanned_cameras:
                camera_ip = camera['ip']
                camera_type = camera['type']
                camera_port = camera['port']
                
                # Always use RTSP format regardless of detected port
                rtsp_url = f"rtsp://admin:admin@{camera_ip}:554/Streaming/Channels/101"
                
                # Generate button text with RTSP URL info
                if camera_type == 'RTSP Camera':
                    button_text = f"📹 RTSP Camera - {camera_ip}\nrtsp://admin:admin@{camera_ip}:554/..."
                elif camera_type == 'Generic Camera':
                    button_text = f"🌐 Camera - {camera_ip} (Port {camera_port})\nrtsp://admin:admin@{camera_ip}:554/..."
                else:
                    button_text = f"📷 {camera_type} - {camera_ip}\nrtsp://admin:admin@{camera_ip}:554/..."
                
                button = tk.Button(
                    self.gradient_canvas,
                    text=button_text,
                    command=lambda url=rtsp_url, name=f"{camera_type}_{camera_ip}": self.on_select(url, name),
                    font=("Arial", 10),
                    bg="#E8F5E8",
                    fg="#2E7D32",
                    relief="flat",
                    bd=1,
                    width=55,
                    height=3,  # Increased height for 2 lines
                    cursor="hand2",
                    wraplength=450,  # Allow text wrapping
                    justify="center"
                )
                
                # Add hover effect
                def on_enter(e, btn=button):
                    btn.config(bg="#C8E6C8")
                def on_leave(e, btn=button):
                    btn.config(bg="#E8F5E8")
                
                button.bind("<Enter>", on_enter)
                button.bind("<Leave>", on_leave)
                
                self.gradient_canvas.create_window(center_x, current_y, window=button)
                current_y += 65  # Increased spacing for taller buttons
        
        # Show message if no cameras found
        if not self.scanned_cameras and not (
            hasattr(__main__, 'current_data_camera') and __main__.current_data_camera and len(__main__.current_data_camera) > 0
        ):
            if not self.scanning:
                self.gradient_canvas.create_text(
                    center_x, center_y + 50,
                    text="ไม่พบกล้องที่เชื่อมต่อ\nกดปุ่มสแกนเพื่อค้นหากล้องในเครือข่าย", 
                    font=("Arial", 14), 
                    fill="white", anchor="center", justify="center"
                )

    def start_network_scan(self):
        """เริ่มสแกนเครือข่าย"""
        if self.scanning:
            return
            
        self.scanning = True
        self.scanned_cameras = []
        self.update_display()  # Refresh UI to show scanning status
        
        def scan_worker():
            try:
                # Get local network
                network_range, local_ip = self.network_scanner.get_local_network()
                print(f"Scanning network: {network_range}")
                
                # Quick scan common IPs first
                def progress_callback(message, progress):
                    # Update UI on main thread
                    self.after(0, lambda: self.update_scan_progress(message, progress))
                
                cameras = self.network_scanner.quick_scan_common_ips(local_ip, progress_callback)
                
                # Update UI with found cameras
                self.scanned_cameras = cameras
                self.scanning = False
                
                # Update display on main thread
                self.after(0, self.update_display)
                
                print(f"Found {len(cameras)} cameras in network")
                for camera in cameras:
                    print(f"  - {camera['type']} at {camera['ip']}:{camera['port']}")
                
            except Exception as e:
                print(f"Network scan error: {e}")
                import traceback
                traceback.print_exc()
                self.scanning = False
                self.after(0, self.update_display)
        
        # Start scanning in background thread
        threading.Thread(target=scan_worker, daemon=True).start()
    
    def update_scan_progress(self, message, progress):
        """อัปเดตสถานะการสแกน"""
        # Could implement a progress bar here if needed
        pass
    
    def find_working_rtsp_url(self, camera):
        """หา RTSP URL ที่ใช้งานได้สำหรับกล้อง - ใช้รูปแบบ RTSP เสมอ"""
        camera_ip = camera['ip']
        
        # Always return standard RTSP format
        return f"rtsp://admin:admin@{camera_ip}:554/Streaming/Channels/101"
