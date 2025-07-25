"""
Network Scanner Module
สำหรับสแกนหากล้อง IP ในเครือข่ายเดียวกัน
"""

import socket
import subprocess
import threading
import time
import ipaddress
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


class NetworkScanner:
    def __init__(self):
        self.camera_ports = [554, 8080, 80, 8554, 1935, 8000, 9999, 37777, 88, 8088]
        self.common_rtsp_paths = [
            "/Streaming/Channels/101",
            "/Streaming/Channels/1/Preview",
            "/stream",
            "/live",
            "/cam/realmonitor?channel=1&subtype=0",
            "/videostream.cgi?user=admin&pwd=admin",
            "/axis-cgi/mjpg/video.cgi",
            "/cgi-bin/camera?resolution=640&quality=1",
            "/mjpg/video.mjpg",
            "/h264/ch1/main/av_stream",
            "/ch0_0.h264"
        ]
        
    def get_local_network(self):
        """หาเครือข่าย local ที่เครื่องเชื่อมต่ออยู่"""
        try:
            # Get default gateway
            if hasattr(socket, 'gethostbyname_ex'):
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
            else:
                # Alternative method
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
            
            # Create network range (assume /24 subnet)
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            return str(network), local_ip
            
        except Exception as e:
            print(f"Error getting local network: {e}")
            return "192.168.1.0/24", "192.168.1.100"  # Default fallback

    def scan_ip_for_camera(self, ip, timeout=2):
        """สแกน IP เดียวหากล้อง"""
        camera_info = None
        
        for port in self.camera_ports:
            if self.check_port_open(ip, port, timeout=timeout):
                camera_info = {
                    'ip': ip,
                    'port': port,
                    'status': 'online',
                    'type': self.detect_camera_type(ip, port),
                    'rtsp_urls': self.generate_rtsp_urls(ip, port),
                    'default_rtsp': f"rtsp://admin:admin@{ip}:554/Streaming/Channels/101"
                }
                break
                
        return camera_info

    def check_port_open(self, ip, port, timeout=2):
        """ตรวจสอบว่า port เปิดอยู่หรือไม่"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                return result == 0
        except:
            return False

    def detect_camera_type(self, ip, port):
        """ตรวจสอบประเภทกล้อง"""
        try:
            # Check HTTP response for camera identification
            if port in [80, 8080, 88, 8088]:
                try:
                    response = requests.get(f"http://{ip}:{port}", timeout=3, allow_redirects=True)
                    headers = response.headers
                    content = response.text.lower()
                    
                    # Check for specific camera brands
                    if 'hikvision' in content or 'hikvision' in str(headers).lower():
                        return 'Hikvision Camera'
                    elif 'dahua' in content or 'dahua' in str(headers).lower():
                        return 'Dahua Camera'
                    elif 'axis' in content or 'axis' in str(headers).lower():
                        return 'Axis Camera'
                    elif 'foscam' in content or 'foscam' in str(headers).lower():
                        return 'Foscam Camera'
                    elif 'tp-link' in content or 'tplink' in content:
                        return 'TP-Link Camera'
                    elif 'netcam' in content or 'ipcam' in content:
                        return 'IP Camera'
                    elif 'webcam' in content or 'camera' in content:
                        return 'Web Camera'
                    elif '<title>' in content and 'camera' in content:
                        return 'IP Camera'
                    else:
                        return 'Generic Camera'
                except Exception as e:
                    # If HTTP fails, still consider it a potential camera
                    return 'IP Camera'
                    
            # RTSP port
            elif port == 554:
                return 'RTSP Camera'
            elif port == 8554:
                return 'RTSP Stream'
            elif port == 1935:
                return 'RTMP Camera'
            else:
                return 'Network Camera'
                
        except Exception as e:
            return f'Camera (Port {port})'

    def generate_rtsp_urls(self, ip, port):
        """สร้าง RTSP URLs ที่เป็นไปได้ในรูปแบบ rtsp://admin:admin@ip:554/path"""
        urls = []
        
        # Standard RTSP URLs with common credentials and paths
        credentials = ['admin:admin', 'admin:', 'admin:12345', 'admin:password', 'user:user']
        
        # Most common RTSP paths for different camera brands
        common_paths = [
            '/Streaming/Channels/101',           # Hikvision main stream
            '/Streaming/Channels/1/Preview',     # Hikvision sub stream
            '/cam/realmonitor?channel=1&subtype=0',  # Dahua
            '/h264/ch1/main/av_stream',          # Some Chinese cameras
            '/stream',                           # Generic
            '/live',                             # Generic
            '/ch0_0.h264'                        # Some IP cameras
        ]
        
        # Always use port 554 for RTSP regardless of detected port
        for cred in credentials:
            for path in common_paths:
                urls.append(f"rtsp://{cred}@{ip}:554{path}")
                        
        return urls[:10]  # Return only first 10 URLs to avoid too many attempts

    def scan_network_range(self, network_range, progress_callback=None, max_workers=50):
        """สแกนเครือข่ายทั้งหมด"""
        cameras = []
        network = ipaddress.IPv4Network(network_range)
        ip_list = [str(ip) for ip in network.hosts()]
        
        total_ips = len(ip_list)
        scanned_count = 0
        
        def scan_single_ip(ip):
            nonlocal scanned_count
            camera = self.scan_ip_for_camera(ip, timeout=1)
            scanned_count += 1
            
            if progress_callback:
                progress = int((scanned_count / total_ips) * 100)
                progress_callback(f"สแกน IP: {ip}", progress)
                
            return camera
        
        # Use ThreadPoolExecutor for concurrent scanning
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ip = {executor.submit(scan_single_ip, ip): ip for ip in ip_list}
            
            for future in as_completed(future_to_ip):
                camera = future.result()
                if camera:
                    cameras.append(camera)
                    
        return cameras

    def quick_scan_common_ips(self, local_ip, progress_callback=None):
        """สแกน IP ทั่วไปอย่างรวดเร็ว"""
        # Extract network prefix
        ip_parts = local_ip.split('.')
        network_prefix = '.'.join(ip_parts[:3])
        
        # Common IP ranges for cameras
        common_ips = []
        # Router and common device IPs
        common_ips.extend([f"{network_prefix}.{i}" for i in [1, 254]])
        # Common camera IP ranges
        common_ips.extend([f"{network_prefix}.{i}" for i in range(100, 120)])
        common_ips.extend([f"{network_prefix}.{i}" for i in range(200, 210)])
        # Additional common IPs
        common_ips.extend([f"{network_prefix}.{i}" for i in [2, 3, 4, 5, 10, 20, 50, 99, 150, 250]])
        
        cameras = []
        total_ips = len(common_ips)
        
        def scan_ip_worker(ip):
            return self.scan_ip_for_camera(ip, timeout=1.5)
        
        # Use ThreadPoolExecutor for faster scanning
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_ip = {executor.submit(scan_ip_worker, ip): ip for ip in common_ips}
            
            for i, future in enumerate(as_completed(future_to_ip)):
                if progress_callback:
                    progress = int((i / total_ips) * 100)
                    ip = future_to_ip[future]
                    progress_callback(f"สแกน IP: {ip}", progress)
                
                camera = future.result()
                if camera:
                    cameras.append(camera)
                    print(f"Found camera: {camera['ip']}:{camera['port']} ({camera['type']})")
                
        return cameras

    def ping_ip(self, ip):
        """Ping IP เพื่อตรวจสอบว่า online อยู่หรือไม่"""
        try:
            # Windows
            result = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], 
                                  capture_output=True, text=True, timeout=3)
            return result.returncode == 0
        except:
            try:
                # Linux/Mac fallback
                result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                                      capture_output=True, text=True, timeout=3)
                return result.returncode == 0
            except:
                return False

    def test_rtsp_url(self, rtsp_url, timeout=5):
        """ทดสอบ RTSP URL ว่าใช้งานได้หรือไม่"""
        try:
            import cv2
            cap = cv2.VideoCapture(rtsp_url)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Try to read one frame
            ret, frame = cap.read()
            cap.release()
            
            return ret and frame is not None
        except:
            return False
