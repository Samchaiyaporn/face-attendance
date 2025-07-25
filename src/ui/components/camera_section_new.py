"""
Camera Section - Refactored
จัดการหน้าจอกล้องหลักที่แยกส่วนต่างๆ ออกเป็น modules แล้ว
"""

import customtkinter as ctk
import queue
import threading
import time
import sys
import os

# Add utils directory to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

# Import custom modules
from core.camera.camera_handler import CameraHandler
from core.face_recognition.face_manager import FaceRecognitionManager
from core.api.api_client import APIClient
from core.attendance.attendance_manager import AttendanceManager
from ui.components.camera_ui import CameraUI
from ui.components.progress_dialog import LoadingManager

# Try to import API utilities
try:
    import sys
    import os
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config'))
    if config_path not in sys.path:
        sys.path.insert(0, config_path)
    from global_config import get_api_base_url
    
    # Test if config loads properly
    test_url = get_api_base_url()
    print(f"Camera Section - API Base URL loaded: {test_url}")
    
except ImportError as e:
    print(f"Camera Section - Could not import global_config: {e}")
    # Ultimate fallback only if everything fails
    def get_api_base_url():
        return "https://smart-school-uat.belib.app/api"


class CameraSection(ctk.CTkFrame):
    def __init__(self, parent, attendance_list=None, rtsp_url=None, camera_name=None, 
                 access_token=None, users_org_id=None, api_url=None):
        super().__init__(parent, fg_color="#CFDEE3", corner_radius=10)

        # Initialize basic variables
        self.running = True
        self.attendance_list = attendance_list
        self.rtsp_url = rtsp_url or "rtsp://admin:admin@192.168.1.100:554/Streaming/Channels/101"
        self.camera_name = camera_name or "Unnamed Camera"
        
        # Use centralized API URL or fallback
        self.api_url = api_url or get_api_base_url()
        
        # Initialize queues
        self.frame_queue = queue.Queue(maxsize=2)
        self.face_processing_queue = queue.Queue(maxsize=1)
        self.face_results_queue = queue.Queue(maxsize=3)
        self.attendance_queue = queue.Queue(maxsize=10)
        
        # Frame processing variables
        self.frame_count = 0
        self.last_face_results = []
        
        # Initialize modules
        self.api_client = APIClient(access_token, self.api_url)
        self.camera_handler = CameraHandler(self.rtsp_url, self.frame_queue)
        self.face_manager = FaceRecognitionManager(self.face_processing_queue, self.face_results_queue)
        self.attendance_manager = AttendanceManager(
            self.attendance_queue, 
            self.api_client, 
            users_org_id, 
            self.camera_name
        )
        self.camera_ui = CameraUI(self)
        
        # Loading manager for progress display
        self.loading_manager = LoadingManager(self)
        
        # Initialize system
        self.initialize_system()

    def initialize_system(self):
        """Initialize the entire system"""
        try:
            # Create UI components
            self.camera_ui.create_ui_components()
            
            # Initialize face recognition model
            if self.face_manager.initialize_model():
                # Load known faces from API with progress
                self.load_students_with_progress()
            
            # Initialize camera
            if self.camera_handler.initialize():
                print("Camera initialized successfully")
                
                # Start all processing threads
                self.start_processing_threads()
                
                # Start UI update loop
                self.update_frame()
            else:
                print("Failed to initialize camera")
                self.running = False
                
        except Exception as e:
            print(f"Failed to initialize system: {e}")
            import traceback
            traceback.print_exc()
            self.running = False
    
    def load_students_with_progress(self):
        """Load students data with progress dialog"""
        def load_data(progress_callback):
            """Function to load data with progress updates"""
            try:
                # Fetch students from API
                students = self.api_client.fetch_students(progress_callback)
                
                # Load known faces
                known_faces = self.face_manager.load_known_faces(students, progress_callback)
                
                return {
                    'students': students,
                    'known_faces': known_faces
                }
            except Exception as e:
                print(f"Error loading students: {e}")
                return {'students': [], 'known_faces': []}
        
        def on_load_complete(result):
            """Callback when loading is complete"""
            students = result.get('students', [])
            known_faces = result.get('known_faces', [])
            print(f"Loaded {len(students)} students and {len(known_faces)} known faces")
            
            # Update header with user count
            if hasattr(self, 'header') and self.header:
                self.header.update_user_count(len(students))
            
            # Start face processing after loading is complete
            if self.face_manager.is_model_available() and len(known_faces) > 0:
                self.face_manager.start_processing()

        # Start loading with progress dialog
        self.loading_manager.start_loading(
            load_data,
            on_load_complete,
            title="กำลังโหลดข้อมูลนักเรียน",
            message="กำลังเชื่อมต่อและดาวน์โหลดข้อมูล..."
        )
    
    def refresh_user_data(self):
        """รีเฟรชข้อมูลผู้ใช้"""
        print("Refreshing user data...")
        
        # Update header to show loading state
        if hasattr(self, 'header') and self.header:
            # Reset user count display
            self.header.gradient_canvas.itemconfig(
                self.header.user_count_text_id, 
                text="กำลังรีเฟรชข้อมูล..."
            )
            
        # Stop current face processing
        if self.face_manager.is_model_available():
            self.face_manager.stop_processing()
        
        # Reload data with progress
        self.load_students_with_progress()

    def start_processing_threads(self):
        """Start all processing threads"""
        if not self.running:
            return
            
        # Start camera capture
        self.camera_handler.start_capture()
        
        # Start face processing if model is available (only if not already running)
        if self.face_manager.is_model_available() and not self.face_manager.running:
            self.face_manager.start_processing()

    def update_frame(self):
        """Update frame display with reduced delay"""
        if not self.running:
            print("Update frame stopped - not running")
            return
            
        try:
            # Process attendance updates
            self.attendance_manager.process_attendance_updates(self.attendance_list)
            
            # Get face results
            try:
                self.last_face_results = self.face_results_queue.get_nowait()
            except queue.Empty:
                pass

            # Get frame - always get the latest frame to reduce delay
            frame = self._get_latest_frame()

            if frame is None:
                # Show connection status if no frames
                camera_status = self.camera_handler.get_connection_status()
                status_text = self.camera_ui.get_connection_status_text(camera_status)
                self.camera_ui.update_camera_display(status_text=status_text)
                
                self.after(50, self.update_frame)  # Reduce frequency when no frames
                return

            # Validate frame
            if frame.size == 0:
                self.after(20, self.update_frame)
                return

            # Process frame for face detection
            self._process_frame_for_faces(frame)
            
            # Draw face boxes and update display
            frame_with_boxes = self.camera_ui.draw_face_boxes(frame, self.last_face_results)
            self.camera_ui.update_camera_display(frame=frame_with_boxes)
            
            # Check for attendance recording
            self._check_for_attendance_recording(frame)

        except Exception as e:
            print(f"Error in update_frame: {e}")
            import traceback
            traceback.print_exc()

        # Schedule next update
        if self.running:
            self.after(20, self.update_frame)  # ~50 FPS max

    def _get_latest_frame(self):
        """Get the most recent frame from queue"""
        frame = None
        frame_count = 0
        
        # Get the most recent frame and discard older ones
        while not self.frame_queue.empty() and frame_count < 5:
            try:
                frame = self.frame_queue.get_nowait()
                frame_count += 1
            except queue.Empty:
                break
                
        return frame

    def _process_frame_for_faces(self, frame):
        """Process frame for face detection"""
        if self.face_manager.is_model_available():
            self.frame_count += 1
            if self.face_manager.should_process_frame(self.frame_count):
                self.face_manager.add_frame_for_processing(frame)

    def _check_for_attendance_recording(self, frame):
        """Check if any face should have attendance recorded"""
        if not self.last_face_results:
            return
            
        current_time = time.time()
        for result in self.last_face_results:
            # Only process recent results
            if current_time - result.get("timestamp", 0) > 3:
                continue
                
            member_id = result.get("member_id")
            similarity = result.get("similarity", 0)
            
            if self.attendance_manager.should_record_attendance(member_id, similarity):
                name = result.get("name", "Unknown")
                bbox = result.get("bbox")
                
                self.attendance_manager.record_attendance(
                    member_id, name, frame, bbox, self.face_manager
                )

    def stop(self):
        """Stop the camera section with better cleanup"""
        print("Stopping camera section...")
        self.running = False
        
        # Stop all modules
        self.camera_handler.stop_capture()
        self.face_manager.stop_processing()
        
        # Clear queues
        queues = [self.frame_queue, self.face_processing_queue, 
                 self.face_results_queue, self.attendance_queue]
        
        for queue_obj in queues:
            try:
                while not queue_obj.empty():
                    queue_obj.get_nowait()
            except:
                pass
        
        print("Camera section stopped")
