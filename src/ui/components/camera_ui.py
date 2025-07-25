"""
UI Components for Camera Section
จัดการส่วน UI ที่เกี่ยวข้องกับการแสดงผล
"""

import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import requests
import time
from io import BytesIO


class CameraUI:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.logo_imgtk = None
        self.clock_label = None
        self.camera_display = None
        
    def create_ui_components(self):
        """Create UI components"""
        # Top white frame
        self.top_space = ctk.CTkFrame(self.parent_frame, height=80, fg_color="white", corner_radius=10)
        self.top_space.pack(fill="x", side="top", padx=10, pady=10)
        
        # Logo
        self.load_logo()
        
        # Digital Clock
        self.create_digital_clock()
        
        # Video frame
        self.video_frame = ctk.CTkFrame(self.parent_frame, fg_color="#CFDEE3", corner_radius=10, width=1280, height=720)
        self.video_frame.pack(fill="x", side="bottom", padx=10, pady=(0, 20))
        self.video_frame.pack_propagate(False)

        # Camera display
        self.camera_display = tk.Label(self.video_frame, bg="#CFDEE3", 
                                     text="กำลังเชื่อมต่อกล้อง...", 
                                     font=("Arial", 16), fg="#666666")
        self.camera_display.pack(fill="both", expand=True)

    def load_logo(self):
        """Load logo"""
        logo_url = "https://image.makewebeasy.net/makeweb/m_1200x600/XdFh0iol7/DefaultData/App_BD___BW.png"
        try:
            response = requests.get(logo_url, timeout=10)
            response.raise_for_status()
            logo_img = Image.open(BytesIO(response.content))
            desired_height = 120
            w, h = logo_img.size
            new_width = int(w * desired_height / h)
            logo_img = logo_img.resize((new_width, desired_height), Image.LANCZOS)
            self.logo_imgtk = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(self.top_space, image=self.logo_imgtk, bg="white", bd=0)
            logo_label.pack(side="left", padx=20, pady=10)
        except Exception as e:
            print("Failed to load logo:", e)

    def create_digital_clock(self):
        """Create digital clock"""
        clock_frame = ctk.CTkFrame(self.top_space, fg_color="white")
        clock_frame.pack(side="right", padx=40, pady=10)

        self.clock_label = ctk.CTkLabel(
            clock_frame,
            text="00:00:00",
            font=("Arial", 36, "bold"),
            fg_color="#00C5AD",
            corner_radius=10,
            text_color="white",
            padx=5,
            pady=5
        )
        self.clock_label.pack()

        def update_clock():
            try:
                now = time.strftime("%H:%M:%S")
                self.clock_label.configure(text=now)
                self.clock_label.after(1000, update_clock)
            except:
                pass

        update_clock()

    def update_camera_display(self, frame=None, status_text=None):
        """Update camera display with frame or status text"""
        if frame is not None:
            try:
                # Get canvas dimensions
                canvas_width = self.video_frame.winfo_width()
                canvas_height = self.video_frame.winfo_height()
                
                if canvas_width <= 1 or canvas_height <= 1:
                    return False

                # Resize frame to fit canvas
                import cv2
                frame_resized = cv2.resize(frame, (canvas_width, canvas_height))
                
                # Convert and display frame
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img = self.apply_rounded_corners(img, radius=10)
                imgtk = ImageTk.PhotoImage(image=img)
                
                self.camera_display.imgtk = imgtk
                self.camera_display.configure(image=imgtk, text="")
                return True
                
            except Exception as e:
                print(f"Display error: {e}")
                return False
        
        elif status_text:
            self.camera_display.configure(text=status_text, fg="#666666")
            return True
            
        return False

    def draw_face_boxes(self, frame, face_results):
        """Draw face detection boxes on frame"""
        if not face_results:
            return frame
            
        import cv2
        import time
        
        current_time = time.time()
        canvas_width = self.video_frame.winfo_width()
        canvas_height = self.video_frame.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return frame
            
        frame_resized = cv2.resize(frame, (canvas_width, canvas_height))
        
        for result in face_results:
            # Only show recent results
            if current_time - result.get("timestamp", 0) < 3:
                try:
                    x, y, w, h = result["bbox"]
                    name = result.get("name", "Unknown")
                    member_id = result.get("member_id", "")
                    similarity = result.get("similarity", 0)

                    # Scale bbox to canvas size
                    if frame.shape[1] > 0 and frame.shape[0] > 0:
                        scale_x = canvas_width / frame.shape[1]
                        scale_y = canvas_height / frame.shape[0]
                        
                        x_scaled = int(x * scale_x)
                        y_scaled = int(y * scale_y)
                        w_scaled = int(w * scale_x)
                        h_scaled = int(h * scale_y)

                        # Draw rectangle and text with better styling
                        color = (0, 255, 0) if similarity > 70 else (255, 255, 0)
                        
                        # Draw thicker border for better visibility
                        cv2.rectangle(frame_resized, (x_scaled, y_scaled), (w_scaled, h_scaled), color, 3)
                        
                        # Add a subtle background for text
                        if member_id and similarity > 70:
                            text = f"{member_id} ({similarity:.1f}%)"
                            
                            # Calculate text size
                            font_scale = 0.7
                            thickness = 2
                            (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
                            
                            # Draw background rectangle for text
                            text_bg_start = (x_scaled, y_scaled - text_height - 15)
                            text_bg_end = (x_scaled + text_width, y_scaled - 5)
                            cv2.rectangle(frame_resized, text_bg_start, text_bg_end, color, -1)
                            
                            # Draw text
                            cv2.putText(frame_resized, text, (x_scaled, y_scaled - 10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
                except Exception as draw_error:
                    print(f"Draw error: {draw_error}")
                    continue
                    
        return frame_resized

    def get_connection_status_text(self, camera_status):
        """Generate connection status text"""
        time_since_last_frame = time.time() - camera_status.get('last_frame_time', 0)
        
        status_text = f"กำลังเชื่อมต่อกล้อง...\n"
        status_text += f"ไม่มีสัญญาณ: {int(time_since_last_frame)} วินาที\n"
        status_text += f"ความพยายามที่: {camera_status.get('retry_count', 0) + 1}/{camera_status.get('max_retries', 3)}"
        
        if camera_status.get('reconnecting', False):
            status_text += "\nกำลังเชื่อมต่อใหม่..."
            
        return status_text

    @staticmethod
    def apply_rounded_corners(img, radius=30):
        """Apply rounded corners to image"""
        try:
            w, h = img.size
            mask = Image.new('L', (w, h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([(0, 0), (w, h)], radius=radius, fill=255)
            img.putalpha(mask)
            return img
        except:
            return img
