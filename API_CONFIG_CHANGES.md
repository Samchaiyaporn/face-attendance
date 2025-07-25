# 🎯 API Configuration Changes Summary

## 📋 สรุปการเปลี่ยนแปลง

### ✅ 1. ปลด installer folder ออกจาก .gitignore
- **แก้ไข**: `.gitignore`
- **รายละเอียด**: ลบ `installer/` ออกจาก .gitignore เพื่อให้ folder installer ถูก track ใน git
- **ผลลัพธ์**: installer folder จะถูกเก็บใน repository

### ✅ 2. กำหนดค่า API URL เป็น https://smart-school-uat.belib.app
- **แก้ไข**: `config/settings.json`, `installer/config/settings.json`
- **เพิ่ม**: `config/api_config.py`, `config/api_loader.py`
- **รายละเอียด**: 
  ```json
  "api": {
    "base_url": "https://smart-school-uat.belib.app",
    "api_path": "/api",
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1.0
  }
  ```

### ✅ 3. แก้ไขทุกที่ที่เรียก API ให้ใช้ configuration
- **แก้ไข**: 
  - `src/core/api/api_client.py`
  - `src/ui/pages/login_page.py`
  - `src/ui/components/camera_section_new.py`
  - `src/ui/main_window.py`
  - `src/utils/api_utils.py`
- **เพิ่ม**: Centralized API configuration loading
- **รายละเอียด**: เปลี่ยนจาก hard-coded URL เป็นการอ่านค่าจาก config files

## 🔧 ไฟล์ที่สร้างใหม่

### 1. `config/api_config.py`
- ไฟล์กำหนดค่า API หลัก
- มี functions: `get_api_url()`, `get_base_api_url()`, `get_headers()`, etc.

### 2. `config/api_loader.py`
- API configuration loader ที่ใช้ได้จากทุกที่
- Singleton pattern สำหรับ configuration
- มี fallback mechanism

### 3. `src/utils/api_utils.py`
- Utility functions สำหรับการจัดการ API
- รองรับการโหลด config จากหลาย location
- มี fallback values

## 🎯 วิธีการทำงาน

### Priority Order ของการโหลด Configuration:
1. **Primary**: `config/settings.json`
2. **Secondary**: `installer/config/settings.json`  
3. **Fallback**: Hard-coded default values

### API Endpoints ที่รองรับ:
```python
# Authentication
get_api_endpoint("auth", "login")  # /api/auth
get_api_endpoint("auth", "logout") # /api/auth/logout

# Students
get_api_endpoint("students", "list")   # /api/users/group/student
get_api_endpoint("students", "detail", id="123") # /api/users/123

# Attendance
get_api_endpoint("attendance", "mark") # /api/face-attendance

# Health Check
get_api_endpoint("health", "check")    # /api/health
```

## 🚀 ประโยชน์ของการเปลี่ยนแปลง

### ✅ **Centralized Configuration**
- เปลี่ยน API URL ได้ที่เดียว (config/settings.json)
- ไม่ต้องแก้ไขโค้ดในหลายที่

### ✅ **Environment Support**
- สามารถใช้ config แยกสำหรับ dev, staging, production
- เปลี่ยน environment ได้ง่าย

### ✅ **Fallback Mechanism**
- ถ้าโหลด config ไม่ได้ จะใช้ default values
- ระบบยังทำงานได้แม้ config file หาย

### ✅ **Build Integration**
- ULTIMATE_BUILD.bat อ่าน API URL จาก config
- Installer จะใช้ URL ที่ถูกต้อง

## 📝 การใช้งาน

### เปลี่ยน API URL:
1. แก้ไข `config/settings.json`:
   ```json
   {
     "api": {
       "base_url": "https://your-new-api.com",
       "api_path": "/api"
     }
   }
   ```

2. Build ใหม่:
   ```bash
   ULTIMATE_BUILD.bat
   ```

### เพิ่ม Endpoint ใหม่:
1. แก้ไข `config/api_loader.py` หรือ `src/utils/api_utils.py`
2. เพิ่ม endpoint ใน dictionary
3. ใช้งาน: `get_api_endpoint("category", "endpoint")`

## ✅ สถานะ

- [x] ปลด installer folder ออกจาก .gitignore
- [x] กำหนด API URL = https://smart-school-uat.belib.app  
- [x] แก้ไขทุกการเรียก API ให้ใช้ configuration
- [x] สร้าง fallback mechanism
- [x] อัปเดต build script
- [x] สร้างเอกสารประกอบ

## 🎉 ผลลัพธ์
ระบบตอนนี้ใช้ configuration-based API URL แล้ว ไม่มี hard-coded URL ในโค้ดหลักแล้ว (มีแค่ fallback values)
