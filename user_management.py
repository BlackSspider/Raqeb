import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
import hashlib
import binascii
import os

# --- الإعدادات الموحدة ---
DB_NAME = "raqeb_system.db"
SALT_BYTES = 16
PBKDF2_ITERATIONS = 150_000

class UserManagement(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#0a0a0a")
        self.pack(fill="both", expand=True)

        self.setup_database_safely()

        # الحاوية الزجاجية
        self.glass_frame = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=20, border_width=1, border_color="#30363d")
        self.glass_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.8)

        self.title_label = ctk.CTkLabel(self.glass_frame, text="User Management", font=("Arial", 28, "bold"), text_color="#ffffff")
        self.title_label.pack(pady=(30, 20), padx=40, anchor="nw")

        self.content_layout = ctk.CTkFrame(self.glass_frame, fg_color="transparent")
        self.content_layout.pack(fill="both", expand=True, padx=40, pady=10)

        # الجدول
        self.table_container = ctk.CTkFrame(self.content_layout, fg_color="transparent")
        self.table_container.pack(side="left", fill="both", expand=True, padx=(0, 20))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Custom.Treeview", background="#161b22", foreground="white", fieldbackground="#161b22", rowheight=35, borderwidth=0)
        style.configure("Custom.Treeview.Heading", background="#161b22", foreground="#ff4d4d", font=("Arial", 11, "bold"), borderwidth=0)
        style.map("Custom.Treeview", background=[('selected', '#330000')], foreground=[('selected', '#ff4d4d')])

        self.tree = ttk.Treeview(self.table_container, columns=("User", "Role", "Email", "Date"), show="headings", style="Custom.Treeview")
        for col in ("User", "Role", "Email", "Date"):
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor="center", width=100)
        self.tree.pack(fill="both", expand=True)

        # الأزرار
        self.button_frame = ctk.CTkFrame(self.content_layout, fg_color="transparent")
        self.button_frame.pack(side="right", fill="y")

        self.create_neon_button("➕  Add User", self.open_user_window).pack(pady=10)
        self.create_neon_button("📝  Edit User", self.open_edit_window).pack(pady=10)
        self.create_neon_button("🗑️  Deleter", self.delete_admin).pack(pady=10)

        self.bottom_logo = ctk.CTkLabel(self.glass_frame, text="🔥 Raqeb\nSYSTEM & NETWORK MONITOR", font=("Arial", 10, "bold"), text_color="#ff4d4d", justify="left")
        self.bottom_logo.pack(side="bottom", anchor="sw", padx=40, pady=20)

        self.load_data()

    def create_neon_button(self, text, command):
        return ctk.CTkButton(self.button_frame, text=text, command=command, corner_radius=8, fg_color="transparent", border_width=2, border_color="#ff4d4d", text_color="#ffffff", hover_color="#330000", width=160, height=45, font=("Arial", 13, "bold"))

    def setup_database_safely(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, salt TEXT, role TEXT DEFAULT 'Admin', email TEXT DEFAULT 'N/A', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cur.execute("PRAGMA table_info(admins)")
        if 'email' not in [column[1] for column in cur.fetchall()]:
            cur.execute("ALTER TABLE admins ADD COLUMN email TEXT DEFAULT 'N/A'")
        
        cur.execute("SELECT COUNT(*) FROM admins WHERE username='Mowfag'")
        if cur.fetchone()[0] == 0:
            salt = os.urandom(SALT_BYTES)
            dk = hashlib.pbkdf2_hmac("sha256", "777116294".encode(), salt, PBKDF2_ITERATIONS)
            cur.execute("INSERT INTO admins (username, password_hash, salt, role, email) VALUES (?, ?, ?, ?, ?)", ("Mowfag", binascii.hexlify(dk).decode(), binascii.hexlify(salt).decode(), "Master Admin", "mowfag@raqeb.com"))
        conn.commit()
        conn.close()

    def open_user_window(self, edit_mode=False):
        # نافذة منبثقة موحدة للإضافة والتعديل
        title = "Edit User" if edit_mode else "Add New User"
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry("400x500")
        win.configure(fg_color="#161b22")
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text=title, font=("Arial", 20, "bold"), text_color="#ff4d4d").pack(pady=20)
        
        u_entry = ctk.CTkEntry(win, placeholder_text="Username", width=250, border_color="#ff4d4d")
        u_entry.pack(pady=10)
        
        p_entry = ctk.CTkEntry(win, placeholder_text="Password", show="*", width=250, border_color="#ff4d4d")
        p_entry.pack(pady=10)
        
        e_entry = ctk.CTkEntry(win, placeholder_text="Email", width=250, border_color="#ff4d4d")
        e_entry.pack(pady=10)

        if edit_mode:
            selected = self.tree.item(self.tree.selection()[0])['values']
            u_entry.insert(0, selected[0])
            u_entry.configure(state="disabled") # لا يسمح بتغيير اسم المستخدم
            e_entry.insert(0, selected[2])

        def save():
            user, pwd, email = u_entry.get(), p_entry.get(), e_entry.get()
            if not user or (not edit_mode and not pwd):
                messagebox.showwarning("Error", "Fields missing!")
                return
            
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            if edit_mode:
                if pwd: # إذا أدخل كلمة مرور جديدة يتم تحديثها
                    salt = os.urandom(SALT_BYTES)
                    dk = hashlib.pbkdf2_hmac("sha256", pwd.encode(), salt, PBKDF2_ITERATIONS)
                    cur.execute("UPDATE admins SET password_hash=?, salt=?, email=? WHERE username=?", (binascii.hexlify(dk).decode(), binascii.hexlify(salt).decode(), email, user))
                else:
                    cur.execute("UPDATE admins SET email=? WHERE username=?", (email, user))
            else:
                salt = os.urandom(SALT_BYTES)
                dk = hashlib.pbkdf2_hmac("sha256", pwd.encode(), salt, PBKDF2_ITERATIONS)
                try:
                    cur.execute("INSERT INTO admins (username, password_hash, salt, email) VALUES (?, ?, ?, ?)", (user, binascii.hexlify(dk).decode(), binascii.hexlify(salt).decode(), email))
                except: messagebox.showerror("Error", "Exists!"); return
            
            conn.commit()
            conn.close()
            self.load_data()
            win.destroy()

        ctk.CTkButton(win, text="SAVE", command=save, fg_color="#ff4d4d", hover_color="#330000").pack(pady=30)

    def open_edit_window(self):
        if not self.tree.selection():
            messagebox.showwarning("Selection", "Select a user first!")
            return
        self.open_user_window(edit_mode=True)

    def delete_admin(self):
        selected = self.tree.selection()
        if not selected: return
        user_name = self.tree.item(selected[0])['values'][0]
        if user_name == "Mowfag": return
        if messagebox.askyesno("Confirm", f"Delete {user_name}?"):
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("DELETE FROM admins WHERE username=?", (user_name,))
            conn.commit()
            conn.close()
            self.load_data()

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT username, role, email, created_at FROM admins")
        for row in cur.fetchall(): self.tree.insert("", "end", values=row)
        conn.close()

if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("1000x650")
    app.title("RAQEB - User Management")
    frame = UserManagement(app)
    app.mainloop()
