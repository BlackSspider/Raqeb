#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import subprocess
import datetime
import os
import requests

from scapy.all import ARP, Ether, srp, conf
conf.verb = 0

from ids_engine import RaqebIDS


class RaqebScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Raqeb Network Scanner + IDS")
        self.root.geometry("1100x620")

        self.dark_mode = True
        self.scan_results = []
        self.stop_event = threading.Event()

        # IDS
        self.ids = RaqebIDS()
        self.known_devices = set()

        self._setup_style()
        self._build_ui()

    # ================= STYLE =================
    def _setup_style(self):
        self.style = ttk.Style()
        self._apply_theme()

    def _apply_theme(self):
        if self.dark_mode:
            bg = "#1e1e1e"
            fg = "#ffffff"
            field = "#2d2d2d"
        else:
            bg = "#f5f5f5"
            fg = "#000000"
            field = "#ffffff"

        self.root.configure(bg=bg)
        self.style.theme_use("default")

        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TButton", padding=6)
        self.style.configure("Treeview",
                             background=field,
                             foreground=fg,
                             rowheight=25,
                             fieldbackground=field)
        self.style.map("Treeview", background=[("selected", "#007acc")])

    # ================= UI =================
    def _build_ui(self):
        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=5)

        ttk.Label(top, text="IP Range:").pack(side="left")
        self.ip_entry = ttk.Entry(top, width=25)
        self.ip_entry.pack(side="left", padx=5)
        self.ip_entry.insert(0, "192.168.1.0/24")

        ttk.Button(top, text="Scan", command=self.start_scan).pack(side="left", padx=5)
        ttk.Button(top, text="Stop", command=self.stop_scan).pack(side="left", padx=5)
        ttk.Button(top, text="OS Detect", command=self.detect_os).pack(side="left", padx=5)
        ttk.Button(top, text="Port Scan", command=self.port_scan).pack(side="left", padx=5)
        ttk.Button(top, text="Export", command=self.export_report).pack(side="left", padx=5)
        ttk.Button(top, text="🌙 / ☀️", command=self.toggle_theme).pack(side="right")

        columns = ("IP", "MAC", "Vendor", "OS")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=260)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.status = ttk.Label(self.root, text="Ready")
        self.status.pack(fill="x", padx=10)

    # ================= ARP SCAN =================
    def start_scan(self):
        self.tree.delete(*self.tree.get_children())
        self.scan_results.clear()
        self.stop_event.clear()

        ip_range = self.ip_entry.get().strip()
        self.status.config(text="Scanning network...")

        threading.Thread(target=self.arp_scan, args=(ip_range,), daemon=True).start()

    def stop_scan(self):
        self.stop_event.set()
        self.status.config(text="Scan stopped")

    def arp_scan(self, ip_range):
        try:
            packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range)
            answered = srp(packet, timeout=2, retry=1)[0]

            for _, recv in answered:
                if self.stop_event.is_set():
                    break

                ip = recv.psrc
                mac = recv.hwsrc
                vendor = self.get_vendor(mac)

                result = {"ip": ip, "mac": mac, "vendor": vendor, "os": ""}
                self.scan_results.append(result)

                self.tree.insert("", "end", values=(ip, mac, vendor, ""))

                # IDS: new device
                alerts = self.ids.analyze_new_device(result, self.known_devices)
                self.known_devices.add(mac)
                if alerts:
                    self.status.config(text="🚨 IDS Alert: New device detected")

            self.status.config(text=f"Scan complete: {len(self.scan_results)} devices")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================= OS DETECTION =================
    def detect_os(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Select", "Select a device first")
            return

        ip = self.tree.item(item)["values"][0]
        self.status.config(text=f"Detecting OS for {ip}...")

        def run():
            try:
                output = subprocess.check_output(
                    ["sudo", "nmap", "-O", ip],
                    stderr=subprocess.STDOUT,
                    text=True
                )

                os_info = "Unknown"
                for line in output.splitlines():
                    if "Running:" in line or "OS details:" in line:
                        os_info = line.strip()
                        break

                self.tree.set(item, column="OS", value=os_info)
                for r in self.scan_results:
                    if r["ip"] == ip:
                        r["os"] = os_info

                # IDS: OS analysis
                alerts = self.ids.analyze_os(os_info, ip)
                if alerts:
                    messagebox.showwarning("IDS Alert", "\n".join(alerts))

                self.status.config(text="OS detection complete")

            except subprocess.CalledProcessError as e:
                messagebox.showerror("Nmap Error", e.output)

        threading.Thread(target=run, daemon=True).start()

    # ================= PORT SCAN =================
    def port_scan(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Select", "Select a device first")
            return

        ip = self.tree.item(item)["values"][0]
        scan_output = []

        win = tk.Toplevel(self.root)
        win.title(f"Advanced Port Scan - {ip}")
        win.geometry("950x520")

        left = tk.Frame(win)
        left.pack(side="left", fill="y", padx=5)

        right = tk.Frame(win)
        right.pack(side="right", fill="both", expand=True)

        tk.Label(left, text="Scan Options").pack(pady=5)

        scan_options = [
            "-sV  | Service Version Detection",
            "-sC  | Default Scripts",
            "-T4  | Fast Scan",
            "-p-  | Scan All Ports",
            "-Pn  | No Ping",
            "-A   | Aggressive Scan"
        ]

        options_listbox = tk.Listbox(left, selectmode=tk.MULTIPLE, height=8, width=32)
        for opt in scan_options:
            options_listbox.insert(tk.END, opt)
        options_listbox.pack(padx=5, pady=5)

        btn_frame = tk.Frame(left)
        btn_frame.pack(pady=10)

        text = tk.Text(right, bg="#111", fg="#0f0", insertbackground="white")
        text.pack(fill="both", expand=True)
        text.tag_config("alert", foreground="red")

        def run_scan():
            selected = options_listbox.curselection()
            if not selected:
                messagebox.showwarning("Options", "Select at least one scan option")
                return

            flags = [scan_options[i].split("|")[0].strip() for i in selected]
            command = ["sudo", "nmap"] + flags + [ip]

            text.insert(tk.END, f"[+] Command: {' '.join(command)}\n\n")
            scan_output.clear()

            def thread():
                try:
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )

                    for line in process.stdout:
                        scan_output.append(line)
                        text.insert(tk.END, line)
                        text.see(tk.END)

                    text.insert(tk.END, "\n[✓] Scan Finished\n")

                    # IDS: port scan analysis
                    alerts = self.ids.analyze_port_scan(scan_output, ip)
                    if alerts:
                        text.insert(tk.END, "\n[!!! IDS ALERTS !!!]\n", "alert")
                        for a in alerts:
                            text.insert(tk.END, f"[ALERT] {a}\n", "alert")

                    self.status.config(text="Port scan complete")

                except Exception as e:
                    text.insert(tk.END, str(e))

            threading.Thread(target=thread, daemon=True).start()

        def export_scan():
            if not scan_output:
                messagebox.showwarning("Empty", "No scan result to export")
                return

            file = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text", "*.txt"), ("HTML", "*.html")]
            )
            if not file:
                return

            if file.endswith(".txt"):
                with open(file, "w") as f:
                    f.writelines(scan_output)
            else:
                html = f"""
                <html><body style="background:#111;color:#0f0;font-family:monospace">
                <h3>Raqeb Port Scan - {ip}</h3>
                <pre>{''.join(scan_output)}</pre>
                </body></html>
                """
                with open(file, "w") as f:
                    f.write(html)

            messagebox.showinfo("Export", "Port scan report exported")

        tk.Button(btn_frame, text="Start Scan", width=18, command=run_scan).pack(pady=3)
        tk.Button(btn_frame, text="Export Result", width=18, command=export_scan).pack(pady=3)

    # ================= EXPORT =================
    def export_report(self):
        if not self.scan_results:
            messagebox.showwarning("Empty", "No results to export")
            return

        file = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("HTML", "*.html")]
        )
        if not file:
            return

        if file.endswith(".json"):
            with open(file, "w") as f:
                json.dump(self.scan_results, f, indent=4)
        else:
            self._export_html(file)

        messagebox.showinfo("Export", "Report exported successfully")

    def _export_html(self, path):
        rows = ""
        for r in self.scan_results:
            rows += f"<tr><td>{r['ip']}</td><td>{r['mac']}</td><td>{r['vendor']}</td><td>{r['os']}</td></tr>"

        html = f"""
        <html><body style="background:#111;color:#fff">
        <h2>Raqeb Network Scan</h2>
        <p>{datetime.datetime.now()}</p>
        <table border="1" cellpadding="6">{rows}</table>
        </body></html>
        """
        with open(path, "w") as f:
            f.write(html)

    # ================= UTIL =================
    def get_vendor(self, mac):
        try:
            r = requests.get(f"https://api.macvendors.com/{mac}", timeout=3)
            return r.text if r.status_code == 200 else "Unknown"
        except:
            return "Unknown"

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self._apply_theme()


# ================= MAIN =================
if __name__ == "__main__":
    if os.geteuid() != 0:
        messagebox.showerror("Permission", "Run with sudo")
        exit(1)

    root = tk.Tk()
    app = RaqebScannerApp(root)
    root.mainloop()
