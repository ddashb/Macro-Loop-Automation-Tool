# =============================================================================
# Macro Loop Automation Tool v1.0 by David Tan
# =============================================================================
# Setup:
#   pip install -r requirements.txt
#
# Tesseract OCR (free, required for OCR step):
#   Download from: https://github.com/UB-Mannheim/tesseract/wiki
#   Install, then if it's not found automatically, uncomment the line below
#   and set the path to where you installed it:
#
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r"C:\Users\david\AppData\Local\Programs\Tesseract-OCR"
#
# Run:
#   python app.py
# =============================================================================

import csv
import json
import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pyautogui
try:
    import pydirectinput
except ImportError:
    pydirectinput = None
try:
    import win32api, win32con
except ImportError:
    win32api = None
    win32con = None
import pytesseract
import ttkbootstrap as tb
from ttkbootstrap.constants import DANGER, PRIMARY, SECONDARY, SUCCESS
from PIL import Image, ImageEnhance, ImageTk

# Fix blurry GUI and wrong mouse coordinates on high-DPI Windows displays
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

# Uncomment if Tesseract is not in your PATH:
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\david\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

def _preprocess_for_ocr(img: Image.Image) -> Image.Image:
    from PIL import ImageFilter
    w, h = img.size
    img = img.resize((w * 3, h * 3), Image.LANCZOS)
    img = img.convert("L")
    img = ImageEnhance.Contrast(img).enhance(2.5)
    img = img.filter(ImageFilter.MedianFilter(3))  # smooth rendering artifacts before threshold
    img = img.point(lambda p: 255 if p > 140 else 0)
    return img


def _clean_ocr_text(text: str) -> str:
    import re
    # Fix UTF-8 bytes misread as Latin-1 (e.g. â€˜ → ')
    try:
        text = text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    # Drop lines that are pure noise (fewer than 3 real letters)
    lines = [ln for ln in text.splitlines() if len(re.sub(r"[^a-zA-Z]", "", ln)) >= 3]
    return "\n".join(lines).strip()


# Darkly theme palette (used to manually style tk.Listbox)
_DARK_BG   = "#2b3035"
_DARK_FG   = "#adb5bd"
_SELECT_BG = "#375a7f"


class MacroApp:
    def __init__(self, root: tb.Window):
        self.root = root
        self.root.title("Macro Loop Automation Tool")
        self.root.minsize(700, 480)

        # --- App state ---
        self.actions: list[dict] = []
        self.stop_flag = threading.Event()
        self.screenshot_counter = 0
        self._run_thread: threading.Thread | None = None
        self._editing_index: int | None = None
        self._drag_start_index: int | None = None

        # --- Input StringVars ---
        self.game_mode_var = tk.BooleanVar(value=False)
        self.loop_count_var = tk.StringVar(value="1")
        self.action_type_var = tk.StringVar(value="Left Click")
        self.click_x = tk.StringVar()
        self.click_y = tk.StringVar()
        self.wait_seconds = tk.StringVar(value="1.0")
        self.ss_x1 = tk.StringVar()
        self.ss_y1 = tk.StringVar()
        self.ss_x2 = tk.StringVar()
        self.ss_y2 = tk.StringVar()
        self.rclick_x = tk.StringVar()
        self.rclick_y = tk.StringVar()
        self.key_name = tk.StringVar()
        self.combo_keys = tk.StringVar()
        self.scroll_x = tk.StringVar()
        self.scroll_y = tk.StringVar()
        self.scroll_amount = tk.StringVar(value="3")
        self.hold_x = tk.StringVar()
        self.hold_y = tk.StringVar()
        self.hold_seconds = tk.StringVar(value="1.0")
        self.auto_wait_var = tk.BooleanVar(value=True)
        self._last_wait_seconds = "1.0"

        self._build_ui()

    # =========================================================================
    # UI Construction
    # =========================================================================

    def _build_ui(self):
        # Toolbar
        toolbar = ttk.Frame(self.root, padding=(6, 4))
        toolbar.pack(side=tk.TOP, fill=tk.X)
        self._build_toolbar(toolbar)

        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X)

        # Middle area
        middle = ttk.Frame(self.root, padding=8)
        middle.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        builder_frame = ttk.LabelFrame(middle, text="Action Builder", padding=8)
        builder_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        self._build_action_builder(builder_frame)

        list_frame = ttk.LabelFrame(middle, text="Actions", padding=8)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._build_action_list(list_frame)

        # Status bar
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X)
        self.status_var = tk.StringVar(value="Ready.")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            anchor=tk.W,
            padding=(8, 4),
            bootstyle="inverse-secondary",
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _build_toolbar(self, parent: ttk.Frame):
        btn_opts = {"padx": 4, "side": tk.LEFT}

        ttk.Button(parent, text="New Loop", bootstyle=SECONDARY, command=self.new_loop).pack(**btn_opts)
        ttk.Button(parent, text="Save Loop", bootstyle=SECONDARY, command=self.save_loop).pack(**btn_opts)
        ttk.Button(parent, text="Load Loop", bootstyle=SECONDARY, command=self.load_loop).pack(**btn_opts)

        ttk.Separator(parent, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=4)

        ttk.Label(parent, text="Loop Count:").pack(side=tk.LEFT)
        ttk.Entry(parent, textvariable=self.loop_count_var, width=5).pack(
            side=tk.LEFT, padx=(4, 12)
        )

        self.run_btn = ttk.Button(
            parent, text="Run Loop", bootstyle=SUCCESS, command=self.run_loop
        )
        self.run_btn.pack(**btn_opts)

        ttk.Button(parent, text="Stop", bootstyle=DANGER, command=self.stop_loop).pack(**btn_opts)

        ttk.Separator(parent, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=4)

        game_cb = ttk.Checkbutton(
            parent, text="Game Mode", variable=self.game_mode_var, bootstyle="warning-round-toggle"
        )
        if pydirectinput is None:
            game_cb.config(state=tk.DISABLED)
        game_cb.pack(side=tk.LEFT, padx=4)

    def _build_action_builder(self, parent: ttk.Frame):
        # Action type dropdown (Combobox instead of OptionMenu)
        ttk.Label(parent, text="Action Type:").grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 4)
        )
        action_types = ["Left Click", "Right Click", "Click & Hold", "Mouseover",
                        "Key Press", "Key Combo", "Scroll", "Wait", "Screenshot"]
        combo = ttk.Combobox(
            parent,
            textvariable=self.action_type_var,
            values=action_types,
            state="readonly",
            width=14,
        )
        combo.bind("<<ComboboxSelected>>", self._on_type_change)
        combo.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 8))

        # --- Left Click fields ---
        self.click_frame = ttk.Frame(parent)
        ttk.Label(self.click_frame, text="X:").grid(row=0, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.click_frame, textvariable=self.click_x, width=8).grid(row=0, column=1, pady=3)
        ttk.Label(self.click_frame, text="Y:").grid(row=1, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.click_frame, textvariable=self.click_y, width=8).grid(row=1, column=1, pady=3)

        # --- Mouseover fields ---
        self.hover_x = tk.StringVar()
        self.hover_y = tk.StringVar()
        self.hover_frame = ttk.Frame(parent)
        ttk.Label(self.hover_frame, text="X:").grid(row=0, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.hover_frame, textvariable=self.hover_x, width=8).grid(row=0, column=1, pady=3)
        ttk.Label(self.hover_frame, text="Y:").grid(row=1, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.hover_frame, textvariable=self.hover_y, width=8).grid(row=1, column=1, pady=3)

        # --- Wait fields ---
        self.wait_frame = ttk.Frame(parent)
        ttk.Label(self.wait_frame, text="Seconds:").grid(row=0, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.wait_frame, textvariable=self.wait_seconds, width=8).grid(row=0, column=1, pady=3)

        # --- Screenshot fields ---
        self.screenshot_frame = ttk.Frame(parent)
        for i, (lbl, var) in enumerate(
            [("X1:", self.ss_x1), ("Y1:", self.ss_y1), ("X2:", self.ss_x2), ("Y2:", self.ss_y2)]
        ):
            ttk.Label(self.screenshot_frame, text=lbl).grid(row=i, column=0, sticky=tk.E, padx=(0, 4))
            ttk.Entry(self.screenshot_frame, textvariable=var, width=8).grid(row=i, column=1, pady=3)
        ttk.Button(
            self.screenshot_frame, text="Pick Area", bootstyle=SECONDARY, command=self.pick_area
        ).grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(8, 0))

        # --- Right Click fields ---
        self.rclick_frame = ttk.Frame(parent)
        ttk.Label(self.rclick_frame, text="X:").grid(row=0, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.rclick_frame, textvariable=self.rclick_x, width=8).grid(row=0, column=1, pady=3)
        ttk.Label(self.rclick_frame, text="Y:").grid(row=1, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.rclick_frame, textvariable=self.rclick_y, width=8).grid(row=1, column=1, pady=3)

        # --- Click & Hold fields ---
        self.hold_frame = ttk.Frame(parent)
        ttk.Label(self.hold_frame, text="X:").grid(row=0, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.hold_frame, textvariable=self.hold_x, width=8).grid(row=0, column=1, pady=3)
        ttk.Label(self.hold_frame, text="Y:").grid(row=1, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.hold_frame, textvariable=self.hold_y, width=8).grid(row=1, column=1, pady=3)
        ttk.Label(self.hold_frame, text="Hold (s):").grid(row=2, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.hold_frame, textvariable=self.hold_seconds, width=8).grid(row=2, column=1, pady=3)

        # --- Key Press fields ---
        self.key_frame = ttk.Frame(parent)
        ttk.Label(self.key_frame, text="Key:").grid(row=0, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.key_frame, textvariable=self.key_name, width=12).grid(row=0, column=1, pady=3)
        ttk.Label(self.key_frame, text="e.g. enter, f5, space", foreground="#6c757d").grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 3))

        # --- Key Combo fields ---
        self.combo_frame = ttk.Frame(parent)
        ttk.Label(self.combo_frame, text="Keys:").grid(row=0, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.combo_frame, textvariable=self.combo_keys, width=12).grid(row=0, column=1, pady=3)
        ttk.Label(self.combo_frame, text="e.g. ctrl,c  or  win,r", foreground="#6c757d").grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 3))

        # --- Scroll fields ---
        self.scroll_frame = ttk.Frame(parent)
        ttk.Label(self.scroll_frame, text="X:").grid(row=0, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.scroll_frame, textvariable=self.scroll_x, width=8).grid(row=0, column=1, pady=3)
        ttk.Label(self.scroll_frame, text="Y:").grid(row=1, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.scroll_frame, textvariable=self.scroll_y, width=8).grid(row=1, column=1, pady=3)
        ttk.Label(self.scroll_frame, text="Amount:").grid(row=2, column=0, sticky=tk.E, padx=(0, 4))
        ttk.Entry(self.scroll_frame, textvariable=self.scroll_amount, width=8).grid(row=2, column=1, pady=3)
        ttk.Label(self.scroll_frame, text="+up / −down", foreground="#6c757d").grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 3))

        # Show the default (Left Click) panel
        self.click_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self._current_field_frame = self.click_frame

        # Buttons
        ttk.Button(parent, text="Get Mouse Pos", bootstyle=SECONDARY, command=self.get_mouse_pos).grid(
            row=3, column=0, columnspan=2, sticky=tk.EW, pady=(12, 3)
        )
        ttk.Button(parent, text="Preview Pos", bootstyle=SECONDARY, command=self.preview_pos).grid(
            row=4, column=0, columnspan=2, sticky=tk.EW, pady=3
        )
        self.add_btn_text = tk.StringVar(value="Add Action")
        self.add_btn = ttk.Button(
            parent, textvariable=self.add_btn_text, bootstyle=PRIMARY, command=self.add_action
        )
        self.add_btn.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(10, 3))
        ttk.Checkbutton(
            parent, text="Auto-wait after action",
            variable=self.auto_wait_var, bootstyle="secondary-round-toggle"
        ).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(4, 0))

    def _build_action_list(self, parent: ttk.Frame):
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(
            parent,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            font=("Consolas", 10),
            activestyle="none",
            bg=_DARK_BG,
            fg=_DARK_FG,
            selectbackground=_SELECT_BG,
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            relief=tk.FLAT,
        )
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.listbox.bind("<Double-Button-1>", self._load_action_for_edit)
        self.listbox.bind("<ButtonPress-1>",   self._drag_start)
        self.listbox.bind("<B1-Motion>",       self._drag_motion)
        self.listbox.bind("<ButtonRelease-1>", self._drag_release)

        ttk.Button(
            parent, text="Remove Selected", bootstyle=(DANGER, "outline"), command=self.remove_selected
        ).pack(side=tk.BOTTOM, fill=tk.X, pady=(8, 0))

    # =========================================================================
    # Dynamic field switching
    # =========================================================================

    def _on_type_change(self, _=None):
        self._current_field_frame.grid_forget()
        action_type = self.action_type_var.get()
        frame_map = {
            "Left Click": self.click_frame,
            "Right Click": self.rclick_frame,
            "Click & Hold": self.hold_frame,
            "Mouseover": self.hover_frame,
            "Key Press": self.key_frame,
            "Key Combo": self.combo_frame,
            "Scroll": self.scroll_frame,
            "Wait": self.wait_frame,
            "Screenshot": self.screenshot_frame,
        }
        self._current_field_frame = frame_map[action_type]
        self._current_field_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W)

    # =========================================================================
    # Toolbar / action callbacks
    # =========================================================================

    def new_loop(self):
        self.actions.clear()
        self._refresh_listbox()
        self._set_status("Loop cleared.")

    def add_action(self):
        action_type = self.action_type_var.get()
        try:
            if action_type == "Left Click":
                x = self._validate_int(self.click_x.get(), "X")
                y = self._validate_int(self.click_y.get(), "Y")
                action = {"type": "click", "x": x, "y": y}

            elif action_type == "Mouseover":
                x = self._validate_int(self.hover_x.get(), "X")
                y = self._validate_int(self.hover_y.get(), "Y")
                action = {"type": "mouseover", "x": x, "y": y}

            elif action_type == "Wait":
                s = self._validate_float(self.wait_seconds.get(), "Seconds")
                if s <= 0:
                    raise ValueError("Seconds must be greater than 0.")
                action = {"type": "wait", "seconds": s}
                self._last_wait_seconds = self.wait_seconds.get()

            elif action_type == "Right Click":
                x = self._validate_int(self.rclick_x.get(), "X")
                y = self._validate_int(self.rclick_y.get(), "Y")
                action = {"type": "right_click", "x": x, "y": y}

            elif action_type == "Click & Hold":
                x = self._validate_int(self.hold_x.get(), "X")
                y = self._validate_int(self.hold_y.get(), "Y")
                s = self._validate_float(self.hold_seconds.get(), "Seconds")
                if s <= 0:
                    raise ValueError("Seconds must be greater than 0.")
                action = {"type": "click_hold", "x": x, "y": y, "seconds": s}

            elif action_type == "Key Press":
                key = self.key_name.get().strip()
                if not key:
                    raise ValueError("Key name cannot be empty.")
                action = {"type": "key_press", "key": key}

            elif action_type == "Key Combo":
                raw = self.combo_keys.get().strip()
                keys = [k.strip() for k in raw.split(",") if k.strip()]
                if len(keys) < 2:
                    raise ValueError("Enter at least 2 comma-separated keys (e.g. ctrl,c).")
                action = {"type": "key_combo", "keys": keys}

            elif action_type == "Scroll":
                x = self._validate_int(self.scroll_x.get(), "X")
                y = self._validate_int(self.scroll_y.get(), "Y")
                amount = self._validate_int(self.scroll_amount.get(), "Amount")
                if amount == 0:
                    raise ValueError("Amount cannot be 0.")
                action = {"type": "scroll", "x": x, "y": y, "amount": amount}

            elif action_type == "Screenshot":
                x1 = self._validate_int(self.ss_x1.get(), "X1")
                y1 = self._validate_int(self.ss_y1.get(), "Y1")
                x2 = self._validate_int(self.ss_x2.get(), "X2")
                y2 = self._validate_int(self.ss_y2.get(), "Y2")
                if x2 <= x1:
                    raise ValueError("X2 must be greater than X1.")
                if y2 <= y1:
                    raise ValueError("Y2 must be greater than Y1.")
                action = {"type": "screenshot", "x1": x1, "y1": y1, "x2": x2, "y2": y2}

            else:
                return

        except ValueError as e:
            self._set_status(f"Error: {e}")
            return

        if self._editing_index is not None:
            self.actions[self._editing_index] = action
            idx = self._editing_index
            self._editing_index = None
            self.add_btn_text.set("Add Action")
            self._refresh_listbox()
            self.listbox.selection_set(idx)
            self._set_status(f"Updated action {idx + 1}: {self._action_label(action)}")
        else:
            self.actions.append(action)
            if self.auto_wait_var.get() and action["type"] != "wait":
                wait_val = float(self._last_wait_seconds)
                self.actions.append({"type": "wait", "seconds": wait_val})
            self._refresh_listbox()
            self._set_status(f"Added: {self._action_label(action)}")

    def remove_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            self._set_status("No action selected.")
            return
        idx = sel[0]
        removed = self.actions.pop(idx)
        self._refresh_listbox()
        self._set_status(f"Removed: {self._action_label(removed)}")

    def save_loop(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Loop",
        )
        if not path:
            return
        try:
            loop_count = int(self.loop_count_var.get())
        except ValueError:
            loop_count = 1
        data = {"actions": self.actions, "loop_count": loop_count}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        self._set_status(f"Saved to {os.path.basename(path)}")

    def load_loop(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Loop",
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.actions = data.get("actions", [])
            self.loop_count_var.set(str(data.get("loop_count", 1)))
            self._refresh_listbox()
            self._set_status(f"Loaded {len(self.actions)} action(s) from {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load file:\n{e}")

    def run_loop(self):
        if not self.actions:
            self._set_status("Error: No actions to run. Add actions first.")
            return
        try:
            loop_count = int(self.loop_count_var.get())
            if loop_count < 1:
                raise ValueError
        except ValueError:
            self._set_status("Error: Loop Count must be a positive integer.")
            return

        self.screenshot_counter = self._get_max_screenshot_number()
        self.stop_flag.clear()
        self.run_btn.config(state=tk.DISABLED)
        self._run_thread = threading.Thread(
            target=self._run_worker, args=(loop_count,), daemon=True
        )
        self._run_thread.start()

    def stop_loop(self):
        self.stop_flag.set()
        self._set_status("Stopping...")

    # =========================================================================
    # Mouse position helpers
    # =========================================================================

    def get_mouse_pos(self):
        """Countdown 3s then capture mouse position into X/Y fields."""
        threading.Thread(target=self._countdown_and_capture, daemon=True).start()

    def _countdown_and_capture(self):
        for i in [2, 1]:
            self.root.after(0, lambda i=i: self._set_status(f"Hover mouse over target... capturing in {i}s"))
            time.sleep(1)
        pos = pyautogui.position()
        action_type = self.action_type_var.get()
        coord_map = {
            "Mouseover":     (self.hover_x,   self.hover_y),
            "Right Click":   (self.rclick_x,  self.rclick_y),
            "Click & Hold":  (self.hold_x,    self.hold_y),
            "Scroll":        (self.scroll_x,  self.scroll_y),
        }
        x_var, y_var = coord_map.get(action_type, (self.click_x, self.click_y))
        self.root.after(0, lambda: x_var.set(str(pos.x)))
        self.root.after(0, lambda: y_var.set(str(pos.y)))
        self.root.after(0, lambda: self._set_status(f"Captured position: ({pos.x}, {pos.y})"))

    def preview_pos(self):
        """Move mouse to the X/Y coords currently in the active action fields."""
        action_type = self.action_type_var.get()
        if action_type == "Mouseover":
            x_var, y_var = self.hover_x, self.hover_y
        else:
            x_var, y_var = self.click_x, self.click_y
        try:
            x = self._validate_int(x_var.get(), "X")
            y = self._validate_int(y_var.get(), "Y")
        except ValueError as e:
            self._set_status(f"Error: {e}")
            return
        pyautogui.moveTo(x, y)
        self._set_status(f"Mouse moved to ({x}, {y})")

    def pick_area(self):
        """Hide the app, freeze the screen, let the user drag-select a region."""
        self.root.withdraw()
        time.sleep(0.2)  # Wait for main window to disappear before screenshot

        screen_img = pyautogui.screenshot()
        screen_w, screen_h = screen_img.size

        overlay = tk.Toplevel()
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-topmost', True)
        overlay.lift()
        overlay.focus_force()

        tk_img = ImageTk.PhotoImage(screen_img)

        canvas = tk.Canvas(overlay, cursor='cross', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
        canvas.image = tk_img  # Prevent garbage collection

        # Semi-transparent instruction banner
        canvas.create_rectangle(
            screen_w // 2 - 280, 8, screen_w // 2 + 280, 52,
            fill='black', stipple='gray50', outline='',
        )
        canvas.create_text(
            screen_w // 2, 30,
            text="Click and drag to select area   |   Escape to cancel",
            fill='yellow', font=('Arial', 14, 'bold'),
        )

        state = {'start_x': 0, 'start_y': 0, 'rect': None}

        def on_press(event):
            state['start_x'] = event.x
            state['start_y'] = event.y
            if state['rect']:
                canvas.delete(state['rect'])
            state['rect'] = canvas.create_rectangle(
                event.x, event.y, event.x, event.y,
                outline='red', width=2, dash=(4, 2),
            )

        def on_drag(event):
            if state['rect']:
                canvas.coords(state['rect'], state['start_x'], state['start_y'], event.x, event.y)

        def on_release(event):
            x1 = min(state['start_x'], event.x)
            y1 = min(state['start_y'], event.y)
            x2 = max(state['start_x'], event.x)
            y2 = max(state['start_y'], event.y)
            overlay.destroy()
            self.root.deiconify()
            self.root.lift()
            if x2 - x1 > 5 and y2 - y1 > 5:
                self.ss_x1.set(str(x1))
                self.ss_y1.set(str(y1))
                self.ss_x2.set(str(x2))
                self.ss_y2.set(str(y2))
                self._set_status(f"Area selected: ({x1},{y1}) → ({x2},{y2})")
            else:
                self._set_status("Selection too small — try again.")

        def on_cancel(event):
            overlay.destroy()
            self.root.deiconify()
            self.root.lift()
            self._set_status("Area selection cancelled.")

        canvas.bind('<ButtonPress-1>', on_press)
        canvas.bind('<B1-Motion>', on_drag)
        canvas.bind('<ButtonRelease-1>', on_release)
        overlay.bind('<Escape>', on_cancel)

    # =========================================================================
    # Run worker (background thread)
    # =========================================================================

    def _run_worker(self, loop_count: int):
        os.makedirs("./screenshots", exist_ok=True)
        try:
            for i in range(loop_count):
                if self.stop_flag.is_set():
                    break
                self.root.after(0, lambda i=i: self._set_status(f"Running loop {i + 1} of {loop_count}..."))
                for action in self.actions:
                    if self.stop_flag.is_set():
                        break
                    self._execute_action(action)

        except pyautogui.FailSafeException:
            self.root.after(0, lambda: self._set_status(
                "Stopped: mouse hit top-left corner (failsafe triggered)."
            ))
            self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL))
            return
        except Exception as e:
            self.root.after(0, lambda e=e: self._set_status(f"Error during run: {e}"))
            self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL))
            return

        if self.stop_flag.is_set():
            self.root.after(0, lambda: self._set_status("Loop stopped by user."))
            self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL))
            return

        # Auto-run OCR after all loops finish
        self.root.after(0, lambda: self._set_status("Loops done. Running OCR on screenshots..."))
        self._run_ocr_on_screenshots()
        self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL))

    def _execute_action(self, action: dict):
        t = action["type"]
        game_mode = self.game_mode_var.get() and pydirectinput is not None
        if t == "click":
            if game_mode:
                pydirectinput.moveTo(action["x"], action["y"])
                time.sleep(0.05)
                if win32api:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    time.sleep(0.02)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                else:
                    pydirectinput.click(action["x"], action["y"])
            else:
                pyautogui.click(action["x"], action["y"])
        elif t == "mouseover":
            if game_mode:
                pydirectinput.moveTo(action["x"], action["y"])
            else:
                pyautogui.moveTo(action["x"], action["y"])
        elif t == "wait":
            # Sleep in small increments so stop_flag is checked more often
            end = time.time() + action["seconds"]
            while time.time() < end:
                if self.stop_flag.is_set():
                    return
                time.sleep(0.05)
        elif t == "screenshot":
            x1, y1, x2, y2 = action["x1"], action["y1"], action["x2"], action["y2"]
            w = x2 - x1
            h = y2 - y1
            self.screenshot_counter += 1
            path = f"./screenshots/{self.screenshot_counter}.png"
            img = pyautogui.screenshot(region=(x1, y1, w, h))
            img.save(path)
        elif t == "right_click":
            if game_mode:
                pydirectinput.moveTo(action["x"], action["y"])
                time.sleep(0.05)
                if win32api:
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                    time.sleep(0.02)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                else:
                    pydirectinput.rightClick(action["x"], action["y"])
            else:
                pyautogui.rightClick(action["x"], action["y"])
        elif t == "click_hold":
            if game_mode and win32api:
                pydirectinput.moveTo(action["x"], action["y"])
                time.sleep(0.05)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                end = time.time() + action["seconds"]
                while time.time() < end:
                    if self.stop_flag.is_set():
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        return
                    time.sleep(0.05)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            else:
                pyautogui.mouseDown(action["x"], action["y"])
                end = time.time() + action["seconds"]
                while time.time() < end:
                    if self.stop_flag.is_set():
                        pyautogui.mouseUp()
                        return
                    time.sleep(0.05)
                pyautogui.mouseUp()
        elif t == "key_press":
            if game_mode:
                pydirectinput.press(action["key"])
            else:
                pyautogui.press(action["key"])
        elif t == "key_combo":
            keys = action["keys"]
            if game_mode:
                for k in keys:
                    pydirectinput.keyDown(k)
                for k in reversed(keys):
                    pydirectinput.keyUp(k)
            else:
                pyautogui.hotkey(*keys)
        elif t == "scroll":
            x, y, amount = action["x"], action["y"], action["amount"]
            if game_mode and win32api:
                win32api.SetCursorPos((x, y))
                time.sleep(0.05)
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, amount * 120, 0)
            else:
                pyautogui.scroll(amount, x=x, y=y)

    # =========================================================================
    # OCR + CSV
    # =========================================================================

    def _run_ocr_on_screenshots(self):
        folder = "./screenshots"
        try:
            pngs = sorted(
                [f for f in os.listdir(folder) if f.endswith(".png")],
                key=lambda f: int(os.path.splitext(f)[0]),
            )
        except Exception as e:
            self.root.after(0, lambda e=e: self._set_status(f"OCR error listing files: {e}"))
            return

        if not pngs:
            self.root.after(0, lambda: self._set_status("No screenshots found for OCR."))
            return

        # Skip files already recorded in results.csv so resumed runs don't re-process old screenshots
        csv_path = "results.csv"
        already_done: set[str] = set()
        csv_exists = os.path.exists(csv_path)
        if csv_exists:
            try:
                with open(csv_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    next(reader, None)  # skip header
                    for row in reader:
                        if row:
                            already_done.add(row[0])
            except Exception:
                pass

        new_pngs = [f for f in pngs if f not in already_done]
        if not new_pngs:
            self.root.after(0, lambda: self._set_status("No new screenshots to process."))
            return

        rows = []
        try:
            for fname in new_pngs:
                img = Image.open(os.path.join(folder, fname))
                img = _preprocess_for_ocr(img)
                text = _clean_ocr_text(pytesseract.image_to_string(img, config="--psm 6"))
                rows.append([fname, text])
        except Exception as e:
            msg = (
                f"OCR error: {e}\n\n"
                "Screenshots were saved, but no results.csv was written.\n"
                "Make sure Tesseract is installed and in your PATH (or set tesseract_cmd at the top of app.py)."
            )
            self.root.after(0, lambda msg=msg: self._set_status(
                "OCR failed. Screenshots saved. See console for details."
            ))
            print(msg)
            return

        try:
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not csv_exists:
                    writer.writerow(["image_file", "extracted_text"])
                writer.writerows(rows)
            self.root.after(0, lambda: self._set_status(
                f"Done. {len(rows)} screenshot(s) processed. results.csv updated."
            ))
        except Exception as e:
            self.root.after(0, lambda e=e: self._set_status(f"Could not write results.csv: {e}"))

    # =========================================================================
    # Edit & drag-reorder
    # =========================================================================

    def _load_action_for_edit(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if not (0 <= idx < len(self.actions)):
            return
        if self._editing_index == idx:
            self._editing_index = None
            self.add_btn_text.set("Add Action")
            self._set_status("Edit cancelled.")
            return
        action = self.actions[idx]
        t = action["type"]
        type_map = {
            "click": "Left Click", "right_click": "Right Click", "click_hold": "Click & Hold",
            "mouseover": "Mouseover", "key_press": "Key Press", "key_combo": "Key Combo",
            "scroll": "Scroll", "wait": "Wait", "screenshot": "Screenshot",
        }
        self.action_type_var.set(type_map.get(t, "Left Click"))
        self._on_type_change()
        if t == "click":
            self.click_x.set(str(action["x"]))
            self.click_y.set(str(action["y"]))
        elif t == "right_click":
            self.rclick_x.set(str(action["x"]))
            self.rclick_y.set(str(action["y"]))
        elif t == "click_hold":
            self.hold_x.set(str(action["x"]))
            self.hold_y.set(str(action["y"]))
            self.hold_seconds.set(str(action["seconds"]))
        elif t == "mouseover":
            self.hover_x.set(str(action["x"]))
            self.hover_y.set(str(action["y"]))
        elif t == "key_press":
            self.key_name.set(action["key"])
        elif t == "key_combo":
            self.combo_keys.set(",".join(action["keys"]))
        elif t == "scroll":
            self.scroll_x.set(str(action["x"]))
            self.scroll_y.set(str(action["y"]))
            self.scroll_amount.set(str(action["amount"]))
        elif t == "wait":
            self.wait_seconds.set(str(action["seconds"]))
        elif t == "screenshot":
            self.ss_x1.set(str(action["x1"]))
            self.ss_y1.set(str(action["y1"]))
            self.ss_x2.set(str(action["x2"]))
            self.ss_y2.set(str(action["y2"]))
        self._editing_index = idx
        self.add_btn_text.set("Update Action")
        self._set_status(f"Editing action {idx + 1} — double-click again to cancel")

    def _drag_start(self, event):
        idx = self.listbox.nearest(event.y)
        self._drag_start_index = idx if 0 <= idx < len(self.actions) else None

    def _drag_motion(self, event):
        if self._drag_start_index is None:
            return
        target = self.listbox.nearest(event.y)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(target)

    def _drag_release(self, event):
        if self._drag_start_index is None:
            return
        target = self.listbox.nearest(event.y)
        src = self._drag_start_index
        self._drag_start_index = None
        if target == src or not (0 <= target < len(self.actions)):
            return
        action = self.actions.pop(src)
        self.actions.insert(target, action)
        if self._editing_index == src:
            self._editing_index = target
        elif self._editing_index is not None:
            # adjust editing index if it shifted due to the move
            if src < self._editing_index <= target:
                self._editing_index -= 1
            elif target <= self._editing_index < src:
                self._editing_index += 1
        self._refresh_listbox()
        self.listbox.selection_set(target)
        self._set_status(f"Moved action {src + 1} → position {target + 1}")

    # =========================================================================
    # Helpers
    # =========================================================================

    def _refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for i, action in enumerate(self.actions):
            self.listbox.insert(tk.END, f"  {i + 1:>2}.  {self._action_label(action)}")

    def _action_label(self, action: dict) -> str:
        t = action["type"]
        if t == "click":
            return f"Left Click at ({action['x']}, {action['y']})"
        elif t == "right_click":
            return f"Right Click at ({action['x']}, {action['y']})"
        elif t == "click_hold":
            return f"Click & Hold at ({action['x']}, {action['y']}) for {action['seconds']}s"
        elif t == "mouseover":
            return f"Mouseover at ({action['x']}, {action['y']})"
        elif t == "key_press":
            return f"Key Press: {action['key']}"
        elif t == "key_combo":
            return f"Key Combo: {'+'.join(action['keys'])}"
        elif t == "scroll":
            direction = "up" if action["amount"] > 0 else "down"
            return f"Scroll {direction} {abs(action['amount'])} at ({action['x']}, {action['y']})"
        elif t == "wait":
            return f"Wait {action['seconds']}s"
        elif t == "screenshot":
            return f"Screenshot ({action['x1']},{action['y1']}) → ({action['x2']},{action['y2']})"
        return str(action)

    def _set_status(self, msg: str):
        """Thread-safe status bar update."""
        self.root.after(0, lambda: self.status_var.set(msg))

    def _get_max_screenshot_number(self) -> int:
        folder = "./screenshots"
        if not os.path.isdir(folder):
            return 0
        nums = [
            int(os.path.splitext(f)[0])
            for f in os.listdir(folder)
            if f.endswith(".png") and os.path.splitext(f)[0].isdigit()
        ]
        return max(nums) if nums else 0

    def _validate_int(self, value: str, field_name: str) -> int:
        value = value.strip()
        if not value:
            raise ValueError(f"{field_name} is required.")
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"{field_name} must be a whole number (got '{value}').")

    def _validate_float(self, value: str, field_name: str) -> float:
        value = value.strip()
        if not value:
            raise ValueError(f"{field_name} is required.")
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"{field_name} must be a number (got '{value}').")


# =============================================================================
# Entry point
# =============================================================================

if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = MacroApp(root)
    root.mainloop()
