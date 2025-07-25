import tkinter as tk
from ui.main_window import MainWindow
from ui.pages import ModernLoginPage, CameraSelectPage
import os

# Environment setup
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Global variables for session data
current_users_org_id = None
current_users_org_name = None
current_access_token = None
current_data_camera = None


def main():
    root = tk.Tk()
    root.title("Smart School - Face Attendance System")
    root.geometry("1000x700")
    root.configure(bg="#f0f2f5")
    
    # Set minimum size
    root.minsize(800, 600)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    container = tk.Frame(root, bg="#f0f2f5")
    container.pack(fill="both", expand=True)

    def show_main_window(rtsp_url, camera_name):
        for widget in container.winfo_children():
            widget.destroy()
        app = MainWindow(container, "Smart School - Face Attendance System", rtsp_url, camera_name, current_access_token, current_users_org_id)
        app.pack(fill="both", expand=True)

    def show_camera_select():
        for widget in container.winfo_children():
            widget.destroy()
        cam_page = CameraSelectPage(container, on_select=show_main_window)
        cam_page.pack(fill="both", expand=True)

    def show_login():
        for widget in container.winfo_children():
            widget.destroy()
        login_page = ModernLoginPage(container, on_login=show_camera_select)
        login_page.pack(fill="both", expand=True)

    show_login()
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Program interrupted. Closing...")


if __name__ == "__main__":
    main()