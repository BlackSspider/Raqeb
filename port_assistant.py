import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import socket
import threading
import ipaddress
import sqlite3
from datetime import datetime

class PortAssistant(ctk.CTkFrame):
    def __init__(self, master):
        # التصميم المعتمد في الصور (Neon Red & Black)
        super().__init__(master, fg_color="#0a0a0a", corner_radius=15, border_width=2, border_color="#e60000")
        self.pack(pady=20, padx=20, fill="both", expand=True)

        self.is_scanning = False 

        # العنوان
        self.title = ctk.CTkLabel(self, text="RAQEB: Port Assistant", font=("Orbitron", 28, "bold"), text_color="#ffffff")
        self.title.pack(pady=20)

        # إطار المدخلات والأزرار
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=10, padx=20, fill="x")

        self.ip_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Target (e.g., 172.29.19.0/24)", 
                                     width=350, border_color="#e60000", fg_color="#161b22", text_color="white")
        self.ip_entry.grid(row=0, column=0, padx=5)

        # الأزرار بنفس الألوان
        self.scan_btn = ctk.CTkButton(self.input_frame, text="SCAN", fg_color="#4CAF50", hover_color="#388E3C", 
                                       text_color="white", font=("Arial", 12, "bold"), width=80, command=self.start_scan_thread)
        self.scan_btn.grid(row=0, column=1, padx=5)

        self.stop_btn = ctk.CTkButton(self.input_frame, text="STOP", fg_color="#e60000", hover_color="#990000", 
                                       text_color="white", font=("Arial", 12, "bold"), width=80, command=self.stop_scan, state="disabled")
        self.stop_btn.grid(row=0, column=2, padx=5)

        self.export_btn = ctk.CTkButton(self.input_frame, text="EXPORT", fg_color="transparent", border_width=1, border_color="#e60000", 
                                         text_color="white", hover_color="#330000", font=("Arial", 12, "bold"), width=80, command=self.export_results)
        self.export_btn.grid(row=0, column=3, padx=5)

        # القسم الأوسط
        self.main_layout = ctk.CTkFrame(self, fg_color="transparent")
        self.main_layout.pack(pady=10, fill="both", expand=True)

        # الجدول بتنسيق الألوان الخاص بك
        self.table_frame = ctk.CTkFrame(self.main_layout, fg_color="#161b22")
        self.table_frame.pack(side="left", padx=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#0a0a0a", foreground="white", fieldbackground="#0a0a0a", rowheight=30, borderwidth=0)
        style.configure("Treeview.Heading", background="#e60000", foreground="black", font=("Arial", 10, "bold"), relief="flat")
        style.map("Treeview", background=[('selected', '#e60000')], foreground=[('selected', 'white')])

        self.tree = ttk.Treeview(self.table_frame, columns=("IP", "Port", "Status", "Service"), show="headings")
        for col in ("IP", "Port", "Status", "Service"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)

        # حقل التلميحات (الجانب الأيمن)
        self.hints_frame = ctk.CTkFrame(self.main_layout, fg_color="#161b22", width=280)
        self.hints_frame.pack(side="right", padx=10, fill="y")
        self.hints_label = ctk.CTkLabel(self.hints_frame, text="VULNERABILITY HINTS", font=("Arial", 14, "bold"), text_color="#ff4d4d")
        self.hints_label.pack(pady=10)
        self.hints_text = ctk.CTkTextbox(self.hints_frame, width=260, fg_color="transparent", text_color="#cccccc", font=("Consolas", 11))
        self.hints_text.pack(pady=5, padx=5, fill="both", expand=True)

    def log_threat_to_db(self, ip, port, svc, severity):
        """إرسال التهديد المكتشف إلى جدول السجلات"""
        try:
            conn = sqlite3.connect("raqeb_system.db")
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            details = f"Detected open port {port} ({svc}) during scan."
            
            cursor.execute("INSERT INTO threat_logs (timestamp, threat_type, source_ip, severity, details) VALUES (?, ?, ?, ?, ?)",
                           (now, "Port Scan Discovery", ip, severity, details))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database Logging Failed: {e}")

    def stop_scan(self):
        self.is_scanning = False
        self.stop_btn.configure(state="disabled")

    def start_scan_thread(self):
        target = self.ip_entry.get().strip()
        if not target: return
        self.is_scanning = True
        self.scan_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        for i in self.tree.get_children(): self.tree.delete(i)
        self.hints_text.delete("0.0", "end")
        threading.Thread(target=self.run_logic, args=(target,), daemon=True).start()

    def run_logic(self, target):
        try:
            if "/" in target:
                net = ipaddress.ip_network(target, strict=False)
                for ip in net.hosts():
                    if not self.is_scanning: break
                    self.scan_ports(str(ip))
            else:
                self.scan_ports(target)
        finally:
            self.is_scanning = False
            self.master.after(0, self.on_finish)

    def on_finish(self):
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        messagebox.showinfo("Raqeb", "Scan task completed successfully.")

    def scan_ports(self, ip):
        port_map = {21:"FTP", 22:"SSH", 23:"TELNET", 80:"HTTP", 443:"HTTPS", 445:"SMB", 3389:"RDP"}
        for port, svc in port_map.items():
            if not self.is_scanning: return
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                if s.connect_ex((ip, port)) == 0:
                    self.tree.insert("", "end", values=(ip, port, "OPEN", svc))
                    self.add_vulnerability_hint(ip, port, svc)
                    # --- عملية الربط هنا ---
                    severity = "High" if port in [21, 23, 445] else "Medium"
                    self.log_threat_to_db(ip, port, svc, severity)

    def add_vulnerability_hint(self, ip, port, svc):
        hints = {21: "FTP (Unencrypted)", 23: "Telnet (Insecure Risk)", 445: "SMB (WannaCry Risk)", 80: "HTTP (No Encryption)"}
        if port in hints:
            self.hints_text.insert("end", f"⚠️ {ip}: {hints[port]}\n\n")
            self.hints_text.see("end")

    def export_results(self):
        # (دالة التصدير كما في الكود السابق)
        pass

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1100x700")
    root.title("RAQEB System - Port Assistant")
    app = PortAssistant(root)
    root.mainloop()
