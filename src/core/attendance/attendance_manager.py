"""
Attendance Manager Module
จัดการการบันทึกและการประมวลผลข้อมูลการเข้าเรียน
"""

import datetime
import threading
import queue
import time
import cv2
from PIL import Image


class AttendanceManager:
    def __init__(self, attendance_queue, api_client, users_org_id, camera_name):
        self.attendance_queue = attendance_queue
        self.api_client = api_client
        self.users_org_id = users_org_id
        self.camera_name = camera_name
        
        # Attendance tracking
        self.attendance_data = []
        self.last_record_time = {}
        self.attendance_lock = threading.Lock()
        
        # Settings
        self.cooldown_time = 300  # 5 minutes between records for same person
        self.similarity_threshold = 70

    def should_record_attendance(self, member_id, similarity):
        """Check if attendance should be recorded"""
        if not member_id or similarity <= self.similarity_threshold:
            return False
            
        now = time.time()
        last_time = self.last_record_time.get(member_id, 0)
        return now - last_time > self.cooldown_time

    def record_attendance(self, member_id, name, frame, bbox, face_manager):
        """Record attendance for a person"""
        if not self.should_record_attendance(member_id, 100):  # Assume high similarity if called
            return False
            
        with self.attendance_lock:
            try:
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                x, y, w, h = bbox

                # Crop face from frame
                face_crop = frame[y:h, x:w]
                if face_crop is None or face_crop.size == 0:
                    return False

                face_pil = Image.fromarray(cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB))

                # Find original image
                known_face = face_manager.get_known_face_by_member_id(member_id)
                original_image = known_face["avatar_image"] if known_face else None

                if original_image:
                    attendance_data = {
                        "name": name,
                        "time": current_time,
                        "capture_image": face_pil,
                        "original_image": original_image,
                        "member_id": member_id
                    }
                    
                    # Add to queue for UI updates
                    if not self.attendance_queue.full():
                        self.attendance_queue.put_nowait(attendance_data)
                    
                    # Update last record time
                    self.last_record_time[member_id] = time.time()
                    
                    # Send to API
                    self.api_client.send_attendance(member_id, self.users_org_id, self.camera_name)
                    
                    print(f"Attendance recorded for {name} ({member_id}) at {current_time}")
                    return True

            except Exception as e:
                print(f"Error recording attendance: {e}")
                return False
                
        return False

    def process_attendance_updates(self, attendance_list_widget):
        """Process attendance updates for UI"""
        try:
            updates_processed = 0
            while not self.attendance_queue.empty() and updates_processed < 5:
                try:
                    attendance_data = self.attendance_queue.get_nowait()
                    
                    self.attendance_data.append(attendance_data)
                    self.attendance_data.sort(key=lambda x: x["time"], reverse=True)
                    
                    # Keep only recent 5 records
                    if len(self.attendance_data) > 5:
                        self.attendance_data = self.attendance_data[:5]
                    
                    # Update UI widget if provided
                    if attendance_list_widget:
                        attendance_list_widget.add_entry(self.attendance_data)
                    
                    updates_processed += 1
                    
                except queue.Empty:
                    break
                
        except Exception as e:
            print(f"Error processing attendance updates: {e}")

    def get_recent_attendance(self, limit=10):
        """Get recent attendance records"""
        with self.attendance_lock:
            return self.attendance_data[:limit]

    def clear_old_records(self, max_age_hours=24):
        """Clear old attendance records"""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        with self.attendance_lock:
            # Clear from last_record_time
            old_members = []
            for member_id, record_time in self.last_record_time.items():
                if record_time < cutoff_time:
                    old_members.append(member_id)
            
            for member_id in old_members:
                del self.last_record_time[member_id]
            
            print(f"Cleared {len(old_members)} old attendance records")

    def set_cooldown_time(self, seconds):
        """Set cooldown time between records"""
        self.cooldown_time = seconds

    def set_similarity_threshold(self, threshold):
        """Set similarity threshold for attendance recording"""
        self.similarity_threshold = threshold

    def get_statistics(self):
        """Get attendance statistics"""
        with self.attendance_lock:
            total_records = len(self.attendance_data)
            unique_members = len(set(record.get("member_id", "") for record in self.attendance_data))
            
            return {
                "total_records": total_records,
                "unique_members": unique_members,
                "recent_records": self.attendance_data[:5]
            }
