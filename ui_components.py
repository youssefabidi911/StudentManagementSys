# ui_components.py
import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime

class Sidebar:
    
    def __init__(self, parent, app, auth_manager=None):
        self.parent = parent
        self.app = app
        self.auth_manager = auth_manager
        self.create_sidebar()
    
    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.parent, width=320, corner_radius=20)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="Student Management\nSystem", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=30)
        
        if self.auth_manager and self.auth_manager.is_authenticated():
            user = self.auth_manager.get_current_user()
            user_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            user_frame.pack(pady=(0, 20), padx=10, fill="x")
            
            ctk.CTkLabel(
                user_frame,
                text=f"👤 {user['full_name']}",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack()
            
            ctk.CTkLabel(
                user_frame,
                text=f"Role: {user['role'].title()}",
                font=ctk.CTkFont(size=11),
                text_color="gray70"
            ).pack()
        
        nav_buttons = [
            ("📊 Dashboard", self.app.show_dashboard),
            ("👨‍🎓 Add Student", self.app.show_add_student),
            ("📚 Manage Grades", self.app.show_manage_grades),
            ("📅 Attendance", self.app.show_attendance),
            ("🔍 Search Students", self.app.show_search_students),
            ("📋 Student List", self.app.show_student_list),
            ("📈 Statistics", self.app.show_statistics)
        ]
        
        if self.auth_manager and self.auth_manager.is_admin():
            nav_buttons.append(("👥 User Management", self.app.show_user_management))
        
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                self.sidebar, 
                text=text, 
                command=command,
                height=45,
                font=ctk.CTkFont(size=14)
            )
            btn.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkButton(
            self.sidebar, 
            text="🚪 Logout", 
            command=self.app.logout,
            height=45,
            fg_color="orange",
            hover_color="darkorange",
            font=ctk.CTkFont(size=14)
        ).pack(pady=5, padx=10, fill="x", side="bottom")
        
        ctk.CTkButton(
            self.sidebar, 
            text="❌ Exit", 
            command=self.app.on_closing,
            height=45,
            fg_color="red",
            hover_color="darkred",
            font=ctk.CTkFont(size=14)
        ).pack(pady=5, padx=10, fill="x", side="bottom")


class DashboardView:
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.create_dashboard()
    
    def create_dashboard(self):
        title = ctk.CTkLabel(
            self.parent, 
            text="Dashboard", 
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(pady=20)
        
        stats = self.db.get_dashboard_stats()
        
        stats_frame = ctk.CTkFrame(self.parent)
        stats_frame.pack(pady=20, padx=20, fill="x")
        
        stats_data = [
            ("Total Students", stats['total_students'], "👨‍🎓"),
            ("Weighted Avg", f"{stats['avg_grade']}%", "📊"),
            ("Present Today", stats['today_present'], "✅"),
            ("Subjects", stats.get('total_subjects', 0), "📚")
        ]
        
        for i, (label, value, icon) in enumerate(stats_data):
            card = ctk.CTkFrame(stats_frame)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=40)).pack(pady=10)
            ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=30, weight="bold")).pack()
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=14)).pack(pady=5)
        
        recent_label = ctk.CTkLabel(
            self.parent, 
            text="Recent Students", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        recent_label.pack(pady=20)
        
        recent_frame = ctk.CTkFrame(self.parent)
        recent_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        columns = ("ID", "Name", "Grade", "Email")
        tree = ttk.Treeview(recent_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        recent_students = self.db.fetch_all("""
            SELECT student_id, name, grade, email 
            FROM students 
            ORDER BY id ASC
            LIMIT 5
        """)
        
        for row in recent_students:
            tree.insert("", "end", values=(row['student_id'], row['name'], row['grade'], row['email']))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)


class StudentFormView:
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.create_form()
    
    def create_form(self):
        title = ctk.CTkLabel(
            self.parent, 
            text="Add New Student", 
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(pady=20)
        
        # Form frame
        form_frame = ctk.CTkFrame(self.parent)
        form_frame.pack(pady=20, padx=50, fill="both", expand=True)
        
        fields = [
            ("Student ID", "student_id"),
            ("Full Name", "name"),
            ("Grade", "grade"),
            ("Email", "email"),
            ("Phone", "phone"),
            ("Address", "address")
        ]
        
        self.entries = {}
        
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(form_frame, text=label + ":", font=ctk.CTkFont(size=14)).grid(
                row=i, column=0, padx=10, pady=10, sticky="e"
            )
            entry = ctk.CTkEntry(form_frame, width=300)
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="w")
            self.entries[key] = entry
        
        submit_btn = ctk.CTkButton(
            form_frame, 
            text="Add Student", 
            command=self.submit_student, 
            height=40
        )
        submit_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def submit_student(self):
        student_data = {key: entry.get() for key, entry in self.entries.items()}
        
        if not student_data['student_id'] or not student_data['name']:
            messagebox.showerror("Error", "Student ID and Name are required!")
            return
        
        student_data['enrollment_date'] = datetime.now().strftime("%Y-%m-%d")
        
        try:
            if self.db.add_student(tuple(student_data.values())):
                messagebox.showinfo("Success", "Student added successfully!")
                for entry in self.entries.values():
                    entry.delete(0, 'end')
        except Exception as e:
            if "Duplicate entry" in str(e):
                messagebox.showerror("Error", "Student ID already exists!")
            else:
                messagebox.showerror("Error", f"Database error: {e}")
                

class GradeManagementView:
    
    SUBJECTS = [
        "Rechereche Operationnelle", "Statistique Exploratoire",
        "Algorithmique avancée & Langage C avancée", "Programmation python avancée",
        "Développement Web 2 - PHP fundamentals", "Programmation Orienté Objet - Java 1",
        "Projet Semestriel - PS1", "Bases de Données avancées",
        "Systèmes d'Informations et Eco-Conception", "Système d'Exploitation Avancée - LPI 102",
        "Préparation à la certification réseaux avancés - CCNA 2",
        "Français sur objectif spécifique - FOS 2 / DELF", "English for Specific Purposes - ESP 2",
        "Projet Socio-Culturel - PSC2"
    ]
    
    SUBJECT_COEFFICIENTS = {
        "Rechereche Operationnelle": 2,
        "Statistique Exploratoire": 2,
        "Algorithmique avancée & Langage C avancée": 3,
        "Programmation python avancée": 2,
        "Développement Web 2 - PHP fundamentals": 2,
        "Programmation Orienté Objet - Java 1": 2,
        "Projet Semestriel - PS1": 3,
        "Bases de Données avancées": 2,
        "Systèmes d'Informations et Eco-Conception": 2,
        "Système d'Exploitation Avancée - LPI 102": 2,
        "Préparation à la certification réseaux avancés - CCNA 2": 2,
        "Français sur objectif spécifique - FOS 2 / DELF": 2,
        "English for Specific Purposes - ESP 2": 2,
        "Projet Socio-Culturel - PSC2": 2
    }
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.create_grade_management()
    
    def create_grade_management(self):
        """Create grade management interface"""
        # Create scrollable main container
        main_container = ctk.CTkScrollableFrame(self.parent)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(
            main_container, 
            text="Manage Grades with Coefficients", 
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(pady=20)
        
        select_frame = ctk.CTkFrame(main_container)
        select_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(select_frame, text="Select Student:", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
        
        students = self.db.get_students()
        student_list = [f"{s['student_id']} - {s['name']}" for s in students]
        
        self.student_combo = ctk.CTkComboBox(select_frame, values=student_list, width=300)
        self.student_combo.pack(side="left", padx=10)
        
        grade_frame = ctk.CTkFrame(main_container)
        grade_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(grade_frame, text="Subject:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.subject_combo = ctk.CTkComboBox(grade_frame, values=self.SUBJECTS, width=250)
        self.subject_combo.grid(row=0, column=1, padx=10, pady=10)
        self.subject_combo.bind(' ', self.update_coefficient_display)
        
        ctk.CTkLabel(grade_frame, text="Coefficient:", font=ctk.CTkFont(size=14)).grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.coefficient_label = ctk.CTkLabel(grade_frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.coefficient_label.grid(row=0, column=3, padx=10, pady=10)
        
        ctk.CTkLabel(grade_frame, text="Grade:", font=ctk.CTkFont(size=14)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.grade_entry = ctk.CTkEntry(grade_frame, width=100)
        self.grade_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(grade_frame, text="Semester:", font=ctk.CTkFont(size=14)).grid(row=1, column=2, padx=10, pady=10, sticky="e")
        self.semester_combo = ctk.CTkComboBox(grade_frame, values=["S1", "S2"], width=100)
        self.semester_combo.grid(row=1, column=3, padx=10, pady=10)
        
        add_btn = ctk.CTkButton(grade_frame, text="Add Grade", command=self.add_grade, height=35)
        add_btn.grid(row=1, column=4, padx=20, pady=10)
        
        info_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        info_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(
            info_frame, 
            text="ℹ️ Note: Coefficients are automatically assigned based on subject importance.",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        ).pack()
        
        self.grades_frame = ctk.CTkFrame(main_container)
        self.grades_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.avg_frame = ctk.CTkFrame(main_container)
        self.avg_frame.pack(pady=10, padx=20, fill="x")
        
        self.student_combo.configure(command=lambda x: self.display_grades())
        self.display_grades()
    
    def update_coefficient_display(self, event=None):
        subject = self.subject_combo.get()
        if subject in self.SUBJECT_COEFFICIENTS:
            coeff = self.SUBJECT_COEFFICIENTS[subject]
            self.coefficient_label.configure(text=f"Coefficient: {coeff}", text_color="green")
        else:
            self.coefficient_label.configure(text="Coefficient: 1", text_color="yellow")
    
    def add_grade(self):
        if not self.student_combo.get():
            messagebox.showerror("Error", "Please select a student!")
            return
        
        student_id = self.student_combo.get().split(" - ")[0]
        
        if not self.subject_combo.get() or not self.grade_entry.get():
            messagebox.showerror("Error", "Please enter subject and grade!")
            return
        
        try:
            grade = float(self.grade_entry.get())
            if grade < 0 or grade > 100:
                messagebox.showerror("Error", "Grade must be between 0 and 100!")
                return
            
            subject = self.subject_combo.get()
            coefficient = self.SUBJECT_COEFFICIENTS.get(subject, 1)
            
            if self.db.add_grade((student_id, subject, grade, coefficient, self.semester_combo.get())):
                messagebox.showinfo("Success", f"Grade added successfully! (Coefficient: {coefficient})")
                self.subject_combo.set('')
                self.grade_entry.delete(0, 'end')
                self.coefficient_label.configure(text="")
                self.display_grades()
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid grade!")
    
    def display_grades(self):
        for widget in self.grades_frame.winfo_children():
            widget.destroy()
        
        for widget in self.avg_frame.winfo_children():
            widget.destroy()
        
        if not self.student_combo.get():
            return
        
        student_id = self.student_combo.get().split(" - ")[0]
        grades = self.db.get_student_grades(student_id)
        
        if grades:
            columns = ("Subject", "Grade", "Coefficient", "Weighted Score", "Semester")
            tree = ttk.Treeview(self.grades_frame, columns=columns, show="headings", height=10)
            
            column_widths = {"Subject": 300, "Grade": 100, "Coefficient": 100, "Weighted Score": 120, "Semester": 80}
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=column_widths.get(col, 150))
            
            total_weighted = 0
            total_coefficient = 0
            
            for grade in grades:
                weighted = grade['grade'] * grade['coefficient']
                total_weighted += weighted
                total_coefficient += grade['coefficient']
                
                tree.insert("", "end", values=(
                    grade['subject'], 
                    f"{grade['grade']:.2f}", 
                    grade['coefficient'],
                    f"{weighted:.2f}",
                    grade['semester']
                ))
            
            tree.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(self.grades_frame, orient="vertical", command=tree.yview)
            scrollbar.pack(side="right", fill="y")
            tree.configure(yscrollcommand=scrollbar.set)
            
            if total_coefficient > 0:
                weighted_avg = total_weighted / total_coefficient
                
                semester_averages = self.db.get_semester_averages(student_id)
                
                avg_display_frame = ctk.CTkFrame(self.avg_frame)
                avg_display_frame.pack(fill="x", pady=10)
                
                # Weighted average card
                card1 = ctk.CTkFrame(avg_display_frame, corner_radius=10)
                card1.pack(side="left", padx=10, pady=10, fill="both", expand=True)
                
                ctk.CTkLabel(card1, text="📊 Weighted Average", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
                avg_color = "green" if weighted_avg >= 10 else "orange" if weighted_avg >= 7 else "red"
                ctk.CTkLabel(
                    card1, 
                    text=f"{weighted_avg:.2f}", 
                    font=ctk.CTkFont(size=28, weight="bold"),
                    text_color=avg_color
                ).pack(pady=5)
                ctk.CTkLabel(card1, text=f"Total Coefficient: {total_coefficient}", font=ctk.CTkFont(size=12)).pack()
                
                # Semester averages card
                card2 = ctk.CTkFrame(avg_display_frame, corner_radius=10)
                card2.pack(side="left", padx=10, pady=10, fill="both", expand=True)
                
                ctk.CTkLabel(card2, text="📚 Semester Averages", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
                
                sem_frame = ctk.CTkFrame(card2, fg_color="transparent")
                sem_frame.pack(pady=5)
                
                s1_color = "green" if semester_averages['semester1'] >= 10 else "orange" if semester_averages['semester1'] >= 7 else "red"
                s2_color = "green" if semester_averages['semester2'] >= 10 else "orange" if semester_averages['semester2'] >= 7 else "red"
                
                ctk.CTkLabel(
                    sem_frame, 
                    text="S1: ", 
                    font=ctk.CTkFont(size=12)
                ).pack(side="left")
                ctk.CTkLabel(
                    sem_frame, 
                    text=f"{semester_averages['semester1']:.2f}" if semester_averages['semester1'] > 0 else "N/A", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=s1_color
                ).pack(side="left", padx=(0, 10))
                
                ctk.CTkLabel(
                    sem_frame, 
                    text="S2: ", 
                    font=ctk.CTkFont(size=12)
                ).pack(side="left")
                ctk.CTkLabel(
                    sem_frame, 
                    text=f"{semester_averages['semester2']:.2f}" if semester_averages['semester2'] > 0 else "N/A", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=s2_color
                ).pack(side="left")
                
                # Overall average
                card3 = ctk.CTkFrame(avg_display_frame, corner_radius=10)
                card3.pack(side="left", padx=10, pady=10, fill="both", expand=True)
                
                ctk.CTkLabel(card3, text="🎯 Overall Average", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
                overall_color = "green" if semester_averages['overall'] >= 10 else "orange" if semester_averages['overall'] >= 7 else "red"
                ctk.CTkLabel(
                    card3, 
                    text=f"{semester_averages['overall']:.2f}", 
                    font=ctk.CTkFont(size=28, weight="bold"),
                    text_color=overall_color
                ).pack(pady=5)
                
                # Grade status
                status = "✅ PASSING" if weighted_avg >= 10 else "❌ FAILING"
                status_color = "green" if weighted_avg >= 10 else "red"
                ctk.CTkLabel(
                    self.avg_frame, 
                    text=status, 
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=status_color
                ).pack(pady=5)
                
        else:
            ctk.CTkLabel(self.grades_frame, text="No grades found for this student", font=ctk.CTkFont(size=14)).pack(pady=20)

# Continue ui_components.py - AttendanceView, SearchView, StudentListView, StatisticsView, UserManagementView

class AttendanceView:
    """Attendance management component"""
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.create_attendance_view()
    
    def create_attendance_view(self):
        """Create attendance management view"""
        title = ctk.CTkLabel(
            self.parent, 
            text="Attendance Management", 
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(pady=20)
        
        # Date selection
        date_frame = ctk.CTkFrame(self.parent)
        date_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(date_frame, text="Date:", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
        self.date_entry = ctk.CTkEntry(date_frame, width=150)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(side="left", padx=10)
        
        # Get all students
        students = self.db.get_students()
        
        if not students:
            ctk.CTkLabel(self.parent, text="No students found. Please add students first.", 
                        font=ctk.CTkFont(size=16)).pack(pady=50)
            return
        
        # Attendance frame with scrollbar
        attendance_container = ctk.CTkScrollableFrame(self.parent, height=400)
        attendance_container.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.attendance_vars = {}
        
        for student in students:
            frame = ctk.CTkFrame(attendance_container)
            frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(frame, text=f"{student['student_id']} - {student['name']}", 
                        width=250, anchor="w").pack(side="left", padx=10)
            
            var = ctk.StringVar(value="Present")
            self.attendance_vars[student['student_id']] = var
            
            present_radio = ctk.CTkRadioButton(frame, text="Present", variable=var, value="Present")
            present_radio.pack(side="left", padx=5)
            
            absent_radio = ctk.CTkRadioButton(frame, text="Absent", variable=var, value="Absent")
            absent_radio.pack(side="left", padx=5)
            
            late_radio = ctk.CTkRadioButton(frame, text="Late", variable=var, value="Late")
            late_radio.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(self.parent, text="Save Attendance", command=self.save_attendance, height=40)
        save_btn.pack(pady=20)
    
    def save_attendance(self):
        """Save attendance records"""
        date = self.date_entry.get()
        
        try:
            for student_id, var in self.attendance_vars.items():
                self.db.save_attendance((student_id, date, var.get(), var.get()))
            
            messagebox.showinfo("Success", "Attendance saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save attendance: {e}")


class SearchView:
    """Student search component"""
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.create_search_view()
    
    def create_search_view(self):
        """Create search interface"""
        title = ctk.CTkLabel(
            self.parent, 
            text="Search Students", 
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(pady=20)
        
        # Search frame
        search_frame = ctk.CTkFrame(self.parent)
        search_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(search_frame, text="Search:", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
        self.search_entry = ctk.CTkEntry(search_frame, width=300)
        self.search_entry.pack(side="left", padx=10)
        
        self.search_by = ctk.CTkComboBox(search_frame, values=["Name", "Student ID", "Grade"], width=120)
        self.search_by.pack(side="left", padx=10)
        
        search_btn = ctk.CTkButton(search_frame, text="Search", command=self.perform_search)
        search_btn.pack(side="left", padx=10)
        
        # Results frame
        self.results_frame = ctk.CTkFrame(self.parent)
        self.results_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda event: self.perform_search())
    
    def perform_search(self):
        """Perform student search"""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        search_term = self.search_entry.get()
        search_field = self.search_by.get()
        
        if not search_term:
            messagebox.showwarning("Warning", "Please enter search term!")
            return
        
        try:
            if search_field == "Name":
                query = "SELECT student_id, name, grade, email, phone FROM students WHERE name LIKE %s"
                results = self.db.fetch_all(query, (f'%{search_term}%',))
            elif search_field == "Student ID":
                query = "SELECT student_id, name, grade, email, phone FROM students WHERE student_id LIKE %s"
                results = self.db.fetch_all(query, (f'%{search_term}%',))
            else:  # Grade
                query = "SELECT student_id, name, grade, email, phone FROM students WHERE grade = %s"
                results = self.db.fetch_all(query, (search_term,))
            
            if results:
                columns = ("Student ID", "Name", "Grade", "Email", "Phone")
                tree = ttk.Treeview(self.results_frame, columns=columns, show="headings", height=15)
                
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=150)
                
                for result in results:
                    tree.insert("", "end", values=(result['student_id'], result['name'], 
                                                  result['grade'], result['email'], result['phone']))
                
                tree.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Scrollbar
                scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=tree.yview)
                scrollbar.pack(side="right", fill="y")
                tree.configure(yscrollcommand=scrollbar.set)
                
                # Result count label
                count_label = ctk.CTkLabel(self.results_frame, text=f"Found {len(results)} student(s)", 
                                          font=ctk.CTkFont(size=12))
                count_label.pack(pady=5)
            else:
                ctk.CTkLabel(self.results_frame, text="No students found", font=ctk.CTkFont(size=16)).pack(pady=50)
                
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")


class StudentListView:
    """Student list component"""
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.create_student_list()
    
    def create_student_list(self):
        """Create student list view"""
        title = ctk.CTkLabel(
            self.parent, 
            text="Student List", 
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(pady=20)
        
        # List frame
        list_frame = ctk.CTkFrame(self.parent)
        list_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        columns = ("Student ID", "Name", "Grade", "Email", "Phone", "Enrollment Date")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        students = self.db.fetch_all("SELECT student_id, name, grade, email, phone, enrollment_date FROM students ORDER BY name")
        
        for row in students:
            tree.insert("", "end", values=(row['student_id'], row['name'], row['grade'], 
                                          row['email'], row['phone'], row['enrollment_date']))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        scrollbar_y.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar_y.set)
        
        scrollbar_x = ttk.Scrollbar(list_frame, orient="horizontal", command=tree.xview)
        scrollbar_x.pack(side="bottom", fill="x")
        tree.configure(xscrollcommand=scrollbar_x.set)
        
        # Count label
        count = self.db.fetch_one("SELECT COUNT(*) as count FROM students")['count']
        count_label = ctk.CTkLabel(list_frame, text=f"Total Students: {count}", font=ctk.CTkFont(size=12))
        count_label.pack(pady=5)


class StatisticsView:
    """Statistics and reports component"""
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.create_statistics()
    
    def create_statistics(self):
        """Create statistics view"""
        title = ctk.CTkLabel(
            self.parent, 
            text="Statistics & Reports", 
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(pady=20)
        
        # Create scrollable frame for statistics
        stats_container = ctk.CTkScrollableFrame(self.parent)
        stats_container.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Grade distribution
        self.create_grade_distribution(stats_container)
        
        # Attendance statistics
        self.create_attendance_stats(stats_container)
        
        # Top students
        self.create_top_students(stats_container)
    
    def create_grade_distribution(self, parent):
        """Create grade distribution section with weighted averages"""
        grade_frame = ctk.CTkFrame(parent)
        grade_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(grade_frame, text="📊 Grade Distribution (Weighted)", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        
        # Get weighted grade distribution
        distribution = self.db.fetch_all('''
            SELECT 
                CASE 
                    WHEN grade >= 19 THEN 'Excellent'
                    WHEN grade >= 16 THEN 'Very Good'
                    WHEN grade >= 12 THEN 'Good'
                    WHEN grade >= 10 THEN 'Passed'
                    ELSE 'Failed'
                END as grade_level,
                SUM(coefficient) as total_coefficient,
                COUNT(*) as grade_count,
                ROUND(AVG(grade), 2) as avg_grade
            FROM grades
            GROUP BY grade_level
            ORDER BY MIN(grade) DESC
        ''')
        
        if distribution:
            total_coeff = sum(g['total_coefficient'] for g in distribution if g['total_coefficient'])
            if total_coeff > 0:
                for grade_data in distribution:
                    frame = ctk.CTkFrame(grade_frame)
                    frame.pack(fill="x", pady=5, padx=20)
                    
                    # Grade level and average
                    info_text = f"{grade_data['grade_level']} (Avg: {grade_data['avg_grade']:.1f})"
                    ctk.CTkLabel(frame, text=info_text, width=200, anchor="w").pack(side="left", padx=10)
                    
                    # Progress bar (using coefficient weight instead of count)
                    percentage = (grade_data['total_coefficient'] / total_coeff) * 100
                    progress = ctk.CTkProgressBar(frame, width=300)
                    progress.pack(side="left", padx=10)
                    progress.set(percentage / 100)
                    
                    ctk.CTkLabel(
                        frame, 
                        text=f"Coef: {grade_data['total_coefficient']} ({percentage:.1f}%)", 
                        width=150
                    ).pack(side="left", padx=10)
            else:
                ctk.CTkLabel(grade_frame, text="No coefficient data available", font=ctk.CTkFont(size=14)).pack(pady=20)
        else:
            ctk.CTkLabel(grade_frame, text="No grade data available", font=ctk.CTkFont(size=14)).pack(pady=20)
    
    def create_attendance_stats(self, parent):
        """Create attendance statistics section"""
        att_frame = ctk.CTkFrame(parent)
        att_frame.pack(pady=20, padx=10, fill="x")
        
        ctk.CTkLabel(att_frame, text="📅 Attendance Overview", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        
        # Check if there are any attendance records first
        total_count = self.db.fetch_one("SELECT COUNT(*) as total FROM attendance")
        
        if total_count and total_count['total'] > 0:
            attendance_stats = self.db.fetch_all('''
                SELECT 
                    status, 
                    COUNT(*) as count,
                    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM attendance), 2) as percentage
                FROM attendance 
                GROUP BY status
                ORDER BY 
                    CASE status
                        WHEN 'Present' THEN 1
                        WHEN 'Late' THEN 2
                        WHEN 'Absent' THEN 3
                        ELSE 4
                    END
            ''')
            
            if attendance_stats:
                for att_data in attendance_stats:
                    frame = ctk.CTkFrame(att_frame)
                    frame.pack(fill="x", pady=5, padx=20)
                    
                    emoji = "✅" if att_data['status'] == 'Present' else "⏰" if att_data['status'] == 'Late' else "❌"
                    ctk.CTkLabel(frame, text=f"{emoji} {att_data['status']}", width=150, anchor="w").pack(side="left", padx=10)
                    
                    progress = ctk.CTkProgressBar(frame, width=300)
                    progress.pack(side="left", padx=10)
                    progress.set(att_data['percentage'] / 100)
                    
                    if att_data['status'] == 'Present':
                        progress.configure(progress_color="green")
                    elif att_data['status'] == 'Late':
                        progress.configure(progress_color="orange")
                    else:
                        progress.configure(progress_color="red")
                    
                    ctk.CTkLabel(frame, text=f"{att_data['count']} records ({att_data['percentage']}%)", 
                               width=150).pack(side="left", padx=10)
        else:
            ctk.CTkLabel(att_frame, text="📭 No attendance records found", font=ctk.CTkFont(size=14)).pack(pady=20)
    
    def create_top_students(self, parent):
        """Create top students section using weighted averages"""
        top_frame = ctk.CTkFrame(parent)
        top_frame.pack(pady=20, padx=10, fill="x")
        
        ctk.CTkLabel(top_frame, text="🏆 Top Performing Students (Weighted by Coefficient)", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        
        # Calculate weighted average for each student
        top_students = self.db.fetch_all('''
            SELECT 
                s.name, 
                s.student_id,
                ROUND(SUM(g.grade * g.coefficient) / SUM(g.coefficient), 2) as weighted_avg
            FROM students s
            JOIN grades g ON s.student_id = g.student_id
            GROUP BY s.student_id, s.name
            HAVING SUM(g.coefficient) > 0
            ORDER BY weighted_avg DESC
            LIMIT 5
        ''')
        
        if top_students:
            for i, student in enumerate(top_students, 1):
                frame = ctk.CTkFrame(top_frame)
                frame.pack(fill="x", pady=5, padx=20)
                
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                
                ctk.CTkLabel(frame, text=f"{medal} {student['name']} ({student['student_id']})", 
                           width=350, anchor="w").pack(side="left", padx=10)
                
                avg = student['weighted_avg']
                color = "green" if avg >= 10 else "orange" if avg >= 7 else "red"
                
                ctk.CTkLabel(frame, text=f"Weighted Average: {avg}%", 
                           font=ctk.CTkFont(weight="bold"),
                           text_color=color).pack(side="left", padx=10)
                
                status = "✅" if avg >= 10 else "❌"
                ctk.CTkLabel(frame, text=status, font=ctk.CTkFont(size=16)).pack(side="left", padx=10)
        else:
            ctk.CTkLabel(top_frame, text="No grade data available", font=ctk.CTkFont(size=14)).pack(pady=20)


class UserManagementView:
    """User management component (admin only)"""
    
    def __init__(self, parent, db_manager, auth_manager):
        self.parent = parent
        self.db = db_manager
        self.auth_manager = auth_manager
        self.create_user_management()
    
    def create_user_management(self):
        """Create user management interface"""
        title = ctk.CTkLabel(
            self.parent, 
            text="👥 User Management", 
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(pady=20)
        
        # Add new user section
        add_frame = ctk.CTkFrame(self.parent)
        add_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(add_frame, text="Add New User", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        
        # Form fields
        fields_frame = ctk.CTkFrame(add_frame)
        fields_frame.pack(pady=10, padx=20)
        
        # Row 1
        row1 = ctk.CTkFrame(fields_frame)
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Username:", width=120).pack(side="left", padx=5)
        self.username_entry = ctk.CTkEntry(row1, width=200)
        self.username_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(row1, text="Full Name:", width=120).pack(side="left", padx=5)
        self.fullname_entry = ctk.CTkEntry(row1, width=200)
        self.fullname_entry.pack(side="left", padx=5)
        
        # Row 2
        row2 = ctk.CTkFrame(fields_frame)
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Email:", width=120).pack(side="left", padx=5)
        self.email_entry = ctk.CTkEntry(row2, width=200)
        self.email_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(row2, text="Password:", width=120).pack(side="left", padx=5)
        self.password_entry = ctk.CTkEntry(row2, width=200, show="•")
        self.password_entry.pack(side="left", padx=5)
        
        # Row 3
        row3 = ctk.CTkFrame(fields_frame)
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Role:", width=120).pack(side="left", padx=5)
        self.role_combo = ctk.CTkComboBox(row3, values=["teacher", "admin"], width=200)
        self.role_combo.pack(side="left", padx=5)
        
        add_btn = ctk.CTkButton(add_frame, text="Add User", command=self.add_user, width=200)
        add_btn.pack(pady=10)
        
        # User list section
        list_frame = ctk.CTkFrame(self.parent)
        list_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(list_frame, text="Existing Users", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        
        # Try to get users from database
        users = self.auth_manager.get_users_from_db()
        
        if users:
            columns = ("Username", "Full Name", "Email", "Role", "Created At", "Last Login")
            tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            
            for user in users:
                tree.insert("", "end", values=(
                    user.get('username', ''),
                    user.get('full_name', ''),
                    user.get('email', ''),
                    user.get('role', ''),
                    user.get('created_at', ''),
                    user.get('last_login', 'Never') if user.get('last_login') else 'Never'
                ))
            
            tree.pack(fill="both", expand=True, padx=10, pady=10)
            
            scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
            scrollbar.pack(side="right", fill="y")
            tree.configure(yscrollcommand=scrollbar.set)
        else:
            ctk.CTkLabel(list_frame, text="No users found", font=ctk.CTkFont(size=14)).pack(pady=20)
    
    def add_user(self):
        """Add new user to database"""
        username = self.username_entry.get().strip()
        full_name = self.fullname_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        role = self.role_combo.get()
        
        if not username or not full_name or not password:
            messagebox.showerror("Error", "Username, Full Name, and Password are required!")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters!")
            return
        
        if self.auth_manager.add_user_to_db(username, password, full_name, email, role):
            messagebox.showinfo("Success", f"User '{username}' added successfully!")
            # Clear form
            self.username_entry.delete(0, 'end')
            self.fullname_entry.delete(0, 'end')
            self.email_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            # Refresh view
            self.create_user_management()
        else:
            messagebox.showerror("Error", "Failed to add user. Username may already exist!")
