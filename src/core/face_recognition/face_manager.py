"""
Face Recognition Manager
จัดการการตรวจจับและจดจำใบหน้าด้วย InsightFace
"""

import os
import sys
import time
import threading
import queue
import numpy as np
import cv2
from PIL import Image

# ตรวจสอบ InsightFace และ setup model path
try:
    import insightface
    INSIGHTFACE_AVAILABLE = True
    print("InsightFace imported successfully")
    
    # Setup model path for PyInstaller
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        application_path = sys._MEIPASS
        model_path = os.path.join(application_path, 'insightface_models')
        if not os.path.exists(model_path):
            os.makedirs(model_path, exist_ok=True)
        os.environ['INSIGHTFACE_HOME'] = model_path
        print(f"InsightFace model path set to: {model_path}")
    else:
        # Running in development
        print("Running in development mode")
        
except ImportError as e:
    print(f"InsightFace import error: {e}")
    INSIGHTFACE_AVAILABLE = False


class FaceRecognitionManager:
    def __init__(self, face_processing_queue, face_results_queue):
        self.face_processing_queue = face_processing_queue
        self.face_results_queue = face_results_queue
        
        # Face recognition variables
        self.face_model = None
        self.known_faces = []
        self.running = False
        self.frame_count = 0
        
        # Threading
        self.processing_thread = None

    def initialize_model(self):
        """Initialize InsightFace model with proper error handling"""
        if not INSIGHTFACE_AVAILABLE:
            print("InsightFace not available - face recognition disabled")
            return False
            
        try:
            print("Loading InsightFace model...")
            
            # Check if running in PyInstaller
            if getattr(sys, 'frozen', False):
                print("Running in PyInstaller mode - downloading models if needed")
                
            # Try loading multiple model formats
            model_loaded = False
            
            # Try loading buffalo_l first
            for model_name in ['buffalo_l', 'buffalo_m', 'buffalo_s']:
                try:
                    print(f"Trying to load {model_name}...")
                    self.face_model = insightface.app.FaceAnalysis(
                        name=model_name,
                        providers=['CPUExecutionProvider']
                    )
                    
                    print(f"Preparing {model_name} model...")
                    # Use larger detection size for better face detection
                    self.face_model.prepare(ctx_id=0, det_size=(640, 640), det_thresh=0.5)
                    
                    # Test model
                    test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
                    test_result = self.face_model.get(test_img)
                    
                    print(f"✅ {model_name} model loaded and tested successfully")
                    model_loaded = True
                    break
                    
                except Exception as model_error:
                    print(f"❌ Failed to load {model_name}: {model_error}")
                    continue
            
            if not model_loaded:
                print("❌ All model loading attempts failed")
                self.face_model = None
                return False
                
            return True
                
        except Exception as e:
            print(f"Failed to load InsightFace model: {e}")
            import traceback
            traceback.print_exc()
            self.face_model = None
            return False

    def load_known_faces(self, students_data, progress_callback=None):
        """Load known faces from student data with progress callback"""
        if self.face_model is None:
            print("Face model is None, skipping face loading")
            return []
            
        known_faces = []
        try:
            total_students = len(students_data)
            print(f"Processing {total_students} students for face recognition")
            
            if progress_callback:
                progress_callback("เริ่มประมวลผลใบหน้า...", 80)
            
            for i, student in enumerate(students_data):
                name = student["display_name"]
                member_id = student["member_id"]
                avatar_image = student["avatar_image"]
                
                # Update progress for face processing
                if progress_callback and total_students > 0:
                    progress = 80 + int((i / total_students) * 18)  # 80% to 98%
                    progress_callback(f"ประมวลผลใบหน้า: {name}", progress)
                
                if avatar_image is None:
                    print(f"Avatar image for {name} is None. Skipping...")
                    continue
                    
                try:
                    # Validate PIL Image
                    if not hasattr(avatar_image, 'convert'):
                        print(f"Invalid image type for {name}. Skipping...")
                        continue
                    
                    # Check image size
                    width, height = avatar_image.size
                    if width < 50 or height < 50:
                        print(f"Image too small for {name}: {width}x{height}. Skipping...")
                        continue
                    
                    # Resize large images
                    if width > 800 or height > 800:
                        print(f"Resizing large image for {name}: {width}x{height}")
                        max_size = 800
                        if width > height:
                            new_width = max_size
                            new_height = int(height * max_size / width)
                        else:
                            new_height = max_size
                            new_width = int(width * max_size / height)
                        avatar_image = avatar_image.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Convert to RGB and numpy array
                    img_rgb = avatar_image.convert("RGB")
                    img_array = np.array(img_rgb, dtype=np.uint8)
                    
                    # Validate array
                    if img_array is None or img_array.size == 0:
                        print(f"Invalid image array for {name}. Skipping...")
                        continue
                        
                    if len(img_array.shape) != 3 or img_array.shape[2] != 3:
                        print(f"Invalid image shape for {name}: {img_array.shape}. Skipping...")
                        continue
                    
                    # Ensure contiguous array
                    if not img_array.flags['C_CONTIGUOUS']:
                        img_array = np.ascontiguousarray(img_array)
                    
                    print(f"Processing face detection for {name} - image shape: {img_array.shape}")
                    
                    # Use InsightFace to detect faces with retry mechanism
                    faces = None
                    for attempt in range(3):
                        try:
                            faces = self.face_model.get(img_array)
                            break
                        except Exception as face_error:
                            print(f"Face detection attempt {attempt + 1} failed for {name}: {face_error}")
                            if attempt == 2:  # Last attempt
                                # Try with smaller image
                                try:
                                    small_img = cv2.resize(img_array, (300, 300))
                                    small_img = np.ascontiguousarray(small_img)
                                    faces = self.face_model.get(small_img)
                                    print(f"Small image detection succeeded for {name}")
                                except Exception as small_error:
                                    print(f"Small image detection also failed for {name}: {small_error}")
                                    break
                            else:
                                time.sleep(0.1)  # Short delay before retry
                    
                    if faces is None:
                        print(f"No faces detected for {name}")
                        continue
                        
                    if len(faces) == 0:
                        print(f"No faces found in image for {name}")
                        continue
                        
                    if len(faces) > 1:
                        print(f"Multiple faces detected for {name}, using first face")
                    
                    # Use first detected face
                    face = faces[0]
                    
                    # Check embedding
                    if not hasattr(face, 'embedding') or face.embedding is None:
                        print(f"No embedding found for {name}")
                        continue
                        
                    embedding = face.embedding
                    
                    if embedding.size == 0:
                        print(f"Empty embedding for {name}")
                        continue
                        
                    known_faces.append({
                        "name": name,
                        "member_id": member_id,
                        "embedding": embedding,
                        "avatar_image": avatar_image
                    })
                    print(f"✅ Successfully added face for {name}")
                    
                except Exception as e:
                    print(f"❌ Error processing image for {name}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
                    
        except Exception as e:
            print(f"❌ Error loading known faces: {e}")
            import traceback
            traceback.print_exc()
            
        print(f"Successfully loaded {len(known_faces)} known faces")
        self.known_faces = known_faces
        
        if progress_callback:
            progress_callback("เสร็จสิ้นการโหลดข้อมูล!", 100)
            
        return known_faces

    def start_processing(self):
        """Start face processing thread"""
        if self.face_model is None:
            print("Face model not available, skipping face processing")
            return
            
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_faces, daemon=True)
        self.processing_thread.start()

    def stop_processing(self):
        """Stop face processing"""
        print("Stopping face processing...")
        self.running = False
        
        if self.processing_thread and self.processing_thread.is_alive():
            try:
                print("Waiting for face processing thread to stop...")
                self.processing_thread.join(timeout=3)
                if self.processing_thread.is_alive():
                    print("Warning: face processing thread did not stop gracefully")
            except Exception as e:
                print(f"Error stopping face processing thread: {e}")

    def should_process_frame(self, frame_count):
        """Determine if frame should be processed for face detection"""
        # Process every 10th frame for faster face detection (was 30)
        return frame_count % 10 == 0 and self.face_processing_queue.empty()

    def add_frame_for_processing(self, frame):
        """Add frame to processing queue"""
        if self.face_model is None:
            return False
            
        try:
            # Create a copy for face processing
            face_frame = frame.copy()
            self.face_processing_queue.put_nowait(face_frame)
            return True
        except queue.Full:
            return False
        except Exception as e:
            print(f"Face queue error: {e}")
            return False

    def _process_faces(self):
        """Process faces with enhanced error handling"""
        if self.face_model is None:
            print("Face model not available")
            return
            
        print("Starting face processing thread...")
        
        while self.running:
            try:
                frame = self.face_processing_queue.get(timeout=1)
                
                # Validate frame
                if frame is None:
                    continue
                    
                if not isinstance(frame, np.ndarray) or frame.size == 0:
                    continue
                    
                if len(frame.shape) != 3:
                    continue

                try:
                    # Process frame
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    if frame_rgb is None or frame_rgb.size == 0:
                        continue
                    
                    # Ensure contiguous array
                    if not frame_rgb.flags['C_CONTIGUOUS']:
                        frame_rgb = np.ascontiguousarray(frame_rgb)
                    
                    # Face detection with retry
                    faces = self._detect_faces_with_retry(frame_rgb, frame)
                    
                    if faces is None:
                        continue
                    
                    # Process detected faces
                    face_results = self._process_detected_faces(faces, frame)

                    # Send results to UI
                    self._send_results_to_ui(face_results)

                except Exception as e:
                    print(f"Error in frame processing: {e}")
                    continue

                # Clear old frames
                self._clear_processing_queue()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in face processing: {e}")

    def _detect_faces_with_retry(self, frame_rgb, original_frame):
        """Detect faces with retry mechanism"""
        faces = None
        for attempt in range(2):
            try:
                faces = self.face_model.get(frame_rgb)
                break
            except Exception as face_error:
                if attempt == 0:
                    # Try resizing frame
                    try:
                        smaller_frame = cv2.resize(frame_rgb, (640, 480))
                        smaller_frame = np.ascontiguousarray(smaller_frame)
                        faces = self.face_model.get(smaller_frame)
                        # Scale bbox back
                        if faces:
                            scale_x = original_frame.shape[1] / 640
                            scale_y = original_frame.shape[0] / 480
                            for face in faces:
                                if hasattr(face, 'bbox') and face.bbox is not None:
                                    face.bbox = face.bbox * np.array([scale_x, scale_y, scale_x, scale_y])
                        break
                    except:
                        continue
                else:
                    print(f"Face detection failed after retries: {face_error}")
                    break
        return faces

    def _process_detected_faces(self, faces, frame):
        """Process detected faces and extract information"""
        face_results = []
        for i, face in enumerate(faces):
            try:
                if not hasattr(face, 'bbox') or not hasattr(face, 'embedding'):
                    continue
                    
                bbox = face.bbox
                if bbox is None or len(bbox) < 4:
                    continue
                    
                x, y, w, h = [int(v) for v in bbox]
                h_img, w_img = frame.shape[:2]
                
                # Expand bounding box to show full face (25% padding)
                face_width = w - x
                face_height = h - y
                
                # Add padding around the face
                padding_x = int(face_width * 0.25)  # 25% padding horizontally
                padding_y = int(face_height * 0.3)   # 30% padding vertically (more for forehead/chin)
                
                # Expand the bounding box
                x = max(0, x - padding_x)
                y = max(0, y - padding_y)
                w = min(w_img, w + padding_x)
                h = min(h_img, h + padding_y)
                
                # Ensure valid bounds
                x = max(0, min(x, w_img))
                y = max(0, min(y, h_img))
                w = max(x + 1, min(w, w_img))
                h = max(y + 1, min(h, h_img))
                
                if w <= x or h <= y:
                    continue

                face_embedding = face.embedding
                if face_embedding is None:
                    continue
                    
                name, similarity, member_id = self.compare_faces(face_embedding)

                face_results.append({
                    "bbox": (x, y, w, h),
                    "name": name,
                    "member_id": member_id,
                    "similarity": similarity,
                    "embedding": face_embedding,
                    "timestamp": time.time()
                })
                    
            except Exception as e:
                print(f"Error processing face {i}: {e}")
                
        return face_results

    def _send_results_to_ui(self, face_results):
        """Send face recognition results to UI"""
        if not self.face_results_queue.full():
            self.face_results_queue.put_nowait(face_results)
        else:
            try:
                self.face_results_queue.get_nowait()
                self.face_results_queue.put_nowait(face_results)
            except queue.Empty:
                self.face_results_queue.put_nowait(face_results)

    def _clear_processing_queue(self):
        """Clear old frames from processing queue"""
        while not self.face_processing_queue.empty():
            try:
                self.face_processing_queue.get_nowait()
            except queue.Empty:
                break

    def compare_faces(self, face_embedding):
        """Compare face embedding with known faces"""
        if not self.known_faces:
            return None, 0, None
            
        best_match = None
        member_id = None
        best_similarity = 0
        
        for known_face in self.known_faces:
            try:
                known_embedding = known_face["embedding"]
                similarity = np.dot(face_embedding, known_embedding) / (
                    np.linalg.norm(face_embedding) * np.linalg.norm(known_embedding)
                )
                similarity = (similarity + 1) / 2 * 100
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    member_id = known_face["member_id"] or known_face["name"]
                    best_match = known_face["name"]
            except Exception as e:
                print(f"Error comparing face: {e}")
                continue
        
        if best_similarity > 70:
            return best_match, best_similarity, member_id
        else:
            return None, best_similarity, None

    def get_known_face_by_member_id(self, member_id):
        """Get known face data by member ID"""
        for face in self.known_faces:
            if face["member_id"] == member_id:
                return face
        return None

    def is_model_available(self):
        """Check if face recognition model is available"""
        return self.face_model is not None
