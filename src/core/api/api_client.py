"""
API Client Module
จัดการการเชื่อมต่อและการส่งข้อมูลไปยัง API
"""

import requests
import threading
from io import BytesIO
from PIL import Image
import sys
import os

# Add utils directory to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

try:
    import sys
    import os
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config'))
    if config_path not in sys.path:
        sys.path.insert(0, config_path)
    from global_config import get_api_base_url, get_api_timeout
    
    # Test if config loads properly
    test_url = get_api_base_url()
    test_timeout = get_api_timeout()
    print(f"API Client - API Base URL loaded: {test_url}, timeout: {test_timeout}")
    API_TIMEOUT = test_timeout
    
except ImportError as e:
    print(f"API Client - Could not import global_config: {e}")
    # Ultimate fallback only if everything fails
    def get_api_base_url():
        return "https://smart-school-uat.belib.app/api"
    API_TIMEOUT = 30


class APIClient:
    def __init__(self, access_token, api_url=None):
        # Use centralized config if no API URL provided
        self.api_url = api_url or get_api_base_url()
        self.access_token = access_token

    def fetch_students(self, progress_callback=None):
        """Fetch student data from API with progress callback"""
        url = f"{self.api_url}/users/group/student"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        try:
            if progress_callback:
                progress_callback("กำลังเชื่อมต่อ API...", 0)
                
            print(f"Fetching students from: {url}")
            response = requests.get(url, headers=headers, params={"limit": "100000"}, timeout=API_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if progress_callback:
                progress_callback("ได้รับข้อมูลจาก API...", 10)
            
            if "results" not in data or "data" not in data["results"]:
                print("Invalid API response structure")
                return []
                
            students = []
            user_list = data["results"]["data"]
            total_users = len(user_list)
            
            if progress_callback:
                progress_callback(f"กำลังโหลดข้อมูลนักเรียน {total_users} คน...", 20)
            
            for i, user in enumerate(user_list):
                display_name = user.get("display_name", "")
                member_id = user.get("member_id", "")
                avatar_path = user.get("avatar_path", "")
                
                # Update progress for avatar loading
                if progress_callback and total_users > 0:
                    progress = 20 + int((i / total_users) * 60)  # 20% to 80%
                    progress_callback(f"กำลังโหลดรูปภาพ: {display_name}", progress)
                
                avatar_image = None
                if avatar_path:
                    avatar_image = self._load_avatar_image(display_name, avatar_path)
                        
                students.append({
                    "display_name": display_name,
                    "avatar_path": avatar_path,
                    "avatar_image": avatar_image,
                    "member_id": member_id
                })
                
            if progress_callback:
                progress_callback(f"โหลดข้อมูลเสร็จสิ้น: {len(students)} คน", 80)
                
            print(f"Total students processed: {len(students)}")
            return students
            
        except Exception as e:
            print(f"Failed to fetch students: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _load_avatar_image(self, display_name, avatar_path):
        """Load avatar image from URL"""
        try:
            print(f"Loading avatar for {display_name} from {avatar_path}")
            img_response = requests.get(avatar_path, timeout=10)
            img_response.raise_for_status()
            
            # Check content type
            content_type = img_response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"Invalid content type for {display_name}: {content_type}")
                return None
                
            # Check file size
            if len(img_response.content) == 0:
                print(f"Empty image file for {display_name}")
                return None
                
            avatar_image = Image.open(BytesIO(img_response.content))
            
            # Check image format
            if avatar_image.format not in ['JPEG', 'PNG', 'BMP', 'TIFF']:
                print(f"Unsupported image format for {display_name}: {avatar_image.format}")
                return None
            
            # Check image size
            if avatar_image.size[0] == 0 or avatar_image.size[1] == 0:
                print(f"Invalid image size for {display_name}: {avatar_image.size}")
                return None
                
            print(f"✅ Successfully loaded avatar for {display_name}")
            return avatar_image
            
        except Exception as e:
            print(f"❌ Failed to load avatar for {display_name}: {e}")
            return None

    def send_attendance(self, member_id, users_org_id, camera_name):
        """Send attendance data to API"""
        api_data = {
            "member_id": member_id,
            "users_org_id": users_org_id,
            'comment': camera_name,
        }

        # Run in separate thread to avoid blocking
        threading.Thread(
            target=self._send_attendance_api,
            args=(api_data, member_id),
            daemon=True
        ).start()

    def _send_attendance_api(self, data_attendance, member_id):
        """Send attendance data to API (internal method)"""
        try:
            response = requests.post(
                f"{self.api_url}/face-attendance",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                json=data_attendance,
                timeout=5
            )
            response.raise_for_status()
            print(f"Attendance recorded successfully for member_id: {member_id}")
        except Exception as e:
            print(f"Failed to record attendance for member_id: {member_id}. Error: {e}")

    def update_token(self, new_token):
        """Update access token"""
        self.access_token = new_token

    def test_connection(self):
        """Test API connection"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=API_TIMEOUT)
            return response.status_code == 200
        except:
            return False
