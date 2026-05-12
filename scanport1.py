import customtkinter as ctk
from tkinter import ttk

# إعداد المظهر العام
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RaqebInterface(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RAQEB: Port Assistant")
        self.geometry("900x700")
        self.configure(fg_color="#121212") # لون الخلفية الداكن

        # --- الجزء العلوي (Input Area) ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(pady=20, padx=20, fill="x")

        self.ip_entry = ctk.CTkEntry(self.top_frame, placeholder_text="IP Address / Range", width=300, border_color="#444")
        self.ip_entry.grid(row=0, column=0, padx=10, pady=5)

        self.scan_type = ctk.CTkComboBox(self.top_frame, values=["Quick Scan", "Full Scan", "Custom"], width=150)
        self.scan_type.grid(row=0, column=1, padx=10)

        self.scan_btn = ctk.CTkButton(self.top_frame, text="Scan", fg_color="#4CAF50", hover_color="#45a049", width=100)
        self.scan_btn.grid(row=0, column=2, padx=10)

        self.export_btn = ctk.CTkButton(self.top_frame, text="Export Results", fg_color="#e74c3c", hover_color="#c0392b", width=120)
        self.export_btn.grid(row=0, column=3, padx=10)

        # --- الجزء الأوسط (Analysis & Hints) ---
        self.mid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mid_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # جدول البيانات (Port Analysis)
        self.table_frame = ctk.CTkFrame(self.mid_frame, fg_color="#1e1e1e", border_width=1, border_color="#333")
        self.table_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(self.table_frame, text="SERVICE & PORT ANALYSIS", font=("Arial", 14, "bold"), text_color="#ff4d4d").pack(pady=10)

        # تخصيص شكل الجدول (Treeview) ليتناسب مع الثيم الداكن
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e", borderwidth=0)
        style.map("Treeview", background=[('selected', '#333')])

        self.tree = ttk.Treeview(self.table_frame, columns=("Port", "Status", "Service", "Version"), show='headings')
        self.tree.heading("Port", text="PORT")
        self.tree.heading("Status", text="STATUS")
        self.tree.heading("Service", text="SERVICE")
        self.tree.heading("Version", text="VERSION")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # قسم التنبيهات (Vulnerability Hints)
        self.hint_frame = ctk.CTkFrame(self.mid_frame, width=250, fg_color="#1e1e1e", border_width=1, border_color="#333")
        self.hint_frame.pack(side="right", fill="both")
        
        ctk.CTkLabel(self.hint_frame, text="VULNERABILITY HINTS", font=("Arial", 14, "bold"), text_color="#ff4d4d").pack(pady=10)
        
        self.hint_text = ctk.CTkTextbox(self.hint_frame, fg_color="transparent", text_color="#ccc", font=("Arial", 12))
        self.hint_text.pack(fill="both", expand=True, padx=5)
        self.hint_text.insert("0.0", "⚠️ Port 22 (SSH): Detected older version...\n\n⚠️ Port 80 (HTTP): Clear-text communication.")

        # --- الجزء السفلي (Status Bar) ---
        self.status_frame = ctk.CTkFrame(self, height=40, fg_color="#1e1e1e")
        self.status_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        self.progress = ctk.CTkProgressBar(self.status_frame, orientation="horizontal", progress_color="#ff4d4d")
        self.progress.pack(side="left", padx=20, fill="x", expand=True)
        self.progress.set(0.4) # قيمة افتراضية للتقدم

        self.cpu_label = ctk.CTkLabel(self.status_frame, text="CPU: 15% | RAM: 40%", font=("Arial", 12))
        self.cpu_label.pack(side="right", padx=20)

if __name__ == "__main__":
    app = RaqebInterface()
    app.mainloop()