import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import os
import threading
from qr_builder import build_qr

BG = "#1e1e2e"
PANEL = "#313244"
TEXT = "#cdd6f4"
MUTED = "#a6adc8"
DIM = "#6c7086"
ACCENT = "#89b4fa"
GREEN = "#a6e3a1"
SURFACE = "#585b70"
RED = "#f38ba8"
YELLOW = "#f9e2af"


class QRGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.qr_color = "#000000"
        self.bg_color = "#ffffff"
        self.logo_path = None
        self.qr_image = None
        self.output_folder = None

        self._build_layout()

    def _build_layout(self):
        tk.Label(self.root, text="QR Code Generator", font=("Segoe UI", 20, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(20, 5))

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=20)

        left = tk.Frame(main, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right = tk.Frame(main, bg=PANEL)
        right.pack(side="right", padx=(10, 0), pady=10)

        self._build_left(left)
        self._build_right(right)

    # ── Left panel ──────────────────────────────────────────────────────────

    def _build_left(self, parent):
        self._build_folder_picker(parent)
        self._section_label(parent, "Text or URL", pady=(12, 2))
        self.text_input = tk.Text(parent, height=4, font=("Segoe UI", 10),
                                  bg=PANEL, fg=TEXT, insertbackground="white",
                                  relief="flat", padx=8, pady=8)
        self.text_input.pack(fill="x")

        self._build_colors(parent)
        self._build_logo(parent)
        self._build_error_correction(parent)
        self._build_buttons(parent)

    def _build_folder_picker(self, parent):
        self._section_label(parent, "Output Folder", pady=(10, 2))
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x")

        self.folder_label = tk.Label(row, text="No folder selected", font=("Segoe UI", 9),
                                     bg=BG, fg=RED, anchor="w")
        self.folder_label.pack(side="left", fill="x", expand=True)

        tk.Button(row, text="Choose Folder", font=("Segoe UI", 9), bg=SURFACE, fg=TEXT,
                  relief="flat", padx=10, cursor="hand2",
                  command=self._pick_folder).pack(side="right")

    def _build_colors(self, parent):
        self._section_label(parent, "Colors", pady=(12, 2))
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x")
        self._color_swatch(row, "QR Color", self._pick_qr_color, "qr_swatch", self.qr_color)
        self._color_swatch(row, "Background", self._pick_bg_color, "bg_swatch", self.bg_color, padx=(16, 0))

    def _build_logo(self, parent):
        self._section_label(parent, "Embed Logo (optional)", pady=(16, 2))
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x")

        self.logo_label = tk.Label(row, text="No file selected", font=("Segoe UI", 9),
                                   bg=BG, fg=DIM)
        self.logo_label.pack(side="left", fill="x", expand=True)

        tk.Button(row, text="Clear", font=("Segoe UI", 9), bg=PANEL, fg=RED,
                  relief="flat", padx=10, cursor="hand2",
                  command=self._clear_logo).pack(side="right", padx=(0, 6))
        tk.Button(row, text="Browse", font=("Segoe UI", 9), bg=SURFACE, fg=TEXT,
                  relief="flat", padx=10, cursor="hand2",
                  command=self._pick_logo).pack(side="right")

    def _build_error_correction(self, parent):
        self._section_label(parent, "Scan Quality", pady=(16, 2))
        self.ec_var = tk.StringVar(value="H")
        row = tk.Frame(parent, bg=BG)
        row.pack(anchor="w")
        for label, val in [("Low", "L"), ("Medium", "M"), ("High", "Q"), ("Max", "H")]:
            tk.Radiobutton(row, text=label, variable=self.ec_var, value=val,
                           bg=BG, fg=TEXT, selectcolor=PANEL,
                           activebackground=BG, font=("Segoe UI", 9)).pack(side="left", padx=4)

    def _build_buttons(self, parent):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", pady=(20, 0))

        self.gen_btn = tk.Button(row, text="Generate QR", font=("Segoe UI", 11, "bold"),
                                 bg=ACCENT, fg=BG, relief="flat", padx=16, pady=8,
                                 cursor="hand2", command=self._on_generate)
        self.gen_btn.pack(side="left")

        self.status_label = tk.Label(row, text="", font=("Segoe UI", 9),
                                     bg=BG, fg=YELLOW)
        self.status_label.pack(side="left", padx=(12, 0))

    # ── Right panel ──────────────────────────────────────────────────────────

    def _build_right(self, parent):
        tk.Label(parent, text="Preview", font=("Segoe UI", 10, "bold"),
                 bg=PANEL, fg=MUTED).pack(pady=(12, 4))

        self.preview_label = tk.Label(parent, bg=PANEL, width=28, height=14)
        self.preview_label.pack(padx=16, pady=(0, 16))

        placeholder = Image.new("RGB", (220, 220), "#45475a")
        photo = ImageTk.PhotoImage(placeholder)
        self.preview_label.configure(image=photo)
        self.preview_label.image = photo

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _section_label(self, parent, text, pady=(10, 2)):
        tk.Label(parent, text=text, font=("Segoe UI", 10, "bold"),
                 bg=BG, fg=MUTED).pack(anchor="w", pady=pady)

    def _color_swatch(self, parent, label, command, attr, color, padx=0):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(side="left", padx=padx)
        tk.Label(frame, text=label, font=("Segoe UI", 9, "bold"),
                 bg=BG, fg=MUTED).pack(anchor="w")
        btn = tk.Button(frame, width=6, bg=color, relief="flat",
                        cursor="hand2", command=command)
        btn.pack(anchor="w", pady=2)
        setattr(self, attr, btn)

    def _set_loading(self, loading):
        if loading:
            self.gen_btn.configure(state="disabled", text="Generating...", bg=SURFACE)
            self.status_label.configure(text="Please wait...")
        else:
            self.gen_btn.configure(state="normal", text="Generate QR", bg=ACCENT)
            self.status_label.configure(text="")

    # ── Event handlers ───────────────────────────────────────────────────────

    def _pick_folder(self):
        folder = filedialog.askdirectory(title="Choose Output Folder")
        if folder:
            self.output_folder = folder
            short = folder if len(folder) <= 40 else "..." + folder[-37:]
            self.folder_label.configure(text=short, fg=GREEN)

    def _pick_qr_color(self):
        color = colorchooser.askcolor(color=self.qr_color, title="Pick QR Color")[1]
        if color:
            self.qr_color = color
            self.qr_swatch.configure(bg=color)

    def _pick_bg_color(self):
        color = colorchooser.askcolor(color=self.bg_color, title="Pick Background Color")[1]
        if color:
            self.bg_color = color
            self.bg_swatch.configure(bg=color)

    def _pick_logo(self):
        path = filedialog.askopenfilename(
            title="Select Logo Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.ico")]
        )
        if path:
            self.logo_path = path
            self.logo_label.configure(text=os.path.basename(path), fg=TEXT)

    def _clear_logo(self):
        self.logo_path = None
        self.logo_label.configure(text="No file selected", fg=DIM)

    def _on_generate(self):
        if not self.output_folder:
            messagebox.showwarning("No Folder", "Please choose an output folder first.")
            return

        data = self.text_input.get("1.0", "end").strip()
        if not data:
            messagebox.showwarning("Empty Input", "Please enter text or a URL.")
            return

        self._set_loading(True)
        threading.Thread(target=self._generate_worker, args=(data,), daemon=True).start()

    def _generate_worker(self, data):
        try:
            img = build_qr(data, self.qr_color, self.bg_color,
                           self.ec_var.get(), self.logo_path)
            self.root.after(0, self._on_done, img)
        except Exception as e:
            self.root.after(0, self._on_error, str(e))

    def _on_done(self, img):
        self.qr_image = img

        preview = img.copy().convert("RGB")
        preview.thumbnail((220, 220))
        photo = ImageTk.PhotoImage(preview)
        self.preview_label.configure(image=photo)
        self.preview_label.image = photo

        out_path = os.path.join(self.output_folder, "qrcode.png")
        self.qr_image.convert("RGB").save(out_path)
        os.startfile(out_path)

        self._set_loading(False)

    def _on_error(self, message):
        self._set_loading(False)
        messagebox.showerror("Error", f"Failed to generate QR code:\n{message}")
