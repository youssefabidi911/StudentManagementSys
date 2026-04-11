# main.py
import customtkinter as ctk
from tkinter import messagebox
from database_manager import DatabaseManager
from auth_manager import AuthManager
from login_window import LoginWindow

# Import UI components
from ui_components import (
    DashboardView, StudentFormView, GradeManagementView,
    AttendanceView, SearchView, StudentListView,
    StatisticsView, UserManagementView, Sidebar
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")



class StudentManagementApp:
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Student Management System")
        self.root.geometry("1400x800")
        self.root.resizable(True, True)
        self.root.wm_iconbitmap("student.ico")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize database and auth managers
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthManager(self.db_manager)
        
        # Main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Content frame (will be updated)
        self.content_frame = ctk.CTkFrame(self.main_container)
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Sidebar (initially hidden)
        self.sidebar = None
        self.current_view = None
        
        # Show login window
        self.show_login()
        
        self.root.mainloop()
    
    def show_login(self):
        """Show login window"""
        self.login_window = LoginWindow(self.root, self.auth_manager, self.on_login_success)
    
    def on_login_success(self):
        """Called after successful login"""
        self.show_main_interface()
    
    def show_main_interface(self):
        """Show main application interface"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create sidebar
        self.sidebar = Sidebar(self.main_container, self, self.auth_manager)
        
        # Show dashboard by default
        self.show_dashboard()
    
    def clear_content(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show dashboard view"""
        self.clear_content()
        self.current_view = DashboardView(self.content_frame, self.db_manager)
    
    def show_add_student(self):
        """Show add student form"""
        self.clear_content()
        self.current_view = StudentFormView(self.content_frame, self.db_manager)
    
    def show_manage_grades(self):
        """Show grade management view"""
        self.clear_content()
        self.current_view = GradeManagementView(self.content_frame, self.db_manager)
    
    def show_attendance(self):
        """Show attendance view"""
        self.clear_content()
        self.current_view = AttendanceView(self.content_frame, self.db_manager)
    
    def show_search_students(self):
        """Show search view"""
        self.clear_content()
        self.current_view = SearchView(self.content_frame, self.db_manager)
    
    def show_student_list(self):
        """Show student list"""
        self.clear_content()
        self.current_view = StudentListView(self.content_frame, self.db_manager)
    
    def show_statistics(self):
        """Show statistics view"""
        self.clear_content()
        self.current_view = StatisticsView(self.content_frame, self.db_manager)
    
    def show_user_management(self):
        """Show user management view (admin only)"""
        if self.auth_manager.is_admin():
            self.clear_content()
            self.current_view = UserManagementView(self.content_frame, self.db_manager, self.auth_manager)
        else:
            messagebox.showerror("Access Denied", "Admin access required!")
    
    def logout(self):
        """Logout user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.auth_manager.logout()
            # Destroy sidebar
            if self.sidebar:
                self.sidebar.sidebar.destroy()
                self.sidebar = None
            # Show login window
            self.show_login()
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            if self.db_manager:
                self.db_manager.close()
            self.root.destroy()



if __name__ == "__main__":
    app = StudentManagementApp()