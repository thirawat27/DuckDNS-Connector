import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import configparser
import requests
import threading
import time
from PIL import Image
from pystray import MenuItem as item, Icon, Menu
import os
import sys
import logging
import re
import socket
from filelock import FileLock, Timeout

# --- Windows-specific icon setup ---
try:
    import ctypes
    from win32con import WM_SETICON, ICON_SMALL, ICON_BIG, IMAGE_ICON, LR_LOADFROMFILE
    import win32gui
    IS_WINDOWS = True
except ImportError:
    IS_WINDOWS = False

def set_window_icon_win32(window):
    """Sets the window icon robustly on Windows."""
    if not IS_WINDOWS:
        return
    try:
        if not window.winfo_exists():
            return
        hwnd = window.winfo_id()
        if os.path.exists(LOGO_FILE):
            h_icon = win32gui.LoadImage(0, LOGO_FILE, IMAGE_ICON, 0, 0, LR_LOADFROMFILE)
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_icon)
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_icon)
    except Exception as e:
        logging.error(f"Failed to set Windows-specific icon: {e}")

# --- Application Constants ---
APP_NAME = "DuckDNS Connector" # REBRAND
APP_VERSION = "1.0.0" # REBRAND
CONFIG_FILE = "config.ini"

# --- Setup Logging ---
def setup_logging():
    """Sets up a basic file logger."""
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_file = 'duckdns_connector.log' # REBRAND log file name
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)

# --- Resource Path Function ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

LOGO_FILE = resource_path("./logo.ico")

# --- Modern Dark Theme Colors ---
THEME = {
    "bg_primary": "#0F0F0F",
    "bg_secondary": "#1A1A1A",
    "bg_tertiary": "#252525",
    "bg_hover": "#2D2D2D",

    "accent_primary": "#0EA5E9",
    "accent_hover": "#0284C7",
    "accent_glow": "#38BDF8",

    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",

    "text_primary": "#F5F5F5",
    "text_secondary": "#A1A1AA",
    "text_tertiary": "#71717A",

    "border": "#2D2D2D",
    "border_focus": "#0EA5E9",
    "border_error": "#EF4444",

    "shadow": "#00000040",
}

def setup_styles(root):
    """Sets up modern ttk styles."""
    style = ttk.Style(root)
    style.theme_use('clam')

    root.option_add('*TCombobox*Listbox.background', THEME["bg_tertiary"])
    root.option_add('*TCombobox*Listbox.foreground', THEME["text_primary"])
    root.option_add('*TCombobox*Listbox.selectBackground', THEME["accent_primary"])
    root.option_add('*TCombobox*Listbox.selectForeground', THEME["text_primary"])
    root.option_add('*TCombobox*Listbox.font', ("Segoe UI", 10))
    root.option_add('*TCombobox*Listbox.relief', 'flat')
    root.option_add('*TCombobox*Listbox.borderwidth', 0)

    style.configure('.',
                    background=THEME["bg_secondary"],
                    foreground=THEME["text_primary"],
                    fieldbackground=THEME["bg_tertiary"],
                    borderwidth=0,
                    relief="flat")

    style.configure('TFrame', background=THEME["bg_primary"])
    style.configure('TLabel',
                    background=THEME["bg_secondary"],
                    foreground=THEME["text_primary"],
                    font=("Segoe UI", 10))

    style.configure('Modern.TEntry',
                    foreground=THEME["text_primary"],
                    fieldbackground=THEME["bg_tertiary"],
                    insertcolor=THEME["accent_primary"],
                    borderwidth=2,
                    relief="flat",
                    bordercolor=THEME["border"],
                    lightcolor=THEME["border"],
                    darkcolor=THEME["border"],
                    padding=(14, 12))

    style.map('Modern.TEntry',
              fieldbackground=[('focus', THEME["bg_hover"])],
              bordercolor=[('focus', THEME["accent_primary"])],
              lightcolor=[('focus', THEME["accent_primary"])],
              darkcolor=[('focus', THEME["accent_primary"])])

    style.configure('Modern.TCombobox',
                    fieldbackground=THEME["bg_tertiary"],
                    background=THEME["bg_tertiary"],
                    foreground=THEME["text_primary"],
                    arrowcolor=THEME["text_secondary"],
                    selectbackground=THEME["bg_tertiary"],
                    selectforeground=THEME["text_primary"],
                    borderwidth=2,
                    relief="flat",
                    bordercolor=THEME["border"],
                    lightcolor=THEME["border"],
                    darkcolor=THEME["border"],
                    padding=(14, 12))

    style.map('Modern.TCombobox',
              fieldbackground=[('readonly', THEME["bg_tertiary"]), ('focus', THEME["bg_hover"])],
              selectbackground=[('readonly', THEME["bg_tertiary"])],
              bordercolor=[('focus', THEME["accent_primary"])],
              lightcolor=[('focus', THEME["accent_primary"])],
              darkcolor=[('focus', THEME["accent_primary"])],
              arrowcolor=[('hover', THEME["text_primary"])])

    style.configure('Toggle.TButton',
                    background=THEME["bg_hover"],
                    foreground=THEME["text_secondary"],
                    font=("Segoe UI", 9),
                    borderwidth=0,
                    relief="flat",
                    padding=(12, 8))

    style.map('Toggle.TButton',
              background=[('active', THEME["bg_tertiary"])],
              foreground=[('active', THEME["accent_primary"])])

# --- UI-FIX: Helper function to draw rounded rectangles on a canvas ---
def create_rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    """Helper to draw a rounded rectangle on a given canvas."""
    return canvas.create_polygon(
        (x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1,
         x2, y1, x2, y1 + r, x2, y1 + r, x2, y2 - r,
         x2, y2, x2 - r, y2, x2 - r, y2, x1 + r, y2,
         x1, y2, x1, y2 - r, x1, y2 - r, x1, y1 + r,
         x1, y1, x1 + r, y1),
        smooth=True, **kwargs
    )

# --- Custom Rounded Button Class ---
class RoundedButton(tk.Canvas):
    """A custom rounded button created with Canvas, supporting hover effects."""
    def __init__(self, parent, width, height, radius, text, command,
                 bg_color, fg_color, hover_color, text_font=("Segoe UI", 10, "bold")):
        super().__init__(parent, width=width, height=height, bg=parent.cget("bg"),
                         highlightthickness=0, borderwidth=0)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color

        self.button_shape = create_rounded_rect(self, 0, 0, width, height, radius, fill=bg_color)
        self.button_text = self.create_text(width / 2, height / 2, text=text, fill=fg_color, font=text_font)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_enter(self, event):
        self.itemconfig(self.button_shape, fill=self.hover_color)

    def _on_leave(self, event):
        self.itemconfig(self.button_shape, fill=self.bg_color)

    def _on_click(self, event):
        if self.command:
            self.command()

# --- Modern Message Box ---
class ModernMessageBox(tk.Toplevel):
    def __init__(self, master, title, message, msg_type="info"):
        super().__init__(master)
        self.title(title)
        self.msg_type = msg_type

        self.resizable(False, False)
        self.configure(bg=THEME["bg_primary"])
        self.attributes("-topmost", True)
        self.overrideredirect(False)
        self.after(100, self._apply_icon_delayed)

        icon_colors = {
            "info": THEME["accent_primary"], "success": THEME["success"],
            "warning": THEME["warning"], "error": THEME["error"]
        }
        self.icon_color = icon_colors.get(msg_type, THEME["accent_primary"])
        self._create_ui(message)

        self.update_idletasks()
        fixed_width = 460
        required_height = self.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (fixed_width // 2)
        y = (self.winfo_screenheight() // 2) - (required_height // 2)
        self.geometry(f"{fixed_width}x{required_height}+{x}+{y}")

        self.attributes('-alpha', 0.0)
        self._fade_in()
        self.focus()

    def _create_ui(self, message):
        main_frame = tk.Frame(self, bg=THEME["bg_primary"])
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        icon_frame = tk.Canvas(main_frame, width=60, height=60, bg=THEME["bg_primary"], highlightthickness=0)
        icon_frame.pack(pady=(0, 20))
        icon_frame.create_oval(5, 5, 55, 55, fill=self.icon_color, outline="")

        icon_symbols = {"info": "i", "success": "✓", "warning": "!", "error": "✕"}
        icon_text = icon_symbols.get(self.msg_type, "i")
        font_size = 28 if self.msg_type in ["info", "warning"] else 24
        icon_font = ("Segoe UI", font_size, "bold")
        icon_frame.create_text(30, 30, text=icon_text, fill=THEME["text_primary"], font=icon_font)

        msg_label = tk.Label(main_frame, text=message, fg=THEME["text_primary"], bg=THEME["bg_primary"],
                           font=("Segoe UI", 11), wraplength=380, justify="center")
        msg_label.pack(pady=(0, 30))
        
        ok_btn = RoundedButton(parent=main_frame, width=150, height=45, radius=22, text="Got it",
                          command=self._fade_out, bg_color=THEME["accent_primary"],
                          fg_color=THEME["text_primary"], hover_color=THEME["accent_hover"])
        ok_btn.pack()

    def _fade_in(self, alpha=0.0):
        alpha += 0.1
        if alpha <= 1.0:
            self.attributes('-alpha', alpha)
            self.after(20, lambda: self._fade_in(alpha))

    def _fade_out(self, alpha=1.0):
        alpha -= 0.1
        if alpha >= 0.0:
            self.attributes('-alpha', alpha)
            self.after(20, lambda: self._fade_out(alpha))
        else:
            self.destroy()

    def _apply_icon_delayed(self):
        try:
            if self.winfo_exists() and os.path.exists(LOGO_FILE):
                self.iconbitmap(LOGO_FILE)
                set_window_icon_win32(self)
        except Exception as e:
            logging.warning(f"Could not set icon for ModernMessageBox: {e}")

# --- ConfigManager ---
class ConfigManager:
    def __init__(self, filename=CONFIG_FILE):
        self.filename = filename
        self.config = configparser.ConfigParser()
        self.load()

    def load(self):
        try:
            self.config.read(self.filename, encoding='utf-8')
        except Exception as e: logging.error(f"Error reading config file: {e}")
        if "DuckDNS" not in self.config: self.config["DuckDNS"] = {"domain": "", "token": ""}
        if "Settings" not in self.config: self.config["Settings"] = {"interval": "5", "notifications": "YES"}
        logging.info("Configuration loaded.")

    def save(self):
        try:
            with open(self.filename, "w", encoding='utf-8') as configfile: self.config.write(configfile)
            logging.info("Configuration saved.")
        except Exception as e: logging.error(f"Error saving config file: {e}")

    def get(self, section, option, fallback=None):
        return self.config.get(section, option, fallback=fallback)

    def get_all_settings(self):
        return {"domain": self.get("DuckDNS", "domain", ""),"token": self.get("DuckDNS", "token", ""),
                "interval": self.get("Settings", "interval", "5"),"notifications": self.get("Settings", "notifications", "YES")}

    def update_settings(self, domain, token, interval, notifications):
        self.config["DuckDNS"]["domain"] = domain
        self.config["DuckDNS"]["token"] = token
        self.config["Settings"]["interval"] = str(interval)
        self.config["Settings"]["notifications"] = notifications
        self.save()

# --- DuckDNS Client ---
class DuckDNSClient:
    IP_PROVIDERS = ["https://api.ipify.org", "https://icanhazip.com", "https://ifconfig.me/ip", "https://api.my-ip.io/ip"]

    def is_connected(self, host="8.8.8.8", port=53, timeout=3):
        try:
            socket.create_connection((host, port), timeout=timeout)
            logging.info("Internet connection check successful.")
            return True
        except OSError as e:
            logging.warning(f"Internet connection check failed: {e}")
            return False

    def get_public_ip(self):
        for provider in self.IP_PROVIDERS:
            try:
                response = requests.get(provider, timeout=10)
                response.raise_for_status()
                ip = response.text.strip()
                if self._is_valid_ip(ip):
                    logging.info(f"Successfully retrieved public IP {ip} from {provider}")
                    return ip
                else: logging.warning(f"Invalid IP format received from {provider}: {ip}")
            except requests.RequestException as e: logging.warning(f"Failed to get IP from {provider}: {e}")
        logging.error("All public IP providers failed.")
        return None

    def _is_valid_ip(self, ip):
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip): return all(0 <= int(part) <= 255 for part in ip.split('.'))
        return False

    def update_duckdns(self, domain, token, ip):
        params = {"domains": domain, "token": token, "ip": ip}
        try:
            response = requests.get("https://www.duckdns.org/update", params=params, timeout=10)
            response.raise_for_status()
            result = response.text.strip()
            logging.info(f"DuckDNS update response: {result}")
            return result
        except requests.RequestException as e:
            logging.error(f"DuckDNS update request failed: {e}")
            return "ERROR"

# --- Modern Settings Window ---
class ModernSettingsWindow(tk.Toplevel):
    def __init__(self, master, current_settings, save_callback):
        super().__init__(master)
        self.save_callback = save_callback

        # --- FIX FOR FLASHING WINDOW ---
        self.withdraw()
        self.attributes('-alpha', 0.0)
        # --- END OF FIX ---

        self.title(f"{APP_NAME} Settings")
        self.resizable(False, False) 
        self.configure(bg=THEME["bg_primary"])
        self.after(100, self._apply_icon_delayed)

        self.grid_rowconfigure(0, weight=1); self.grid_rowconfigure(1, weight=0); self.grid_columnconfigure(0, weight=1)

        self._build_scroll_area()
        self._build_header(self.content_frame)
        self._create_credentials_card(self.content_frame, current_settings)
        self._create_app_settings_card(self.content_frame, current_settings)
        self._build_footer()

        # --- FIX FOR FLASHING WINDOW (PART 2) ---
        self.update_idletasks()
        width, height = 560, 660
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(width, height)
        self.deiconify()
        self._fade_in()
        # --- END OF FIX ---
        
        self.focus()

    def _build_scroll_area(self):
        outer = tk.Frame(self, bg=THEME["bg_primary"])
        outer.grid(row=0, column=0, sticky="nsew")
        self.canvas = tk.Canvas(outer, bg=THEME["bg_primary"], highlightthickness=0, bd=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.content_frame = tk.Frame(self.canvas, bg=THEME["bg_primary"])
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas.find_all()[0], width=e.width))
        self.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-3, "units"))
        self.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(3, "units"))

    def _build_header(self, parent):
        header_frame = tk.Frame(parent, bg=THEME["bg_primary"], height=80)
        header_frame.pack(fill="x", padx=30, pady=(30, 20)); header_frame.pack_propagate(False)
        tk.Label(header_frame, text="DuckDNS Connection Settings", fg=THEME["text_primary"], bg=THEME["bg_primary"], font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(header_frame, text="Configure your DuckDNS connection", fg=THEME["text_secondary"], bg=THEME["bg_primary"], font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 0))
        tk.Frame(parent, bg=THEME["bg_secondary"]).pack(fill="x", padx=0)

    def _build_footer(self):
        footer = tk.Frame(self, bg=THEME["bg_primary"])
        footer.grid(row=1, column=0, sticky="ew")
        inner = tk.Frame(footer, bg=THEME["bg_primary"])
        inner.pack(fill="x", padx=30, pady=20)
        inner.grid_columnconfigure(0, weight=1); inner.grid_columnconfigure(1, weight=1)

        cancel_btn = RoundedButton(parent=inner, width=200, height=48, radius=24, text="Cancel", command=self._fade_out,
                                 bg_color=THEME["bg_tertiary"], fg_color=THEME["text_secondary"], hover_color=THEME["bg_hover"])
        cancel_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        save_btn = RoundedButton(parent=inner, width=200, height=48, radius=24, text="Save Changes", command=self.save_and_close,
                               bg_color=THEME["accent_primary"], fg_color=THEME["text_primary"], hover_color=THEME["accent_hover"])
        save_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def _create_rounded_card(self, parent, pady):
        card_outer = tk.Frame(parent, bg=THEME["bg_primary"])
        card_outer.pack(fill="x", padx=30, pady=pady)
        
        card_canvas = tk.Canvas(card_outer, bg=THEME["bg_primary"], highlightthickness=0)
        card_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        card_canvas.bind('<Configure>', 
            lambda e: (
                e.widget.delete("all"), 
                create_rounded_rect(e.widget, 0, 0, e.width, e.height, 15, fill=THEME["bg_secondary"])
            )
        )
        
        content_frame = tk.Frame(card_outer, bg=THEME["bg_secondary"])
        content_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        return content_frame

    def _create_credentials_card(self, parent, settings):
        card = self._create_rounded_card(parent, pady=(20, 20))

        header = tk.Frame(card, bg=THEME["bg_secondary"])
        header.pack(fill="x", padx=25, pady=(25, 20))
        tk.Label(header, text="🔐 DuckDNS Credentials", fg=THEME["text_primary"], bg=THEME["bg_secondary"], font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(header, text="Enter your DuckDNS account information", fg=THEME["text_secondary"], bg=THEME["bg_secondary"], font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 0))

        domain_frame = tk.Frame(card, bg=THEME["bg_secondary"])
        domain_frame.pack(fill="x", padx=25, pady=(0, 20))
        tk.Label(domain_frame, text="Domain", fg=THEME["text_primary"], bg=THEME["bg_secondary"], font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))
        self.domain_entry = ttk.Entry(domain_frame, style='Modern.TEntry')
        self.domain_entry.pack(fill="x"); self.domain_entry.insert(0, settings.get("domain", ""))
        tk.Label(domain_frame, text="Enter your subdomain only (e.g., my-home-server)", fg=THEME["text_tertiary"], bg=THEME["bg_secondary"], font=("Segoe UI", 9, "italic")).pack(anchor="w", pady=(8, 0))

        token_frame = tk.Frame(card, bg=THEME["bg_secondary"])
        token_frame.pack(fill="x", padx=25, pady=(0, 25))
        tk.Label(token_frame, text="Token", fg=THEME["text_primary"], bg=THEME["bg_secondary"], font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))
        token_input_frame = tk.Frame(token_frame, bg=THEME["bg_secondary"])
        token_input_frame.pack(fill="x")

        token_input_frame.grid_columnconfigure(0, weight=1)
        token_input_frame.grid_columnconfigure(1, weight=0)

        self.token_entry = ttk.Entry(token_input_frame, show="•", style='Modern.TEntry')
        self.token_entry.grid(row=0, column=0, sticky="ewns")
        self.token_entry.insert(0, settings.get("token", ""))

        self.show_token_btn = ttk.Button(token_input_frame, text="Show", command=self.toggle_token_visibility, style='Toggle.TButton')
        self.show_token_btn.grid(row=0, column=1, sticky="ns", padx=(10, 0))

        tk.Label(token_frame, text="Find this on your DuckDNS account page", fg=THEME["text_tertiary"], bg=THEME["bg_secondary"], font=("Segoe UI", 9, "italic")).pack(anchor="w", pady=(8, 0))

    def _create_app_settings_card(self, parent, settings):
        card = self._create_rounded_card(parent, pady=(0, 10))

        header = tk.Frame(card, bg=THEME["bg_secondary"])
        header.pack(fill="x", padx=25, pady=(25, 20))
        tk.Label(header, text="⚙️ Application Settings", fg=THEME["text_primary"], bg=THEME["bg_secondary"], font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(header, text="Customize how the app behaves", fg=THEME["text_secondary"], bg=THEME["bg_secondary"], font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 0))

        interval_frame = tk.Frame(card, bg=THEME["bg_secondary"])
        interval_frame.pack(fill="x", padx=25, pady=(0, 20))
        tk.Label(interval_frame, text="Update Interval", fg=THEME["text_primary"], bg=THEME["bg_secondary"], font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))
        self.interval_combo = ttk.Combobox(interval_frame, values=["5", "10", "15", "30", "60"], state="readonly", style='Modern.TCombobox')
        self.interval_combo.set(settings.get("interval", "5")); self.interval_combo.pack(fill="x")
        
        # --- FIX: Disable mouse wheel scrolling on Combobox ---
        self.interval_combo.bind("<MouseWheel>", lambda e: "break")
        self.interval_combo.bind("<Button-4>", lambda e: "break")
        self.interval_combo.bind("<Button-5>", lambda e: "break")
        # --- END OF FIX ---
        
        tk.Label(interval_frame, text="How often to check for IP changes (in minutes)", fg=THEME["text_tertiary"], bg=THEME["bg_secondary"], font=("Segoe UI", 9, "italic")).pack(anchor="w", pady=(8, 0))

        notify_frame = tk.Frame(card, bg=THEME["bg_secondary"])
        notify_frame.pack(fill="x", padx=25, pady=(0, 25))
        tk.Label(notify_frame, text="Notifications", fg=THEME["text_primary"], bg=THEME["bg_secondary"], font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))
        self.notify_combo = ttk.Combobox(notify_frame, values=["YES", "NO"], state="readonly", style='Modern.TCombobox')
        self.notify_combo.set(settings.get("notifications", "YES")); self.notify_combo.pack(fill="x")

        # --- FIX: Disable mouse wheel scrolling on Combobox ---
        self.notify_combo.bind("<MouseWheel>", lambda e: "break")
        self.notify_combo.bind("<Button-4>", lambda e: "break")
        self.notify_combo.bind("<Button-5>", lambda e: "break")
        # --- END OF FIX ---
        
        tk.Label(notify_frame, text="Show system notifications for updates", fg=THEME["text_tertiary"], bg=THEME["bg_secondary"], font=("Segoe UI", 9, "italic")).pack(anchor="w", pady=(8, 0))

    def toggle_token_visibility(self):
        if self.token_entry.cget("show") == "•": self.token_entry.config(show=""); self.show_token_btn.config(text="Hide")
        else: self.token_entry.config(show="•"); self.show_token_btn.config(text="Show")

    def save_and_close(self):
        domain, token = self.domain_entry.get().strip(), self.token_entry.get().strip()
        if not domain or not token: return ModernMessageBox(self, "Error", "Domain and Token cannot be empty.", "error")
        domain = domain.replace(".duckdns.org", "")
        if not re.match(r"^[a-zA-Z0-9-]+$", domain): return ModernMessageBox(self, "Invalid Domain", "Domain format is invalid.\nIt should only contain letters, numbers, and hyphens.", "error")
        if not re.match(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$", token, re.IGNORECASE): return ModernMessageBox(self, "Invalid Token", "The token format appears to be incorrect.\nPlease double-check it on your DuckDNS account page.", "warning")
        self.save_callback({"domain": domain, "token": token, "interval": self.interval_combo.get(), "notifications": self.notify_combo.get()})
        self._fade_out()

    def _fade_in(self, alpha=0.0):
        if alpha <= 1.0: self.attributes('-alpha', alpha); self.after(20, lambda: self._fade_in(alpha + 0.1))
    def _fade_out(self, alpha=1.0):
        if alpha >= 0.0: self.attributes('-alpha', alpha); self.after(20, lambda: self._fade_out(alpha - 0.1))
        else: self.destroy()
    def _apply_icon_delayed(self):
        try:
            if self.winfo_exists() and os.path.exists(LOGO_FILE): self.iconbitmap(LOGO_FILE); set_window_icon_win32(self)
        except Exception as e: logging.warning(f"Could not set icon for ModernSettingsWindow: {e}")

# --- UpdateWorker ---
class UpdateWorker(threading.Thread):
    def __init__(self, app_controller):
        super().__init__(daemon=True)
        self.app, self.client, self.last_ip = app_controller, DuckDNSClient(), None
        self.stop_event, self.force_update_event = threading.Event(), threading.Event()
        self._running = False

    def run(self):
        self._running = True; logging.info("UpdateWorker thread started."); time.sleep(2)
        while not self.stop_event.is_set():
            try: self.run_update_cycle()
            except Exception as e: logging.error(f"Error in update cycle: {e}", exc_info=True); self.app.update_status("Error in update cycle. Check logs.", is_error=True)
            try: interval_minutes = int(self.app.config.get("Settings", "interval", "5"))
            except ValueError: interval_minutes = 5
            if interval_minutes < 1: interval_minutes = 5
            for _ in range(interval_minutes * 60):
                if self.stop_event.is_set(): break
                if self.force_update_event.wait(timeout=1): self.force_update_event.clear(); break
        self._running = False; logging.info("UpdateWorker thread stopped.")

    def run_update_cycle(self):
        if self.stop_event.is_set(): return
        if not self.client.is_connected(): return self.app.update_status("Error: No internet connection.", is_error=True)
        settings = self.app.config.get_all_settings()
        if not settings["domain"] or not settings["token"]: return self.app.update_status("Configuration missing. Right-click to open Settings.")
        self.app.update_status("Checking public IP...")
        public_ip = self.client.get_public_ip()
        if self.stop_event.is_set(): return
        if not public_ip: return self.app.update_status("Error: Could not get public IP.", is_error=True)
        if public_ip != self.last_ip:
            self.app.update_status(f"New IP: {public_ip}. Updating...")
            result = self.client.update_duckdns(settings["domain"], settings["token"], public_ip)
            if "OK" in result:
                self.last_ip = public_ip
                self.app.update_status(f"Update successful! IP is now {public_ip}")
                logging.info(f"IP updated successfully to {public_ip} for domain {settings['domain']}.")
            elif "KO" in result: self.app.update_status("Update failed! Check Domain/Token.", is_error=True); logging.error("Update failed (KO).")
            else: self.app.update_status("Error connecting to DuckDNS.", is_error=True); logging.error(f"Unknown error from DuckDNS. Response: {result}")
        else: self.app.update_status(f"IP unchanged: {public_ip}"); logging.info(f"IP address ({public_ip}) has not changed.")

    def stop(self):
        logging.info("Stopping UpdateWorker..."); self.stop_event.set(); self.force_update_event.set()
        if self._running and threading.current_thread() != self: self.join(timeout=5)
    def force_update(self):
        logging.info("Force update triggered by user."); self.app.update_status("Forcing update..."); self.force_update_event.set()

# --- Main Application Controller ---
class DuckDNSSentryApp:
    def __init__(self):
        self.root = tk.Tk(); self.root.withdraw()
        self.image_for_tray, self.icon, self.settings_window = None, None, None
        self.config = ConfigManager()
        self.worker = UpdateWorker(self)
        self._is_exiting = False

    def _setup_icons(self):
        if not os.path.exists(LOGO_FILE): self._show_fatal_error(f"Icon file not found:\n{LOGO_FILE}"); return False
        try:
            self.image_for_tray = Image.open(LOGO_FILE)
            if self.image_for_tray.size[0] > 256 or self.image_for_tray.size[1] > 256:
                self.image_for_tray = self.image_for_tray.resize((256, 256), Image.Resampling.LANCZOS)
            self.root.after(100, self._apply_root_icon); return True
        except Exception as e: self._show_fatal_error(f"Failed to load icon file.\nError: {e}"); return False

    def _apply_root_icon(self):
        try:
            if self.root.winfo_exists() and os.path.exists(LOGO_FILE): self.root.iconbitmap(LOGO_FILE); set_window_icon_win32(self.root)
        except Exception as e: logging.warning(f"Could not set icon for root window: {e}")

    def run(self):
        logging.info(f"Starting {APP_NAME} v{APP_VERSION}")
        if not self._setup_icons(): sys.exit(1)
        setup_styles(self.root)
        menu = (item('Settings', self.open_settings, default=True), item('Force Update', self.worker.force_update),
                item('Show My Public IP', self.show_ip), Menu.SEPARATOR, item(f'About {APP_NAME}', self.show_about),
                item('Exit', self.exit_app))
        self.icon = Icon(APP_NAME, self.image_for_tray, f"{APP_NAME} - Starting...", menu)
        self.worker.start()
        try: self.icon.run_detached(); self.root.mainloop()
        except Exception as e: logging.critical(f"Error in main loop: {e}", exc_info=True)
        finally: self._cleanup()

    def _cleanup(self):
        if self._is_exiting: return
        self._is_exiting = True; logging.info("Cleaning up resources...")
        try: self.worker.stop(); self.icon.stop()
        except Exception as e: logging.error(f"Error during cleanup: {e}")

    def _show_fatal_error(self, message):
        logging.critical(message); temp_root = tk.Tk(); temp_root.withdraw()
        messagebox.showerror("Fatal Error", message); temp_root.destroy()

    def update_status(self, message, is_error=False):
        if not self._is_exiting: self.root.after(0, self._update_status_threadsafe, message, is_error)

    def _update_status_threadsafe(self, message, is_error):
        if not self.icon or self._is_exiting: return
        try:
            self.icon.title = f"{APP_NAME}\n[{time.strftime('%H:%M:%S')}] {message}"
            has_notify = hasattr(self.icon, 'HAS_NOTIFICATION') and self.icon.HAS_NOTIFICATION
            if self.config.get("Settings", "notifications") == "YES" and has_notify:
                self.icon.notify(message, f"{APP_NAME} Error" if is_error else f"{APP_NAME}")
        except Exception as e: logging.error(f"Error updating status: {e}")

    def show_modern_dialog(self, title, message, msg_type="info"):
        if not self._is_exiting: ModernMessageBox(self.root, title, message, msg_type)

    def save_new_settings(self, settings):
        self.config.update_settings(**settings)
        self.show_modern_dialog("Settings Saved", "Your settings have been saved successfully!", "success")
        self.worker.force_update()

    def open_settings(self, icon=None, item=None):
        if self._is_exiting: return
        if self.settings_window and self.settings_window.winfo_exists(): return self.settings_window.lift()
        self.settings_window = ModernSettingsWindow(self.root, self.config.get_all_settings(), self.save_new_settings)
        self.settings_window.protocol("WM_DELETE_WINDOW", self._on_settings_close)

    def _on_settings_close(self):
        if self.settings_window: self.settings_window.destroy(); self.settings_window = None
    
    def show_ip(self, icon, item):
        ip = DuckDNSClient().get_public_ip() or "Not available"
        self.root.after(0, self.show_modern_dialog, "Your Public IP", f"Your current public IP address is:\n\n{ip}", "info")

    def show_about(self, icon, item):
        about_text = f"{APP_NAME} v{APP_VERSION}\n\nA DuckDNS IP updater with a simple interface.\n\nDeveloped by thirawat27"
        self.root.after(0, self.show_modern_dialog, f"About {APP_NAME}", about_text, "info")

    def exit_app(self, icon=None, item=None):
        if self._is_exiting: return
        logging.info("Exit command received from tray."); self.root.after(0, self._safe_exit)

    def _safe_exit(self):
        if self._is_exiting: return
        self._is_exiting = True; logging.info("Executing safe exit on main thread.")
        try:
            if self.settings_window and self.settings_window.winfo_exists(): self.settings_window.destroy()
            self.worker.stop(); self.icon.stop()
            if self.root.winfo_exists(): self.root.destroy()
        except Exception as e: logging.error(f"Error during safe exit: {e}"); sys.exit(1)

# --- Program Entry Point ---
def show_warning_message(title, message):
    temp_root = tk.Tk(); temp_root.withdraw(); messagebox.showwarning(title, message); temp_root.destroy()

if __name__ == "__main__":
    lock_path = os.path.join(os.path.expanduser("~"), "duckdns_connector.lock") # REBRAND lock file
    lock = FileLock(lock_path, timeout=1)

    try:
        lock.acquire(timeout=0)
        setup_logging()
        app = DuckDNSSentryApp()
        app.run()
    except Timeout:
        logging.warning("Application is already running. Exiting.")
        show_warning_message("Already Running", f"{APP_NAME} is already running.\nCheck the system tray.")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}", exc_info=True)
        show_warning_message("Application Error", f"An unexpected error occurred. Please check the log file for details.\n\nError: {e}")
        sys.exit(1)
    finally:
        try: lock.release()
        except: pass