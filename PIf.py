import customtkinter as ctk
from tkinter import messagebox
import socket

# Appearance Settings
ctk.set_appearance_mode("dark")

class RaqebProtocolFinder(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("RAQEB | Protocol Intelligence")
        self.geometry("600x650")
        self.configure(fg_color="#010101")
        self.attributes("-alpha", 0.98)

        self._build_ui()

    def _build_ui(self):
        # Header
        ctk.CTkLabel(self, text="🔍 PROTOCOL IDENTIFIER", 
                     font=("Orbitron", 26, "bold"), text_color="#00f2ff").pack(pady=25)

        # Main Glass Frame
        self.container = ctk.CTkFrame(self, fg_color="#0a0a0a", border_width=2, 
                                      border_color="#00f2ff", corner_radius=20)
        self.container.pack(padx=40, pady=10, fill="both", expand=True)

        # Input Section
        ctk.CTkLabel(self.container, text="ENTER PORT NUMBER OR NAME", 
                     text_color="#00f2ff", font=("Arial", 12, "bold")).pack(pady=(30, 5))
        
        self.input_entry = ctk.CTkEntry(self.container, width=350, height=45, 
                                        placeholder_text="e.g. 80 or http", fg_color="#000")
        self.input_entry.pack(pady=10)

        # Action Buttons
        btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_frame.pack(pady=20)

        self.btn_by_port = ctk.CTkButton(btn_frame, text="FIND BY PORT #", fg_color="#333", 
                                         font=("Arial", 12, "bold"), command=self.find_by_port)
        self.btn_by_port.pack(side="left", padx=10)

        self.btn_by_name = ctk.CTkButton(btn_frame, text="FIND BY NAME", fg_color="#333", 
                                         font=("Arial", 12, "bold"), command=self.find_by_name)
        self.btn_by_name.pack(side="left", padx=10)

        # Result Display Area
        self.result_label = ctk.CTkLabel(self.container, text="Result will appear here", 
                                         font=("Consolas", 16), text_color="#2ecc71")
        self.result_label.pack(pady=40)

        # Footer Signature
        self.footer = ctk.CTkLabel(self, text="Developed by: Mowfag Adnan Abu Ras", 
                                   font=("Times New Roman", 17, "bold", "italic"), text_color="#D4AF37")
        self.footer.pack(side="bottom", pady=20)

    def find_by_port(self):
        val = self.input_entry.get().strip()
        if not val.isdigit():
            messagebox.showwarning("Input Error", "Please enter a valid numeric port.")
            return
        try:
            name = socket.getservbyport(int(val))
            self.result_label.configure(text=f"Port {val} is assigned to: {name.upper()}", text_color="#2ecc71")
        except:
            self.result_label.configure(text=f"No standard service found for Port {val}", text_color="#e74c3c")

    def find_by_name(self):
        val = self.input_entry.get().strip().lower()
        if not val: return
        try:
            port = socket.getservbyname(val)
            self.result_label.configure(text=f"Service '{val.upper()}' uses Port: {port}", text_color="#2ecc71")
        except:
            self.result_label.configure(text=f"Could not find Port for service: {val}", text_color="#e74c3c")

if __name__ == "__main__":
    app = RaqebProtocolFinder()
    app.mainloop()