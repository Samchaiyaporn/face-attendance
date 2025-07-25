import tkinter as tk
import sys
import os
from .components.header import Header
from .components.attendance_list import AttendanceList
from .components.camera_section_new import CameraSection
from .styles import COLORS

# Add utils directory to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils'))
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

# Try to import API utilities
try:
    import sys
    import os
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
    if config_path not in sys.path:
        sys.path.insert(0, config_path)
    from global_config import get_api_base_url
    
    # Test if config loads properly
    test_url = get_api_base_url()
    print(f"Main Window - API Base URL loaded: {test_url}")
    
except ImportError as e:
    print(f"Main Window - Could not import global_config: {e}")
    # Ultimate fallback only if everything fails
    def get_api_base_url():
        return "https://smart-school-uat.belib.app/api"

class MainWindow(tk.Frame):
    def __init__(self, parent, title, rtsp_url, camera_name, current_access_token, current_users_org_id, api_url=None):
        super().__init__(parent)
        self.rtsp_url = rtsp_url
        self.camera_name = camera_name
        self.current_access_token = current_access_token
        self.api_url = api_url or get_api_base_url()  # Use centralized config
        self.current_users_org_id = current_users_org_id
        self.attendance_list = None  # หรือสร้าง attendance_list ตามระบบคุณ

        self.setup_ui(title)  # <-- สร้าง UI ที่เดียว

    def setup_ui(self, title):
        self.winfo_toplevel().title(title)
        self.winfo_toplevel().state("zoomed")
        self.winfo_toplevel().configure(bg=COLORS["background"])

        # Camera Section (create first to pass to header)
        main_frame = tk.Frame(self.winfo_toplevel(), bg=COLORS["background"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Left Side - Camera
        camera_frame = tk.Frame(main_frame, bg=COLORS["background"])
        camera_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Create camera section
        self.camera_section = CameraSection(
            camera_frame, 
            self.attendance_list, 
            self.rtsp_url, 
            self.camera_name, 
            self.current_access_token, 
            self.current_users_org_id,
            self.api_url
        )
        self.camera_section.pack(fill="both", expand=True)

        # Header (create after camera section)
        header = Header(self.winfo_toplevel(), camera_section=self.camera_section)
        header.pack(fill="x", pady=(0, 10), before=main_frame)
        
        # Store header reference in camera section for updates
        self.camera_section.header = header

        # Right: Attendance List
        self.attendance_list = AttendanceList(main_frame)
        self.attendance_list.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Update camera section with attendance list
        self.camera_section.attendance_list = self.attendance_list

    def close_camera(self):
        """ปิดการเชื่อมต่อกล้องใน CameraSection"""
        if hasattr(self, 'camera_section'):
            self.camera_section.stop()
