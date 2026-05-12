import customtkinter as ctk
from tkinter import messagebox
import sqlite3

# --- إعدادات النظام وقاعدة البيانات ---
DB_NAME = "raqeb.db"

def setup_full_database():
    """هذا التابع يضمن وجود كل جداول  نظام راقب  قبل تشغيل الواجهة"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # 1. جدول المشرفين (admins)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT  admin ,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # 2. جدول الأجهزة المكتشفة (devices)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT, mac TEXT, vendor TEXT, status TEXT,
        discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # 3. جدول التهديدات (threats)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS threats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT, type TEXT, description TEXT, action TEXT,
        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # 4. جدول الجلسات (sessions)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER, username TEXT,
        login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (admin_id) REFERENCES admins(id)
    )""")
    
    # 5. جدول سجلات الدخول (auth_logs)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS auth_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, success INTEGER, reason TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    conn.commit()
    conn.close()

# --- واجهة تسجيل الدخول ---
ctk.set_appearance_mode("dark")

class RaqebLoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        setup_full_database() # التأكد من الجدولة فوراً
        
        self.title("Raqeb - Login Interface")
        self.geometry("800x750")
        self.configure(fg_color="#0a0a0a")

        # الإطار الرئيسي (Glassmorphism)
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#161b22", border_width=1, border_color="#30363d")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.7)

        # اللوجو
        self.logo_label = ctk.CTkLabel(self.main_frame, text="🔥 Raqeb", font=("Orbitron", 50, "bold"), text_color="#ff4d4d")
        self.logo_label.pack(pady=(50, 5))

        self.sub_label = ctk.CTkLabel(self.main_frame, text="SYSTEM & NETWORK MONITOR", font=("Arial", 13, "bold"), text_color="#ffffff")
        self.sub_label.pack(pady=(0, 40))

        # حقول الإدخال
        self.user_entry = ctk.CTkEntry(self.main_frame, placeholder_text="👤 Username", width=320, height=45, border_color="#ff4d4d", fg_color="#0d1117")
        self.user_entry.pack(pady=12)
        self.user_entry.insert(0, "Mowfag") # المستخدم المطلوب بالحرف الكبير

        self.pass_entry = ctk.CTkEntry(self.main_frame, placeholder_text="🔒 Password", show="*", width=320, height=45, border_color="#ff4d4d", fg_color="#0d1117")
        self.pass_entry.pack(pady=12)

        # زر الدخول المضيء
        self.login_btn = ctk.CTkButton(self.main_frame, text="LOGIN", command=self.handle_login,
                                       fg_color="transparent", border_width=2, border_color="#ff4d4d",
                                       hover_color="#330000", width=220, height=45, font=("Arial", 18, "bold"), text_color="#ff4d4d")
        self.login_btn.pack(pady=40)

    def handle_login(self):
        user = self.user_entry.get()
        password = self.pass_entry.get()

        # شرط الدخول الخاص بك
        if user == "Mowfag" and password == "777116294":
            self.log_auth(user, 1, "Success Bypass")
            self.go_to_dashboard()
        else:
            self.log_auth(user, 0, "Failed Attempt")
            messagebox.showerror("Raqeb", "Access Denied!")

    def log_auth(self, user, success, reason):
        """تسجيل محاولات الدخول في الجداول التي أنشأناها"""
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("INSERT INTO auth_logs (username, success, reason) VALUES (?, ?, ?)", (user, success, reason))
            conn.commit()
            conn.close()
        except Exception: pass

    def go_to_dashboard(self):
        messagebox.showinfo("Raqeb", f"Welcome, Engineer {self.user_entry.get()}")
        self.destroy()
        # المرحلة القادمة: استدعاء واجهة Dashboard الفخمة
        print("Redirecting to Raqeb Dashboard...")

if __name__ == "__main__":
    app = RaqebLoginApp()
    app.mainloop()