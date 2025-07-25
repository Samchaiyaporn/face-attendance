# Troubleshooting Guide - คู่มือการแก้ไขปัญหา

## ปัญหาที่พบบ่อย

### 🚫 ปัญหาการติดตั้ง

#### Python Version ไม่ถูกต้อง
```bash
# ตรวจสอบ Python version
python --version

# ถ้าไม่ใช่ 3.8+ ให้ติดตั้งใหม่จาก python.org
```

#### Virtual Environment ไม่ทำงาน
```bash
# สร้าง virtual environment ใหม่
python -m venv .venv

# เปิดใช้งาน (Windows)
.venv\Scripts\activate

# เปิดใช้งาน (macOS/Linux)
source .venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt
```

#### Package Installation ล้มเหลว
```bash
# อัพเกรด pip
python -m pip install --upgrade pip

# ติดตั้งแต่ละ package ทีละตัว
pip install customtkinter
pip install opencv-python
pip install insightface

# ถ้ายังไม่ได้ ใช้ --no-cache-dir
pip install --no-cache-dir -r requirements.txt
```

### 📷 ปัญหากล้อง

#### กล้องไม่ทำงาน
```python
# ทดสอบกล้อง
import cv2

# ตรวจสอบกล้องที่มี
for i in range(4):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i}: Available")
        cap.release()
    else:
        print(f"Camera {i}: Not available")
```

#### IP Camera เชื่อมต่อไม่ได้
1. **ตรวจสอบ IP address**
   ```bash
   ping <ip_address>
   ```

2. **ตรวจสอบ RTSP URL**
   ```python
   import cv2
   cap = cv2.VideoCapture('rtsp://username:password@ip:port/stream')
   print(cap.isOpened())
   ```

3. **ตรวจสอบ Firewall**
   - เปิด port ที่จำเป็น
   - ปิด Windows Defender Firewall ชั่วคราว

#### ภาพจากกล้องไม่ชัด
1. **ปรับ resolution**
   ```python
   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
   ```

2. **ปรับแสง**
   - เพิ่มแสงสว่าง
   - หลีกเลี่ยงแสงแบ็คไลท์

3. **ทำความสะอาดเลนส์**

### 🤖 ปัญหา Face Recognition

#### Face Recognition ไม่แม่นยำ
1. **ปรับ threshold**
   ```python
   # ลดค่า threshold เพื่อความแม่นยำมากขึ้น
   threshold = 0.6  # จาก 0.7
   ```

2. **ปรับขนาดรูปภาพ**
   ```python
   # ปรับขนาดรูปก่อนประมวลผล
   face_img = cv2.resize(face_img, (112, 112))
   ```

3. **เพิ่มข้อมูลการเรียนรู้**
   - ถ่ายรูปหน้าในมุมต่างๆ
   - ถ่ายในแสงที่แตกต่างกัน

#### InsightFace Model ไม่โหลด
```bash
# ดาวน์โหลด model ใหม่
pip uninstall insightface
pip install insightface

# หรือโหลด model manual
import insightface
app = insightface.app.FaceAnalysis()
app.prepare(ctx_id=0, det_size=(640, 640))
```

### 🖥️ ปัญหา UI

#### CustomTkinter ไม่แสดงผล
```bash
# อัพเดต CustomTkinter
pip install --upgrade customtkinter

# ตรวจสอบ Tkinter
python -c "import tkinter; print('Tkinter OK')"
```

#### Font ไม่แสดงผลภาษาไทย
```python
import customtkinter as ctk

# ใช้ font ที่รองรับภาษาไทย
font = ctk.CTkFont(family="Tahoma", size=14)
label = ctk.CTkLabel(parent, text="ข้อความภาษาไทย", font=font)
```

#### UI แช่แข็ง (Freezing)
```python
# ใช้ threading สำหรับงานหนัก
import threading

def heavy_task():
    # งานที่ใช้เวลานาน
    pass

# รันใน thread แยก
thread = threading.Thread(target=heavy_task)
thread.daemon = True
thread.start()
```

### 🌐 ปัญหา Network Scanner

#### Network Scanner ไม่ทำงาน
1. **ติดตั้ง nmap**
   ```bash
   # Windows: ดาวน์โหลดจาก nmap.org
   # macOS: brew install nmap
   # Linux: sudo apt-get install nmap
   ```

2. **ตรวจสอบ network permissions**
   - รันโปรแกรมใน Administrator mode
   - ตรวจสอบ network adapter settings

3. **ทดสอบ network connection**
   ```bash
   ping 192.168.1.1
   arp -a
   ```

### 💾 ปัญหาข้อมูล

#### ไฟล์ข้อมูลเสียหาย
```python
import json
import os

# สำรองข้อมูล
def backup_data():
    try:
        if os.path.exists('data/attendance.json'):
            import shutil
            shutil.copy('data/attendance.json', 'data/attendance_backup.json')
        print("Backup completed")
    except Exception as e:
        print(f"Backup failed: {e}")

# กู้คืนข้อมูล
def restore_data():
    try:
        if os.path.exists('data/attendance_backup.json'):
            import shutil
            shutil.copy('data/attendance_backup.json', 'data/attendance.json')
        print("Restore completed")
    except Exception as e:
        print(f"Restore failed: {e}")
```

#### Config ไฟล์หาย
```python
# สร้าง config default
default_config = {
    "camera": {
        "default_index": 0,
        "resolution": [1280, 720],
        "fps": 30
    },
    "face_recognition": {
        "threshold": 0.7,
        "model": "buffalo_l"
    },
    "ui": {
        "theme": "dark",
        "font_size": 14
    }
}

import json
with open('config/settings.json', 'w') as f:
    json.dump(default_config, f, indent=4)
```

## การแก้ไขปัญหาเฉพาะ

### Performance Issues

#### โปรแกรมช้า
1. **ปรับ frame rate**
   ```python
   # ลด FPS
   import time
   time.sleep(0.1)  # หน่วงเวลา 100ms ระหว่าง frame
   ```

2. **ปรับขนาดรูปภาพ**
   ```python
   # ลดขนาดรูปก่อนประมวลผล
   small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
   ```

3. **ใช้ threading**
   ```python
   import concurrent.futures
   
   with concurrent.futures.ThreadPoolExecutor() as executor:
       future = executor.submit(face_recognition_task, frame)
       result = future.result()
   ```

#### Memory Leak
```python
import gc

def cleanup_memory():
    """ทำความสะอาด memory"""
    gc.collect()

# เรียกใช้เป็นระยะ
import threading
import time

def memory_cleanup_timer():
    while True:
        time.sleep(300)  # ทุก 5 นาที
        cleanup_memory()

cleanup_thread = threading.Thread(target=memory_cleanup_timer)
cleanup_thread.daemon = True
cleanup_thread.start()
```

### Error Messages

#### "No module named 'cv2'"
```bash
pip uninstall opencv-python
pip install opencv-python
```

#### "No module named 'insightface'"
```bash
pip install insightface
```

#### "DLL load failed"
```bash
# ติดตั้ง Visual C++ Redistributable
# ดาวน์โหลดจาก Microsoft

# หรือใช้ conda
conda install opencv
```

#### "Permission denied"
```bash
# รันใน Administrator mode
# หรือเปลี่ยน permissions
chmod 755 script.py
```

## การ Debug

### เปิด Debug Mode
```python
import logging

# ตั้งค่า logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# ใช้งาน
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### ตรวจสอบ System Information
```python
import platform
import sys
import cv2
import numpy as np

def system_info():
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"OpenCV version: {cv2.__version__}")
    print(f"NumPy version: {np.__version__}")
    
    # ตรวจสอบ GPU
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        print(f"ONNX providers: {providers}")
    except ImportError:
        print("ONNX Runtime not installed")

system_info()
```

## การขอความช่วยเหลือ

### เมื่อพบปัญหาที่แก้ไม่ได้

1. **รวบรวมข้อมูล**
   - Error message ที่สมบูรณ์
   - ขั้นตอนที่ทำให้เกิดปัญหา
   - System information
   - Python version และ package versions

2. **สร้าง Issue**
   - อธิบายปัญหาอย่างชัดเจน
   - แนบ error logs
   - ระบุสิ่งที่คาดหวัง vs สิ่งที่เกิดขึ้นจริง

3. **หา Documentation**
   - ตรวจสอบ README.md
   - ดู DEVELOPMENT.md
   - อ่าน CHANGELOG.md

### Log Files ที่สำคัญ
- `debug.log` - Debug information
- `error.log` - Error messages
- `performance.log` - Performance metrics

### Useful Commands
```bash
# ตรวจสอบ Python environment
python -m pip list

# ตรวจสอบ system
systeminfo  # Windows
uname -a    # macOS/Linux

# ตรวจสอบ network
ipconfig    # Windows
ifconfig    # macOS/Linux
```
