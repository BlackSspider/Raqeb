import customtkinter as ctk
from tkinter import ttk
import sqlite3
from datetime import datetime

class ThreatLogs(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#0a0a0a", corner_radius=15, border_width=2, border_color="#e60000")
        self.pack(pady=20, padx=20, fill="both", expand=True)

        # 1. التأكد من وجود الجدول عند بدء التشغيل
        self.ensure_table_exists()

        # العنوان بنفس تصميمك
        self.header_label = ctk.CTkLabel(self, text="🛡️ RAQEB: Threat Logs", font=("Orbitron", 24, "bold"), text_color="#ffffff")
        self.header_label.pack(pady=15, padx=20, anchor="nw")

        # إحصائيات سريعة (Stat Cards)
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(pady=10, padx=20, fill="x")

        self.card1, self.card1_val = self.create_stat_card(self.stats_frame, "Total Threats", "0", "#ff4d4d")
        self.card1.grid(row=0, column=0, padx=10)

        # إطار المحتوى (الجدول)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # تصميم الجدول (الأسود والأحمر)
        self.table_container = ctk.CTkFrame(self.content_frame, fg_color="#161b22", corner_radius=10)
        self.table_container.pack(side="left", fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Threat.Treeview", background="#0a0a0a", foreground="white", fieldbackground="#0a0a0a", rowheight=35, borderwidth=0)
        style.configure("Threat.Treeview.Heading", background="#e60000", foreground="black", font=("Arial", 11, "bold"), relief="flat")
        style.map("Threat.Treeview", background=[('selected', '#e60000')], foreground=[('selected', 'white')])

        self.tree = ttk.Treeview(self.table_container, columns=("Time", "Type", "Source", "Severity"), show="headings", style="Threat.Treeview")
        for col in ("Time", "Type", "Source", "Severity"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)

        # زر التحديث
        self.refresh_btn = ctk.CTkButton(self, text="REFRESH DATA", fg_color="#4CAF50", hover_color="#388E3C", 
                                          font=("Arial", 12, "bold"), command=self.load_real_data)
        self.refresh_btn.pack(pady=10)

        # تحميل البيانات الحقيقية فور الفتح
        self.load_real_data()

    def ensure_table_exists(self):
        """تنشئ الجدول إذا لم يكن موجوداً في قاعدة البيانات"""
        try:
            conn = sqlite3.connect("raqeb_system.db")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threat_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    threat_type TEXT,
                    source_ip TEXT,
                    severity TEXT,
                    details TEXT,
                    status TEXT DEFAULT 'Unresolved'
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing table: {e}")

    def create_stat_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, fg_color="#161b22", width=200, height=100, border_width=1, border_color=color)
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=title, font=("Arial", 14), text_color="#888888").pack(pady=(15, 0))
        val_label = ctk.CTkLabel(card, text=value, font=("Orbitron", 24, "bold"), text_color=color)
        val_label.pack(pady=5)
        return card, val_label

    def load_real_data(self):
        """جلب البيانات من قاعدة البيانات وعرضها في الجدول"""
        # مسح البيانات القديمة من الواجهة أولاً
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        try:
            conn = sqlite3.connect("raqeb_system.db")
            cursor = conn.cursor()
            
            # جلب آخر السجلات المضافة
            cursor.execute("SELECT timestamp, threat_type, source_ip, severity FROM threat_logs ORDER BY id DESC")
            rows = cursor.fetchall()
            
            for row in rows:
                self.tree.insert("", "end", values=row)
            
            # تحديث العداد الإجمالي
            cursor.execute("SELECT COUNT(*) FROM threat_logs")
            total_count = cursor.fetchone()[0]
            self.card1_val.configure(text=str(total_count))
            
            conn.close()
        except Exception as e:
            print(f"Error loading data: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1100x700")
    root.title("RAQEB - Threat Logs Dashboard")
    app = ThreatLogs(root)
    root.mainloop()
