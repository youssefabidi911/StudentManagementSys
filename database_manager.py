import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    
    def __init__(self):
        self.mysql_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'student_management_db')
        }
        self.conn = None
        self.cursor = None
        self.is_connected = False
        self.init_database()
    
    def init_database(self):
        try:
            connection = mysql.connector.connect(
                host=self.mysql_config['host'],
                user=self.mysql_config['user'],
                password=self.mysql_config['password']
            )
            
            cursor = connection.cursor()
            
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.mysql_config['database']}")
            cursor.execute(f"USE {self.mysql_config['database']}")
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    student_id VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    grade VARCHAR(20) NOT NULL,
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    address TEXT,
                    enrollment_date DATE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS grades (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    student_id VARCHAR(50) NOT NULL,
                    subject VARCHAR(100) NOT NULL,
                    grade DECIMAL(5,2) NOT NULL,
                    coefficient INT DEFAULT 1 NOT NULL,
                    semester VARCHAR(20) NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                    INDEX idx_student_id (student_id)
                )
            ''')
            
            cursor.execute("SHOW COLUMNS FROM grades LIKE 'coefficient'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE grades ADD COLUMN coefficient INT DEFAULT 1 NOT NULL")
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    student_id VARCHAR(50) NOT NULL,
                    date DATE NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                    UNIQUE KEY unique_attendance (student_id, date),
                    INDEX idx_date (date)
                )
            ''')
            
            cursor.execute('''
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
            ''')
            
            connection.commit()
            cursor.close()
            connection.close()
            
            self.conn = mysql.connector.connect(**self.mysql_config)
            self.cursor = self.conn.cursor(dictionary=True)
            self.is_connected = True
            
            self.create_default_users()
            
            print("MySQL Database connected successfully!")
            
        except Error as e:
            print(f"Database Error: {e}")
            messagebox.showwarning("Database Warning", 
                f"Could not connect to MySQL: {e}\n\n"
                "The application will run in offline mode with file-based storage.\n"
                "Please check your .env file and make sure MySQL is running.")
            self.is_connected = False
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.is_connected = False
    
    def create_default_users(self):
        try:
            def hash_password(password):
                return hashlib.sha256(password.encode()).hexdigest()
            
            admin_username = os.getenv('ADMIN_USERNAME', 'admin')
            admin_password = os.getenv('ADMIN_PASSWORD')
            admin_full_name = os.getenv('ADMIN_FULL_NAME', 'Administrator')
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@school.com')
            
            teacher_username = os.getenv('TEACHER_USERNAME', 'teacher1')
            teacher_password = os.getenv('TEACHER_PASSWORD')
            teacher_full_name = os.getenv('TEACHER_FULL_NAME', 'John Smith')
            teacher_email = os.getenv('TEACHER_EMAIL', 'john.smith@school.com')
            
            if admin_password:
                admin_check = self.fetch_one("SELECT id FROM users WHERE username = %s", (admin_username,))
                if not admin_check:
                    query = "INSERT INTO users (username, password, full_name, email, role) VALUES (%s, %s, %s, %s, %s)"
                    self.execute_query(query, (admin_username, hash_password(admin_password), admin_full_name, admin_email, "admin"))
                    print(f"Default admin account created: {admin_username}")
            
            if teacher_password:
                teacher_check = self.fetch_one("SELECT id FROM users WHERE username = %s", (teacher_username,))
                if not teacher_check:
                    query = "INSERT INTO users (username, password, full_name, email, role) VALUES (%s, %s, %s, %s, %s)"
                    self.execute_query(query, (teacher_username, hash_password(teacher_password), teacher_full_name, teacher_email, "teacher"))
                    print(f"Default teacher account created: {teacher_username}")
                
        except Exception as e:
            print(f"Error creating default users: {e}")
    
    def execute_query(self, query, params=None):
        if not self.is_connected:
            return False
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except Error as e:
            print(f"Database error: {e}")
            self.conn.rollback()
            return False
    
    def fetch_one(self, query, params=None):
        if not self.is_connected:
            return None
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Error as e:
            print(f"Database error: {e}")
            return None
    
    def fetch_all(self, query, params=None):
        if not self.is_connected:
            return []
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Database error: {e}")
            return []
    
    def add_student(self, student_data):
        query = '''
            INSERT INTO students (student_id, name, grade, email, phone, address, enrollment_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        return self.execute_query(query, student_data)
    
    def add_grade(self, grade_data):
        query = '''
            INSERT INTO grades (student_id, subject, grade, coefficient, semester)
            VALUES (%s, %s, %s, %s, %s)
        '''
        return self.execute_query(query, grade_data)
    
    def save_attendance(self, attendance_data):
        query = '''
            INSERT INTO attendance (student_id, date, status)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE status = %s
        '''
        return self.execute_query(query, attendance_data)
    
    def get_students(self):
        return self.fetch_all("SELECT student_id, name FROM students ORDER BY name")
    
    def get_student_grades(self, student_id):
        query = '''
            SELECT subject, grade, coefficient, semester FROM grades 
            WHERE student_id = %s 
            ORDER BY semester, subject
        '''
        return self.fetch_all(query, (student_id,))
    
    def get_weighted_average(self, student_id, semester=None):
        if semester:
            query = '''
                SELECT SUM(grade * coefficient) as total_weighted, SUM(coefficient) as total_coefficient
                FROM grades 
                WHERE student_id = %s AND semester = %s
            '''
            result = self.fetch_one(query, (student_id, semester))
        else:
            query = '''
                SELECT SUM(grade * coefficient) as total_weighted, SUM(coefficient) as total_coefficient
                FROM grades 
                WHERE student_id = %s
            '''
            result = self.fetch_one(query, (student_id,))
        
        if result and result.get('total_coefficient') and result['total_coefficient'] > 0:
            return round(result['total_weighted'] / result['total_coefficient'], 2)
        return 0
    
    def get_semester_averages(self, student_id):
        s1_avg = self.get_weighted_average(student_id, "S1")
        s2_avg = self.get_weighted_average(student_id, "S2")
        
        if s1_avg > 0 and s2_avg > 0:
            overall = (s1_avg + s2_avg) / 2
        elif s1_avg > 0:
            overall = s1_avg
        elif s2_avg > 0:
            overall = s2_avg
        else:
            overall = 0
        
        return {
            'semester1': s1_avg,
            'semester2': s2_avg,
            'overall': round(overall, 2)
        }
    
    def get_dashboard_stats(self):
        stats = {}
        
        result = self.fetch_one("SELECT COUNT(*) as total FROM students")
        stats['total_students'] = result['total'] if result else 0
        
        result = self.fetch_one("""
            SELECT ROUND(SUM(grade * coefficient) / SUM(coefficient), 2) as weighted_avg
            FROM grades
            WHERE coefficient > 0
        """)
        stats['avg_grade'] = result['weighted_avg'] if result and result.get('weighted_avg') else 0
        
        result = self.fetch_one("""
            SELECT COUNT(*) as present FROM attendance 
            WHERE status = 'Present' AND date = CURDATE()
        """)
        stats['today_present'] = result['present'] if result else 0
        
        result = self.fetch_one("SELECT COUNT(DISTINCT subject) as total FROM grades")
        stats['total_subjects'] = result['total'] if result else 0
        
        return stats
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.is_connected = False
