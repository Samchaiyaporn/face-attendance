# Changelog - บันทึกการเปลี่ยนแปลง

## Version 2.0.0 (Current)

### 🎉 Major Features Added
- **Modular Architecture**: แบ่งโค้ดเป็น modules ที่ชัดเจน
- **Network Scanner**: สแกนหากล้อง IP ในเครือข่ายอัตโนมัติ
- **Improved UI**: ปรับปรุง UI ด้วย CustomTkinter
- **Progress Dialog**: แสดงสถานะการทำงาน
- **User Count Display**: แสดงจำนวนผู้ใช้ที่ลงทะเบียน
- **Refresh Button**: ปุ่มรีเฟรชข้อมูล

### 🔧 Technical Improvements
- **Code Refactoring**: แบ่งโค้ดจาก main.py เป็น modules
- **Better Error Handling**: จัดการ error ได้ดีขึ้น
- **Performance Optimization**: ปรับปรุงประสิทธิภาพ
- **Memory Management**: จัดการ memory ได้ดีขึ้น

### 📁 File Structure
```
src/
├── main.py                    # Entry point
├── core/                      # Core functionality
│   ├── api/
│   │   └── api_client.py     # API client
│   ├── attendance/
│   │   └── attendance_manager.py  # Attendance management
│   ├── camera/
│   │   └── camera_handler.py # Camera handling
│   └── face_recognition/
│       └── face_manager.py   # Face recognition
├── ui/                       # User interface
│   ├── main_window.py        # Main window
│   ├── components/           # UI components
│   │   ├── header.py
│   │   ├── camera_ui.py
│   │   ├── camera_section_new.py
│   │   ├── progress_dialog.py
│   │   └── attendance_list.py
│   └── pages/               # UI pages
│       ├── login_page.py
│       └── camera_select_page.py
└── utils/                   # Utilities
    └── network_scanner.py   # Network scanner
```

### 🐛 Bug Fixes
- Fixed camera connection issues
- Fixed face recognition accuracy
- Fixed UI responsiveness
- Fixed memory leaks
- Fixed logo path issues

### 📦 Dependencies Updated
- Updated to latest CustomTkinter
- Updated OpenCV version
- Added network scanning capabilities
- Optimized package requirements

## Version 1.0.0 (Previous)

### Initial Features
- Basic face recognition
- Simple camera support
- Basic attendance tracking
- Simple UI interface

### Known Issues (Fixed in 2.0.0)
- Monolithic code structure
- Limited camera support
- Basic UI design
- No network scanning
- Memory leaks
- Performance issues

## Roadmap - แผนการพัฒนาต่อไป

### Version 2.1.0 (Planned)
- [ ] Database integration
- [ ] Advanced reporting
- [ ] Multi-language support
- [ ] Export functionality
- [ ] Admin panel

### Version 2.2.0 (Future)
- [ ] Mobile app support
- [ ] Cloud synchronization
- [ ] Advanced analytics
- [ ] Integration with school systems
- [ ] API for third-party integration

### Version 3.0.0 (Long-term)
- [ ] AI-powered features
- [ ] Advanced security
- [ ] Microservices architecture
- [ ] Scalable deployment
- [ ] Enterprise features

## Migration Guide

### จาก Version 1.0.0 ไป 2.0.0

#### ขั้นตอนการอัพเกรด:
1. **Backup ข้อมูลเดิม**
   ```bash
   copy data\attendance.json backup\attendance_v1.json
   copy config\settings.json backup\settings_v1.json
   ```

2. **อัพเดต dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **ไฟล์ที่เปลี่ยนแปลง**
   - `main.py` → แบ่งเป็น modules ใน `src/`
   - `camera.py` → `src/core/camera/camera_handler.py`
   - `face_recognition.py` → `src/core/face_recognition/face_manager.py`

4. **การตั้งค่าใหม่**
   - UI settings ใน config file
   - Network scanner settings
   - Performance optimization settings

#### Breaking Changes:
- File paths ใหม่สำหรับ modules
- API changes ใน core functions
- Config file format ใหม่

#### Compatibility:
- ข้อมูล attendance เดิมยังใช้ได้
- การตั้งค่ากล้องเดิมยังใช้ได้
- Face recognition models เดิมยังใช้ได้

## Contributors

### Version 2.0.0
- **Code Refactoring**: แบ่ง monolithic code เป็น modules
- **UI Improvements**: ปรับปรุง interface ใหม่ทั้งหมด
- **Network Features**: เพิ่ม network scanner
- **Documentation**: สร้างเอกสารครบถ้วน
- **Build System**: ระบบ build และ deployment

### Acknowledgments
- OpenCV community
- CustomTkinter developers
- InsightFace team
- Python community
