# auth_manager.py
import hashlib
import json
import os
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv 

# Load environment variables
load_dotenv()

class AuthManager:
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.current_user = None
        self.users_file = "teachers.json"
        self.init_users_table()
        
    def init_users_table(self):
        try:
            if self.db_manager and hasattr(self.db_manager, 'conn') and self.db_manager.conn:
                query = '''
                    CREATE TABLE IF NOT EXISTS users (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        full_name VARCHAR(100) NOT NULL,
                        email VARCHAR(100),
                        role VARCHAR(20) DEFAULT 'teacher',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP NULL,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                '''
                self.db_manager.execute_query(query)
                
                # Create initial admin from environment variable if no users exist
                self.create_initial_admin_from_env()
                
            else:
                print("Database connection not available, using file-based storage")
                self.create_users_file()
                
        except Error as e:
            print(f"Error creating users table: {e}")
            self.create_users_file()
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.create_users_file()
    
    def create_initial_admin_from_env(self):
        """Create initial admin using credentials from environment variables"""
        try:
            # Check if any users exist
            user_count = self.db_manager.fetch_one("SELECT COUNT(*) as count FROM users")
            
            if user_count and user_count.get('count', 0) == 0:
                # Get admin credentials from environment variables
                admin_username = os.getenv('ADMIN_USERNAME', 'admin')
                admin_password = os.getenv('ADMIN_PASSWORD')
                admin_full_name = os.getenv('ADMIN_FULL_NAME', 'System Administrator')
                admin_email = os.getenv('ADMIN_EMAIL', 'admin@school.com')
                
                if not admin_password:
                    print("WARNING: ADMIN_PASSWORD not set in environment variables!")
                    print("Please set ADMIN_PASSWORD in .env file or environment variables")
                    return False
                
                hashed_password = self.hash_password(admin_password)
                query = """
                    INSERT INTO users (username, password, full_name, email, role, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                result = self.db_manager.execute_query(
                    query, 
                    (admin_username, hashed_password, admin_full_name, admin_email, 'admin', True)
                )
                
                if result:
                    print(f"Initial admin user '{admin_username}' created successfully!")
                return result
        except Exception as e:
            print(f"Error creating initial admin: {e}")
            return False
    
    # Rest of your methods remain the same...
        
    def init_users_table(self):
        try:
            if self.db_manager and hasattr(self.db_manager, 'conn') and self.db_manager.conn:
                query = '''
                    CREATE TABLE IF NOT EXISTS users (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        full_name VARCHAR(100) NOT NULL,
                        email VARCHAR(100),
                        role VARCHAR(20) DEFAULT 'teacher',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP NULL,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                '''
                self.db_manager.execute_query(query)
                
                # Check if admin exists
                admin_check = self.db_manager.fetch_one("SELECT id FROM users WHERE username = 'admin'")
                if not admin_check:
                    hashed_password = self.hash_password("youssef123")
                    query = '''
                        INSERT INTO users (username, password, full_name, email, role)
                        VALUES (%s, %s, %s, %s, %s)
                    '''
                    self.db_manager.execute_query(query, ("admin", hashed_password, "Administrator", "admin@school.com", "admin"))
                    print("Default admin account created: admin / youssef123")
                    
                # Check if teacher exists
                teacher_check = self.db_manager.fetch_one("SELECT id FROM users WHERE username = 'teacher1'")
                if not teacher_check:
                    hashed_password = self.hash_password("teacher123")
                    query = '''
                        INSERT INTO users (username, password, full_name, email, role)
                        VALUES (%s, %s, %s, %s, %s)
                    '''
                    self.db_manager.execute_query(query, ("teacher1", hashed_password, "John Smith", "john.smith@school.com", "teacher"))
                    print("Default teacher account created: teacher1 / teacher123")
            else:
                print("Database connection not available, using file-based storage")
                self.create_users_file()
                
        except Error as e:
            print(f"Error creating users table: {e}")
            self.create_users_file()
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.create_users_file()
    
    def create_users_file(self):
        if not os.path.exists(self.users_file):
            default_users = {
                "admin": {
                    "password": self.hash_password("youssef123"),
                    "full_name": "Administrator",
                    "email": "admin@school.com",
                    "role": "admin",
                    "is_active": True
                },
                "teacher1": {
                    "password": self.hash_password("teacher123"),
                    "full_name": "John Smith",
                    "email": "john.smith@school.com",
                    "role": "teacher",
                    "is_active": True
                }
            }
            with open(self.users_file, 'w') as f:
                json.dump(default_users, f, indent=4)
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        hashed_password = self.hash_password(password)
        
        if self.db_manager and hasattr(self.db_manager, 'conn') and self.db_manager.conn:
            try:
                query = "SELECT id, username, full_name, email, role FROM users WHERE username = %s AND password = %s AND is_active = TRUE"
                user = self.db_manager.fetch_one(query, (username, hashed_password))
                
                if user:
                    self.db_manager.execute_query(
                        "UPDATE users SET last_login = NOW() WHERE username = %s",
                        (username,)
                    )
                    self.current_user = user
                    return True, user
                else:
                    return False, None
            except Error as e:
                print(f"Database auth error: {e}")
                return self.file_authenticate(username, hashed_password)
        
        return self.file_authenticate(username, hashed_password)
    
    def file_authenticate(self, username, hashed_password):
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    users = json.load(f)
                
                if username in users:
                    user_data = users[username]
                    if user_data.get("password") == hashed_password and user_data.get("is_active", True):
                        self.current_user = {
                            "id": 1,
                            "username": username,
                            "full_name": user_data.get("full_name", username),
                            "email": user_data.get("email", ""),
                            "role": user_data.get("role", "teacher")
                        }
                        return True, self.current_user
            return False, None
        except Exception as e:
            print(f"File auth error: {e}")
            return False, None
    
    def change_password(self, username, old_password, new_password):
        hashed_old = self.hash_password(old_password)
        hashed_new = self.hash_password(new_password)
        
        if self.db_manager and hasattr(self.db_manager, 'conn') and self.db_manager.conn:
            user = self.db_manager.fetch_one(
                "SELECT id FROM users WHERE username = %s AND password = %s",
                (username, hashed_old)
            )
            if user:
                return self.db_manager.execute_query(
                    "UPDATE users SET password = %s WHERE username = %s",
                    (hashed_new, username)
                )
            return False
        else:
            try:
                with open(self.users_file, 'r') as f:
                    users = json.load(f)
                
                if username in users and users[username]["password"] == hashed_old:
                    users[username]["password"] = hashed_new
                    with open(self.users_file, 'w') as f:
                        json.dump(users, f, indent=4)
                    return True
            except Exception:
                pass
            return False
    
    def get_users_from_db(self):
        """Get all users from database"""
        if self.db_manager and hasattr(self.db_manager, 'conn') and self.db_manager.conn:
            try:
                users = self.db_manager.fetch_all(
                    "SELECT id, username, full_name, email, role, created_at, last_login, is_active FROM users ORDER BY id"
                )
                return users if users else []
            except Exception as e:
                print(f"Error fetching users: {e}")
                return []
        return []
    
    def add_user_to_db(self, username, password, full_name, email, role):
        """Add a new user to database"""
        if self.db_manager and hasattr(self.db_manager, 'conn') and self.db_manager.conn:
            try:
                # Check if user exists
                existing = self.db_manager.fetch_one("SELECT id FROM users WHERE username = %s", (username,))
                if existing:
                    return False
                
                hashed_password = self.hash_password(password)
                query = """
                    INSERT INTO users (username, password, full_name, email, role)
                    VALUES (%s, %s, %s, %s, %s)
                """
                return self.db_manager.execute_query(query, (username, hashed_password, full_name, email, role))
            except Exception as e:
                print(f"Error adding user: {e}")
                return False
        return False
    
    def logout(self):
        self.current_user = None
    
    def is_authenticated(self):
        return self.current_user is not None
    
    def is_admin(self):
        return self.current_user and self.current_user.get("role") == "admin"
    
    def get_current_user(self):
        return self.current_user