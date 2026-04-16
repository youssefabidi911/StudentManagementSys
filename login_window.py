import customtkinter as ctk
from tkinter import messagebox

class LoginWindow:
    
    def __init__(self, parent, auth_manager, on_login_success):
        self.parent = parent
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success
        self.window = None
        self.password_visible = False
        self.create_login_window()
    
    def create_login_window(self):
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Teacher Login - Student Management System")
        self.window.geometry("1400x800")
        self.window.resizable(True, True)
        
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.focus_force()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (800 // 2)
        self.window.geometry(f"1400x800+{x}+{y}")
        
        main_frame = ctk.CTkFrame(self.window, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="Student Management System",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=30)
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Teacher Login Portal",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        subtitle_label.pack(pady=(0, 30))
        
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(pady=20)
        
        ctk.CTkLabel(form_frame, text="Username", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.username_entry = ctk.CTkEntry(
            form_frame,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            placeholder_text="Enter your username"
        )
        self.username_entry.pack(pady=(0, 20))
        
        ctk.CTkLabel(form_frame, text="Password", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        
        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.pack(pady=(0, 20))
        
        self.password_entry = ctk.CTkEntry(
            password_frame,
            width=260,
            height=40,
            font=ctk.CTkFont(size=14),
            placeholder_text="Enter your password",
            show="•"
        )
        self.password_entry.pack(side="left", padx=(0, 5))
        
        self.toggle_btn = ctk.CTkButton(
            password_frame,
            text="👁",
            width=35,
            height=40,
            command=self.toggle_password_visibility
        )
        self.toggle_btn.pack(side="left")
        
        self.login_btn = ctk.CTkButton(
            form_frame,
            text="Login",
            width=200,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.login
        )
        self.login_btn.pack(pady=20)
        
        self.change_pwd_btn = ctk.CTkButton(
            form_frame,
            text="Change Password",
            width=200,
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color="gray30",
            command=self.show_change_password
        )
        self.change_pwd_btn.pack(pady=10)
        
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(pady=30)
        
        ctk.CTkLabel(
            info_frame,
            text=" ",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).pack()
        
        self.username_entry.bind('<Return>', lambda event: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda event: self.login())
    
    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_entry.configure(show="")
            self.toggle_btn.configure(text="👁‍🗨")
        else:
            self.password_entry.configure(show="•")
            self.toggle_btn.configure(text="👁")
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Login Error", "Please enter both username and password!")
            return
        
        self.login_btn.configure(state="disabled", text="Logging in...")
        
        success, user = self.auth_manager.authenticate(username, password)
        
        self.login_btn.configure(state="normal", text="Login")
        
        if success:
            messagebox.showinfo("Login Success", f"Welcome, {user['full_name']}!\n\nRole: {user['role'].title()}")
            self.window.destroy()
            self.on_login_success()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password!\n\nPlease contact your system administrator.")
            self.password_entry.delete(0, 'end')
            self.username_entry.focus()
    
    def show_change_password(self):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Change Password")
        dialog.geometry("450x550")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (550 // 2)
        dialog.geometry(f"450x550+{x}+{y}")
        
        frame = ctk.CTkFrame(dialog, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text="Change Password",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(frame, text="Username", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(10, 0))
        username_entry = ctk.CTkEntry(frame, width=350, height=40)
        username_entry.pack(pady=5, padx=20)
        
        ctk.CTkLabel(frame, text="Current Password", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(10, 0))
        old_pwd_entry = ctk.CTkEntry(frame, width=350, height=40, show="•")
        old_pwd_entry.pack(pady=5, padx=20)
        
        ctk.CTkLabel(frame, text="New Password (min 6 characters)", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(10, 0))
        new_pwd_entry = ctk.CTkEntry(frame, width=350, height=40, show="•")
        new_pwd_entry.pack(pady=5, padx=20)
        
        ctk.CTkLabel(frame, text="Confirm New Password", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(10, 0))
        confirm_pwd_entry = ctk.CTkEntry(frame, width=350, height=40, show="•")
        confirm_pwd_entry.pack(pady=5, padx=20)
        
        def change_password():
            username = username_entry.get().strip()
            old_pwd = old_pwd_entry.get()
            new_pwd = new_pwd_entry.get()
            confirm_pwd = confirm_pwd_entry.get()
            
            if not username or not old_pwd or not new_pwd:
                messagebox.showerror("Error", "Please fill all fields!")
                return
            
            if new_pwd != confirm_pwd:
                messagebox.showerror("Error", "New passwords do not match!")
                return
            
            if len(new_pwd) < 6:
                messagebox.showerror("Error", "New password must be at least 6 characters!")
                return
            
            if self.auth_manager.change_password(username, old_pwd, new_pwd):
                messagebox.showinfo("Success", "Password changed successfully!\nPlease login with your new password.")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to change password!\nPlease check your username and current password.")
        
        ctk.CTkButton(
            frame,
            text="Change Password",
            command=change_password,
            height=40,
            width=200
        ).pack(pady=20)
        
        ctk.CTkButton(
            frame,
            text="Cancel",
            command=dialog.destroy,
            fg_color="gray",
            hover_color="darkgray",
            height=35,
            width=200
        ).pack()
