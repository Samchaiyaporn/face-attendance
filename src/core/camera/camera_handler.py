"""
Camera Handler Module
จัดการการเชื่อมต่อและการรับภาพจากกล้อง RTSP
"""

import cv2
import time
import threading
import queue
import numpy as np


class CameraHandler:
    def __init__(self, rtsp_url, frame_queue, max_retry_count=3, frame_timeout=5):
        self.rtsp_url = rtsp_url
        self.frame_queue = frame_queue
        self.max_retry_count = max_retry_count
        self.frame_timeout = frame_timeout
        
        # Camera connection variables
        self.cap = None
        self.connection_retry_count = 0
        self.last_frame_time = time.time()
        self.reconnect_in_progress = False
        self.running = False
        
        # Threading
        self.capture_thread = None
        self.monitor_thread = None

    def initialize(self):
        """Initialize camera connection"""
        try:
            print(f"Connecting to camera: {self.rtsp_url}")
            
            # Validate URL format
            if not self.rtsp_url or not self.rtsp_url.startswith(('rtsp://', 'http://', 'https://')):
                print("Invalid RTSP URL format")
                return False
                
            self.connect_camera()
            if self.cap and self.cap.isOpened():
                print("Camera connection successful")
                # Test initial frame read
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    print("Initial frame read successful")
                    self.last_frame_time = time.time()
                    return True
                else:
                    print("Warning: Could not read initial frame")
                    return False
            else:
                print("Failed to connect to camera")
                return False
                
        except Exception as e:
            print(f"Failed to initialize camera: {e}")
            import traceback
            traceback.print_exc()
            return False

    def connect_camera(self):
        """Connect to camera using OpenCV with enhanced error handling"""
        try:
            # Close existing connection
            self.close_connection()
            
            print("Opening camera with OpenCV...")
            
            # Try multiple backends
            backends = [cv2.CAP_FFMPEG, cv2.CAP_GSTREAMER, cv2.CAP_ANY]
            
            for backend in backends:
                try:
                    print(f"Trying backend: {backend}")
                    # Create VideoCapture object with specific backend
                    self.cap = cv2.VideoCapture(self.rtsp_url, backend)
                    
                    # Set camera properties for better performance
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffer
                    
                    # Set timeout properties if available
                    try:
                        self.cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)  # 5 second timeout
                        self.cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000)   # 3 second read timeout
                    except:
                        pass
                    
                    # Try to read a frame to test connection
                    success = False
                    for attempt in range(5):
                        ret, frame = self.cap.read()
                        if ret and frame is not None and frame.size > 0:
                            print(f"Successfully read test frame with backend {backend}")
                            success = True
                            break
                        time.sleep(0.2)
                    
                    if success:
                        break
                    else:
                        print(f"Backend {backend} failed to read frames")
                        if self.cap:
                            self.cap.release()
                            self.cap = None
                        
                except Exception as backend_error:
                    print(f"Backend {backend} failed: {backend_error}")
                    if self.cap:
                        self.cap.release()
                        self.cap = None
                    continue
            
            if not self.cap or not self.cap.isOpened():
                raise Exception("All backends failed to connect")
            
            # Get camera properties
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            print(f"Connected to camera: {width}x{height} @ {fps} FPS")
            self.connection_retry_count = 0
            
        except Exception as e:
            print(f"Failed to connect camera: {e}")
            import traceback
            traceback.print_exc()
            self.close_connection()
            raise e

    def start_capture(self):
        """Start camera capture threads"""
        self.running = True
        
        # Frame capture thread
        self.capture_thread = threading.Thread(target=self._capture_frames, daemon=True)
        self.capture_thread.start()
        
        # Connection monitor thread
        self.monitor_thread = threading.Thread(target=self._monitor_connection, daemon=True)
        self.monitor_thread.start()

    def stop_capture(self):
        """Stop camera capture"""
        print("Stopping camera capture...")
        self.running = False
        
        # Close camera connection first
        self.close_connection()
        
        # Wait for threads to finish
        threads_to_wait = []
        
        if self.capture_thread and self.capture_thread.is_alive():
            threads_to_wait.append(('capture_thread', self.capture_thread))
            
        if self.monitor_thread and self.monitor_thread.is_alive():
            threads_to_wait.append(('monitor_thread', self.monitor_thread))
        
        # Wait for each thread with timeout
        for thread_name, thread in threads_to_wait:
            try:
                print(f"Waiting for {thread_name} to stop...")
                thread.join(timeout=3)
                if thread.is_alive():
                    print(f"Warning: {thread_name} did not stop gracefully")
            except Exception as e:
                print(f"Error stopping {thread_name}: {e}")
        
        print("Camera capture stopped")

    def _capture_frames(self):
        """Capture frames from camera with corruption handling"""
        if not self.running:
            return
            
        print("Starting frame capture with OpenCV...")
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.running:
            try:
                if not self.cap or not self.cap.isOpened():
                    print("No camera connection, attempting to reconnect...")
                    self._reconnect_camera()
                    if not self.cap or not self.cap.isOpened():
                        time.sleep(2)
                        continue
                
                # Read frame from camera
                ret, frame = self.cap.read()
                
                if not ret or frame is None:
                    consecutive_errors += 1
                    print(f"Failed to read frame (error count: {consecutive_errors})")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        print("Too many consecutive frame errors, reconnecting...")
                        self._reconnect_camera()
                        consecutive_errors = 0
                        time.sleep(1)
                        continue
                    
                    time.sleep(0.1)
                    continue
                
                # Validate frame
                if not self._validate_frame(frame):
                    consecutive_errors += 1
                    continue
                
                # Reset error counter on successful frame
                consecutive_errors = 0
                self.last_frame_time = time.time()
                self.connection_retry_count = 0
                
                # Add to frame queue (drop old frames to reduce delay)
                try:
                    # Clear all old frames first to minimize delay
                    while not self.frame_queue.empty():
                        try:
                            self.frame_queue.get_nowait()
                        except queue.Empty:
                            break
                    
                    # Add new frame
                    self.frame_queue.put_nowait(frame)
                    
                except queue.Full:
                    # If queue is full, drop oldest frame
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait(frame)
                    except queue.Empty:
                        pass
                except Exception as queue_error:
                    print(f"Frame queue error: {queue_error}")
                
                # Reduced delay for better real-time performance
                time.sleep(0.02)  # ~50 FPS max, but actual will be limited by camera
                    
            except Exception as e:
                consecutive_errors += 1
                print(f"Error in capture_frames: {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    print("Too many consecutive errors, attempting reconnection...")
                    self._reconnect_camera()
                    consecutive_errors = 0
                else:
                    time.sleep(0.1)
        
        print("Frame capture stopped")
        self.close_connection()

    def _monitor_connection(self):
        """Monitor camera connection and reconnect if needed"""
        while self.running:
            try:
                current_time = time.time()
                
                # Check if we haven't received frames for too long
                if current_time - self.last_frame_time > self.frame_timeout:
                    if not self.reconnect_in_progress:
                        print(f"Frame timeout detected ({current_time - self.last_frame_time:.1f}s), attempting reconnection...")
                        self._reconnect_camera()
                    
                time.sleep(3)
                
            except Exception as e:
                print(f"Error in connection monitor: {e}")
                time.sleep(5)

    def _reconnect_camera(self):
        """Reconnect to camera with better error handling"""
        if self.reconnect_in_progress:
            return
            
        if self.connection_retry_count >= self.max_retry_count:
            print("Max retry count reached, stopping...")
            self.running = False
            return
            
        self.reconnect_in_progress = True
        
        try:
            print(f"Reconnecting to camera (attempt {self.connection_retry_count + 1}/{self.max_retry_count})...")
            
            # Close existing connection first
            self.close_connection()
            
            # Clear frame queue
            self._clear_frame_queue()
            
            # Wait before reconnecting
            wait_time = min(2 + self.connection_retry_count * 2, 10)
            print(f"Waiting {wait_time} seconds before reconnection...")
            time.sleep(wait_time)
            
            if not self.running:
                return
            
            # Try to reconnect
            self.connect_camera()
            
            if self.cap and self.cap.isOpened():
                self.last_frame_time = time.time()
                print("Camera reconnected successfully")
                self.connection_retry_count = 0
            else:
                raise Exception("Failed to establish connection")
            
        except Exception as e:
            print(f"Reconnection failed: {e}")
            self.connection_retry_count += 1
            
            # If max retries reached, stop the system
            if self.connection_retry_count >= self.max_retry_count:
                print("Max retry attempts reached. Stopping camera system.")
                self.running = False
        finally:
            self.reconnect_in_progress = False

    def _validate_frame(self, frame):
        """Validate frame to catch corruption early"""
        if frame.size == 0:
            return False
            
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            print(f"Invalid frame shape: {frame.shape}")
            return False
            
        if frame.shape[0] == 0 or frame.shape[1] == 0:
            print(f"Zero dimension frame: {frame.shape}")
            return False
        
        return True

    def _clear_frame_queue(self):
        """Clear frame queue to remove old data"""
        try:
            while not self.frame_queue.empty():
                self.frame_queue.get_nowait()
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Error clearing frame queue: {e}")

    def close_connection(self):
        """Close camera connection safely"""
        try:
            if self.cap:
                self.cap.release()
                self.cap = None
                print("Camera connection closed")
        except Exception as e:
            print(f"Error closing camera connection: {e}")

    def get_connection_status(self):
        """Get current connection status"""
        return {
            'connected': self.cap is not None and self.cap.isOpened(),
            'retry_count': self.connection_retry_count,
            'max_retries': self.max_retry_count,
            'reconnecting': self.reconnect_in_progress,
            'last_frame_time': self.last_frame_time,
            'running': self.running
        }
