import csv
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

try:
    from PIL import ImageGrab
except ImportError:
    raise ImportError("Pillow is required. Install it with: pip install pillow")


class ColorRecord:
    def __init__(self, timestamp, x, y, r, g, b, hex_value):
        self.timestamp = timestamp
        self.x = x
        self.y = y
        self.r = r
        self.g = g
        self.b = b
        self.hex_value = hex_value

    def to_list(self):
        return [
            self.timestamp,
            self.x,
            self.y,
            self.r,
            self.g,
            self.b,
            self.hex_value
        ]


class CursorColorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cursor Color Detector")
        self.root.geometry("900x680")
        self.root.minsize(820, 620)

        self.running = True
        self.history = []
        self.max_history = 500
        self.last_hex = "#000000"
        self.last_rgb = (0, 0, 0)
        self.last_position = (0, 0)
        self.last_saved_path = None

        self.refresh_rate = tk.IntVar(value=100)
        self.auto_log = tk.BooleanVar(value=False)
        self.only_log_changes = tk.BooleanVar(value=True)
        self.last_logged_hex = None

        self.configure_root()
        self.build_ui()
        self.bind_shortcuts()
        self.schedule_next_update()

    def configure_root(self):
        self.root.configure(bg="#1e1e1e")

    def build_ui(self):
        self.build_title_section()
        self.build_info_section()
        self.build_preview_section()
        self.build_controls_section()
        self.build_history_section()
        self.build_footer_section()

    def build_title_section(self):
        title_frame = tk.Frame(self.root, bg="#1e1e1e")
        title_frame.pack(fill="x", padx=16, pady=(16, 8))

        title_label = tk.Label(
            title_frame,
            text="Live Mouse Cursor Color Detector",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#1e1e1e"
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            title_frame,
            text="Tracks the color directly under your cursor and shows RGB + HEX values.",
            font=("Arial", 10),
            fg="#cfcfcf",
            bg="#1e1e1e"
        )
        subtitle_label.pack(anchor="w", pady=(4, 0))

    def build_info_section(self):
        info_frame = tk.Frame(self.root, bg="#2b2b2b", bd=1, relief="solid")
        info_frame.pack(fill="x", padx=16, pady=8)

        left_frame = tk.Frame(info_frame, bg="#2b2b2b")
        left_frame.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        self.position_label = tk.Label(
            left_frame,
            text="Position: X=0, Y=0",
            font=("Consolas", 13),
            fg="white",
            bg="#2b2b2b"
        )
        self.position_label.pack(anchor="w", pady=4)

        self.rgb_label = tk.Label(
            left_frame,
            text="RGB: (0, 0, 0)",
            font=("Consolas", 13),
            fg="white",
            bg="#2b2b2b"
        )
        self.rgb_label.pack(anchor="w", pady=4)

        self.hex_label = tk.Label(
            left_frame,
            text="HEX: #000000",
            font=("Consolas", 13, "bold"),
            fg="white",
            bg="#2b2b2b"
        )
        self.hex_label.pack(anchor="w", pady=4)

        self.time_label = tk.Label(
            left_frame,
            text="Last update: --",
            font=("Consolas", 11),
            fg="#cfcfcf",
            bg="#2b2b2b"
        )
        self.time_label.pack(anchor="w", pady=4)

        right_frame = tk.Frame(info_frame, bg="#2b2b2b")
        right_frame.pack(side="right", padx=12, pady=12)

        self.status_label = tk.Label(
            right_frame,
            text="Status: RUNNING",
            font=("Arial", 12, "bold"),
            fg="#7CFC00",
            bg="#2b2b2b"
        )
        self.status_label.pack(anchor="e", pady=4)

        self.history_count_label = tk.Label(
            right_frame,
            text="History items: 0",
            font=("Arial", 11),
            fg="white",
            bg="#2b2b2b"
        )
        self.history_count_label.pack(anchor="e", pady=4)

    def build_preview_section(self):
        preview_outer = tk.Frame(self.root, bg="#1e1e1e")
        preview_outer.pack(fill="x", padx=16, pady=8)

        preview_label = tk.Label(
            preview_outer,
            text="Current Color Preview",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#1e1e1e"
        )
        preview_label.pack(anchor="w", pady=(0, 6))

        self.preview_box = tk.Canvas(
            preview_outer,
            width=300,
            height=120,
            bg="#000000",
            highlightthickness=1,
            highlightbackground="#666666"
        )
        self.preview_box.pack(anchor="w")

    def build_controls_section(self):
        controls_frame = tk.Frame(self.root, bg="#2b2b2b", bd=1, relief="solid")
        controls_frame.pack(fill="x", padx=16, pady=8)

        buttons_row = tk.Frame(controls_frame, bg="#2b2b2b")
        buttons_row.pack(fill="x", padx=12, pady=(12, 8))

        self.toggle_button = tk.Button(
            buttons_row,
            text="Pause",
            width=12,
            command=self.toggle_running
        )
        self.toggle_button.pack(side="left", padx=4)

        add_button = tk.Button(
            buttons_row,
            text="Add to History",
            width=14,
            command=self.add_current_color_to_history
        )
        add_button.pack(side="left", padx=4)

        copy_hex_button = tk.Button(
            buttons_row,
            text="Copy HEX",
            width=12,
            command=self.copy_hex
        )
        copy_hex_button.pack(side="left", padx=4)

        copy_rgb_button = tk.Button(
            buttons_row,
            text="Copy RGB",
            width=12,
            command=self.copy_rgb
        )
        copy_rgb_button.pack(side="left", padx=4)

        save_button = tk.Button(
            buttons_row,
            text="Save History",
            width=12,
            command=self.save_history_to_csv
        )
        save_button.pack(side="left", padx=4)

        clear_button = tk.Button(
            buttons_row,
            text="Clear History",
            width=12,
            command=self.clear_history
        )
        clear_button.pack(side="left", padx=4)

        settings_row = tk.Frame(controls_frame, bg="#2b2b2b")
        settings_row.pack(fill="x", padx=12, pady=(0, 12))

        refresh_label = tk.Label(
            settings_row,
            text="Refresh rate (ms):",
            fg="white",
            bg="#2b2b2b",
            font=("Arial", 10)
        )
        refresh_label.pack(side="left", padx=(0, 6))

        refresh_box = ttk.Combobox(
            settings_row,
            textvariable=self.refresh_rate,
            values=[20, 50, 100, 150, 200, 300, 500, 1000],
            width=8,
            state="readonly"
        )
        refresh_box.pack(side="left", padx=(0, 12))

        auto_log_check = tk.Checkbutton(
            settings_row,
            text="Auto-log samples",
            variable=self.auto_log,
            fg="white",
            bg="#2b2b2b",
            selectcolor="#2b2b2b",
            activebackground="#2b2b2b",
            activeforeground="white"
        )
        auto_log_check.pack(side="left", padx=6)

        change_check = tk.Checkbutton(
            settings_row,
            text="Only log on color change",
            variable=self.only_log_changes,
            fg="white",
            bg="#2b2b2b",
            selectcolor="#2b2b2b",
            activebackground="#2b2b2b",
            activeforeground="white"
        )
        change_check.pack(side="left", padx=6)

    def build_history_section(self):
        history_outer = tk.Frame(self.root, bg="#1e1e1e")
        history_outer.pack(fill="both", expand=True, padx=16, pady=8)

        history_label = tk.Label(
            history_outer,
            text="Color History",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#1e1e1e"
        )
        history_label.pack(anchor="w", pady=(0, 6))

        list_frame = tk.Frame(history_outer, bg="#1e1e1e")
        list_frame.pack(fill="both", expand=True)

        self.history_listbox = tk.Listbox(
            list_frame,
            font=("Consolas", 10),
            bg="#111111",
            fg="white",
            selectbackground="#4444aa",
            activestyle="none"
        )
        self.history_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, command=self.history_listbox.yview)
        scrollbar.pack(side="right", fill="y")

        self.history_listbox.config(yscrollcommand=scrollbar.set)
        self.history_listbox.bind("<Double-Button-1>", self.copy_selected_hex)

    def build_footer_section(self):
        footer = tk.Frame(self.root, bg="#1e1e1e")
        footer.pack(fill="x", padx=16, pady=(0, 12))

        footer_label = tk.Label(
            footer,
            text="Shortcuts: Space = Pause/Resume | H = Add to history | C = Copy HEX | R = Copy RGB | S = Save history",
            font=("Arial", 9),
            fg="#bbbbbb",
            bg="#1e1e1e"
        )
        footer_label.pack(anchor="w")

    def bind_shortcuts(self):
        self.root.bind("<space>", lambda event: self.toggle_running())
        self.root.bind("<h>", lambda event: self.add_current_color_to_history())
        self.root.bind("<H>", lambda event: self.add_current_color_to_history())
        self.root.bind("<c>", lambda event: self.copy_hex())
        self.root.bind("<C>", lambda event: self.copy_hex())
        self.root.bind("<r>", lambda event: self.copy_rgb())
        self.root.bind("<R>", lambda event: self.copy_rgb())
        self.root.bind("<s>", lambda event: self.save_history_to_csv())
        self.root.bind("<S>", lambda event: self.save_history_to_csv())

    def schedule_next_update(self):
        delay = self.get_safe_refresh_rate()
        self.root.after(delay, self.update_color_loop)

    def get_safe_refresh_rate(self):
        try:
            value = int(self.refresh_rate.get())
        except Exception:
            value = 100

        if value < 10:
            value = 10

        return value

    def update_color_loop(self):
        if self.running:
            self.read_cursor_color()
            self.update_labels()
            self.maybe_auto_log()

        self.schedule_next_update()

    def read_cursor_color(self):
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()

        try:
            screenshot = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
            pixel = screenshot.getpixel((0, 0))

            if len(pixel) >= 3:
                r, g, b = pixel[0], pixel[1], pixel[2]
            else:
                r, g, b = 0, 0, 0

        except Exception:
            r, g, b = 0, 0, 0

        hex_value = self.rgb_to_hex(r, g, b)

        self.last_position = (x, y)
        self.last_rgb = (r, g, b)
        self.last_hex = hex_value

    def update_labels(self):
        x, y = self.last_position
        r, g, b = self.last_rgb
        now_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.position_label.config(text=f"Position: X={x}, Y={y}")
        self.rgb_label.config(text=f"RGB: ({r}, {g}, {b})")
        self.hex_label.config(text=f"HEX: {self.last_hex}")
        self.time_label.config(text=f"Last update: {now_string}")

        self.preview_box.config(bg=self.last_hex)
        self.history_count_label.config(text=f"History items: {len(self.history)}")

        if self.running:
            self.status_label.config(text="Status: RUNNING", fg="#7CFC00")
        else:
            self.status_label.config(text="Status: PAUSED", fg="#FFD700")

    def rgb_to_hex(self, r, g, b):
        return "#{:02X}{:02X}{:02X}".format(r, g, b)

    def toggle_running(self):
        self.running = not self.running

        if self.running:
            self.toggle_button.config(text="Pause")
        else:
            self.toggle_button.config(text="Resume")

        self.update_labels()

    def add_current_color_to_history(self):
        x, y = self.last_position
        r, g, b = self.last_rgb
        hex_value = self.last_hex
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = ColorRecord(timestamp, x, y, r, g, b, hex_value)
        self.history.append(record)

        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_listbox.delete(0)

        line = f"{timestamp} | X:{x:<4} Y:{y:<4} | RGB({r:>3}, {g:>3}, {b:>3}) | {hex_value}"
        self.history_listbox.insert(tk.END, line)
        self.history_listbox.yview_moveto(1)

        self.last_logged_hex = hex_value
        self.update_labels()

    def maybe_auto_log(self):
        if not self.auto_log.get():
            return

        if self.only_log_changes.get():
            if self.last_hex == self.last_logged_hex:
                return

        self.add_current_color_to_history()

    def copy_hex(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_hex)
        self.root.update()

    def copy_rgb(self):
        r, g, b = self.last_rgb
        rgb_text = f"({r}, {g}, {b})"
        self.root.clipboard_clear()
        self.root.clipboard_append(rgb_text)
        self.root.update()

    def copy_selected_hex(self, event=None):
        selection = self.history_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index < 0 or index >= len(self.history):
            return

        hex_value = self.history[index].hex_value
        self.root.clipboard_clear()
        self.root.clipboard_append(hex_value)
        self.root.update()

    def clear_history(self):
        answer = messagebox.askyesno("Clear History", "Are you sure you want to clear all saved color history?")
        if not answer:
            return

        self.history.clear()
        self.history_listbox.delete(0, tk.END)
        self.last_logged_hex = None
        self.update_labels()

    def save_history_to_csv(self):
        if not self.history:
            messagebox.showwarning("No Data", "There is no history to save yet.")
            return

        default_name = f"color_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        file_path = filedialog.asksaveasfilename(
            title="Save Color History",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["timestamp", "x", "y", "r", "g", "b", "hex"])

                for record in self.history:
                    writer.writerow(record.to_list())

            self.last_saved_path = file_path
            messagebox.showinfo("Saved", f"History saved successfully.\n\n{file_path}")

        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file.\n\n{e}")


def main():
    root = tk.Tk()

    try:
        app = CursorColorApp(root)
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
