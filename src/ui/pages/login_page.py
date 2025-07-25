"""
Modern Login Page Component
หน้าล็อกอินที่มีดีไซน์สวยงามพร้อม gradient background
"""

import tkinter as tk
import requests
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

# Add utils directory to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

# Try to import API utilities
try:
    import sys
    import os
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config'))
    if config_path not in sys.path:
        sys.path.insert(0, config_path)
    from global_config import get_api_endpoint, get_api_base_url
    
    # Test if config loads properly
    test_url = get_api_base_url()
    print(f"API Base URL loaded: {test_url}")
    
except ImportError as e:
    print(f"Could not import global_config: {e}")
    # Ultimate fallback only if everything fails
    def get_api_endpoint(category, endpoint):
        return "https://smart-school-uat.belib.app/api/auth"
    def get_api_base_url():
        return "https://smart-school-uat.belib.app/api"


class ModernLoginPage(tk.Frame):
    def __init__(self, parent, on_login):
        super().__init__(parent, bg="#f0f2f5")
        self.on_login = on_login
        
        # Create main container
        self.main_container = tk.Frame(self, bg="#f0f2f5")
        self.main_container.pack(fill="both", expand=True)
        
        # Create gradient background
        self.create_gradient_background()
        
        # Create login form
        self.create_login_form()
        
        # Force initial update after a short delay
        self.after(100, self.force_initial_update)
        
    def force_initial_update(self):
        """บังคับให้ canvas update ครั้งแรก"""
        if self.gradient_canvas.winfo_width() > 1 and self.gradient_canvas.winfo_height() > 1:
            self.update_gradient()
        else:
            # ลองใหม่หากยังไม่ได้ขนาด
            self.after(50, self.force_initial_update)
        
    def create_gradient_background(self):
        """สร้าง gradient background"""
        self.gradient_canvas = tk.Canvas(self.main_container, highlightthickness=0, bg="#26659f")
        self.gradient_canvas.pack(fill="both", expand=True)
        
        # Bind resize event
        self.gradient_canvas.bind('<Configure>', self.on_canvas_configure)
        
    def on_canvas_configure(self, event):
        """Update gradient when canvas is resized"""
        self.after_idle(self.update_gradient)
        
    def update_gradient(self):
        """Update gradient and form position"""
        self.gradient_canvas.delete("all")
        
        width = self.gradient_canvas.winfo_width()
        height = self.gradient_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
            
        # Create gradient from top to bottom
        self.create_gradient(self.gradient_canvas, "#26659f", "#00c5ad", width, height)
        
        # Redraw login form on canvas
        self.draw_login_form(width, height)
        
    def create_gradient(self, canvas, start_color, end_color, width, height):
        """สร้าง gradient บน Canvas"""
        steps = 50  # ลดจำนวน steps เพื่อประสิทธิภาพ
        r1, g1, b1 = self.hex_to_rgb(start_color)
        r2, g2, b2 = self.hex_to_rgb(end_color)
        
        for i in range(steps):
            r = int(r1 + (r2 - r1) * i / steps)
            g = int(g1 + (g2 - g1) * i / steps)
            b = int(b1 + (b2 - b1) * i / steps)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y1 = i * height / steps
            y2 = (i + 1) * height / steps
            canvas.create_rectangle(0, y1, width, y2, fill=color, outline=color)
    
    def hex_to_rgb(self, hex_color):
        """แปลงสี HEX เป็น RGB"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def create_login_form(self):
        """สร้าง login form (invisible frame for initial setup)"""
        # Create entry variables
        self.username_var = tk.StringVar(value="superadmin@bookdose.com")
        self.password_var = tk.StringVar(value="Bookdose4993!")
        
        # Load logo
        self.load_logo()
        
        # Initialize form elements
        self.username_entry = None
        self.password_entry = None
        self.login_button = None
        
    def load_logo(self):
        """โหลด logo"""
        try:
            # Get the path to the logo - navigate up from ui/pages to ui/images
            current_file_dir = os.path.dirname(os.path.abspath(__file__))  # ui/pages
            ui_dir = os.path.dirname(current_file_dir)  # ui
            logo_path = os.path.join(ui_dir, "images", "logo-bdpath.png")
            logo_path = os.path.normpath(logo_path)
            
            if os.path.exists(logo_path):
                image = Image.open(logo_path)
                # Resize logo
                desired_height = 80
                w, h = image.size
                new_width = int(w * desired_height / h)
                image = image.resize((new_width, desired_height), Image.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(image)
            else:
                self.logo_image = None
                print(f"Logo not found at: {logo_path}")
        except Exception as e:
            print(f"Error loading logo: {e}")
            self.logo_image = None
    
    def draw_login_form(self, canvas_width, canvas_height):
        """วาด login form บน canvas"""
        # Calculate center position
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Login form dimensions
        form_width = 380
        form_height = 480
        
        # Draw login card background
        card_x1 = center_x - form_width // 2
        card_y1 = center_y - form_height // 2
        card_x2 = center_x + form_width // 2
        card_y2 = center_y + form_height // 2
        
        # Add subtle shadow effect
        shadow_offset = 6
        self.gradient_canvas.create_rectangle(
            card_x1 + shadow_offset, card_y1 + shadow_offset, 
            card_x2 + shadow_offset, card_y2 + shadow_offset,
            fill="#000000", outline="", stipple="gray25"
        )
        
        # Create main login card - ใช้ rectangle ธรรมดาแต่สวยงาม
        self.gradient_canvas.create_rectangle(
            card_x1, card_y1, card_x2, card_y2,
            fill="white", outline="#e0e7ff", width=2
        )
        
        # Draw logo
        if self.logo_image:
            self.gradient_canvas.create_image(
                center_x, card_y1 + 70,
                image=self.logo_image, anchor="center"
            )
        
        # Draw title
        self.gradient_canvas.create_text(
            center_x, card_y1 + 130,
            text="Smart School", 
            font=("Segoe UI", 22, "bold"), 
            fill="#1e293b", anchor="center"
        )
        
        self.gradient_canvas.create_text(
            center_x, card_y1 + 160,
            text="Face Attendance System", 
            font=("Segoe UI", 11), 
            fill="#64748b", anchor="center"
        )
        
        # Create input fields
        self.create_canvas_inputs(center_x, center_y, form_width, card_y1)

    def create_canvas_inputs(self, center_x, center_y, form_width, card_y1):
        """สร้าง input fields บน canvas"""
        # Destroy existing widgets
        if hasattr(self, 'username_entry') and self.username_entry:
            self.username_entry.destroy()
        if hasattr(self, 'password_entry') and self.password_entry:
            self.password_entry.destroy()
        if hasattr(self, 'login_button') and self.login_button:
            self.login_button.destroy()
        
        # Username section
        self.gradient_canvas.create_text(
            center_x - 140, card_y1 + 200,
            text="Username", font=("Segoe UI", 10, "bold"), 
            fill="#374151", anchor="w"
        )
        
        # Username entry background
        self.gradient_canvas.create_rectangle(
            center_x - 140, card_y1 + 220,
            center_x + 140, card_y1 + 250,
            fill="#f8fafc", outline="#cbd5e1", width=1
        )
        
        # Modern username entry
        self.username_entry = tk.Entry(
            self.gradient_canvas,
            textvariable=self.username_var,
            font=("Segoe UI", 10),
            width=35,
            relief="flat",
            bd=0,
            highlightthickness=0,
            insertbackground="#1e293b",
            bg="#f8fafc",
            fg="#1e293b"
        )
        
        self.gradient_canvas.create_window(
            center_x, card_y1 + 235,
            window=self.username_entry
        )
        
        # Password section
        self.gradient_canvas.create_text(
            center_x - 140, card_y1 + 270,
            text="Password", font=("Segoe UI", 10, "bold"), 
            fill="#374151", anchor="w"
        )
        
        # Password entry background
        self.gradient_canvas.create_rectangle(
            center_x - 140, card_y1 + 290,
            center_x + 140, card_y1 + 320,
            fill="#f8fafc", outline="#cbd5e1", width=1
        )
        
        # Modern password entry
        self.password_entry = tk.Entry(
            self.gradient_canvas,
            textvariable=self.password_var,
            font=("Segoe UI", 10),
            width=35,
            show="*",
            relief="flat",
            bd=0,
            highlightthickness=0,
            insertbackground="#1e293b",
            bg="#f8fafc",
            fg="#1e293b"
        )
        
        self.gradient_canvas.create_window(
            center_x, card_y1 + 305,
            window=self.password_entry
        )
        
        # Login button background
        self.gradient_canvas.create_rectangle(
            center_x - 140, card_y1 + 350,
            center_x + 140, card_y1 + 390,
            fill="#3b82f6", outline="", width=0
        )
        
        # Modern login button
        self.login_button = tk.Button(
            self.gradient_canvas,
            text="LOGIN",
            command=self.try_login,
            font=("Segoe UI", 11, "bold"),
            bg="#3b82f6",
            fg="white",
            relief="flat",
            bd=0,
            width=32,
            height=2,
            cursor="hand2",
            activebackground="#2563eb",
            activeforeground="white"
        )
        
        self.gradient_canvas.create_window(
            center_x, card_y1 + 370,
            window=self.login_button
        )
        
        # Add hover effects
        self.add_button_hover_effects()
        
        # Set focus and bindings
        self.username_entry.focus_set()
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus_set())
        self.password_entry.bind('<Return>', lambda e: self.try_login())
        
        # Add focus effects
        self.add_input_focus_effects()

    def add_input_focus_effects(self):
        """เพิ่ม focus effects สำหรับ input fields"""
        def on_username_focus_in(e):
            self.username_entry.config(bg="white")
            
        def on_username_focus_out(e):
            self.username_entry.config(bg="#f8fafc")
            
        def on_password_focus_in(e):
            self.password_entry.config(bg="white")
            
        def on_password_focus_out(e):
            self.password_entry.config(bg="#f8fafc")
    
        self.username_entry.bind("<FocusIn>", on_username_focus_in)
        self.username_entry.bind("<FocusOut>", on_username_focus_out)
        self.password_entry.bind("<FocusIn>", on_password_focus_in)
        self.password_entry.bind("<FocusOut>", on_password_focus_out)

    def add_button_hover_effects(self):
        """เพิ่ม hover effects สำหรับปุ่ม"""
        def on_enter(e):
            self.login_button.config(bg="#2563eb")
            
        def on_leave(e):
            self.login_button.config(bg="#3b82f6")
    
        def on_click(e):
            self.login_button.config(bg="#1d4ed8")
            self.after(100, lambda: self.login_button.config(bg="#2563eb"))
            
        self.login_button.bind("<Enter>", on_enter)
        self.login_button.bind("<Leave>", on_leave)
        self.login_button.bind("<Button-1>", on_click)
    
    def try_login(self):
        """ทำการ login"""
        email = self.username_var.get()
        password = self.password_var.get()
        
        if not email or not password:
            messagebox.showerror("Error", "กรุณากรอก Username และ Password")
            return
            
        url = get_api_endpoint("auth", "login")
        data = {
            "email": email,
            "password": password,
            "device": "web",
            "user_group": "teacher"
        }
        
        # Change button state during login
        original_text = self.login_button.cget("text")
        self.login_button.config(text="LOGGING IN...", state="disabled", bg="#cccccc")
        self.gradient_canvas.update()
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                response_data = response.json()
                if response_data["status"] == "success":
                    messagebox.showinfo("Login Success", "เข้าสู่ระบบสำเร็จ")
                    # Store the users_org_id from the response
                    users_org_id = response_data["results"]["user"]["users_org_id"]
                    users_org_name = response_data["results"]["user"]["org"]["name_th"]
                    access_token = response_data["results"]["backendTokens"]["accessToken"]
                    data_camera = response_data["results"]["user"]["org"]["data_camera"]
                    
                    # Store in global variables
                    import __main__
                    __main__.current_users_org_id = users_org_id
                    __main__.current_users_org_name = users_org_name
                    __main__.current_access_token = access_token
                    __main__.current_data_camera = data_camera
                    
                    self.on_login()
                elif response_data["status"] == "error":
                    if response_data.get("message") == "Invalid email or password":
                        messagebox.showerror("Login Failed", "อีเมลหรือรหัสผ่านไม่ถูกต้อง")
                    else:
                        messagebox.showerror("Login Failed", "เกิดข้อผิดพลาดในการเข้าสู่ระบบ")
                else:
                    messagebox.showerror("Login Failed", "เกิดข้อผิดพลาดในการเข้าสู่ระบบ")
            else:
                messagebox.showerror("Login Failed", "อีเมลหรือรหัสผ่านไม่ถูกต้อง")
        except requests.exceptions.Timeout:
            messagebox.showerror("Error", "การเชื่อมต่อหมดเวลา กรุณาลองใหม่อีกครั้ง")
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้\n{e}")
        finally:
            # Reset button state - check if button still exists
            try:
                if hasattr(self, 'login_button') and self.login_button and self.login_button.winfo_exists():
                    self.login_button.config(text=original_text, state="normal", bg="#3b82f6")
            except tk.TclError:
                # Button was destroyed (page changed), ignore the error
                pass
