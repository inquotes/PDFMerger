#!/usr/bin/env python3
"""
PDF Stitcher - A native macOS app to merge PDF files
Uses CustomTkinter for modern UI and pypdf for merging
"""

import os
import re
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pypdf import PdfWriter
from datetime import datetime
from tkinterdnd2 import DND_FILES, TkinterDnD

if sys.platform == "darwin":
    from AppKit import NSApplication, NSColor, NSApp


# Color palette — derived from the app icon
RUST = "#BA3601"
RUST_HOVER = "#8E2A01"
MUTED_RUST = "#6B3020"
MUTED_RUST_HOVER = "#552518"
CREAM = "#FCEFD9"
CREAM_MID = ("#F5E4C8", "#2B2B2B")       # panels / list frame (light, dark)
SELECTION_BG = ("#E2BA88", "#4A2010")     # selected row (light, dark)
WARM_GRAY = "#8B8178"
DIMMED_ROW = ("#E8CDB0", "#2A1A10")      # source row during drag (light, dark)
FILE_TEXT = ("#5C534A", "#8B8178")        # file name / index text (light, dark)
BTN_TEXT = "#FCEFD9"                      # button label text (cream on rust)


class Tk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


class PDFMergerApp(Tk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("PDF Stitcher")
        self.geometry("700x500")
        self.minsize(500, 400)
        
        # Set appearance
        ctk.set_appearance_mode("system")  # Follow macOS dark/light mode
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=(CREAM, ctk.ThemeManager.theme["CTk"]["fg_color"][1]))
        
        # Store PDF file paths with metadata
        self.pdf_files = []  # List of dicts: {"path": str, "name": str, "created": datetime}

        # Drag-and-drop reorder state
        self._drag_source_index = None
        self._drag_target_index = None
        self._drag_indicator = None
        self._drag_ghost = None
        self._drag_active = False

        self._create_ui()
        self._setup_dnd()
        self.after(100, self._style_titlebar)
        ctk.AppearanceModeTracker.callback_list.append(self._on_appearance_change)
    
    def _create_ui(self):
        # Main container with padding
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === Top frame: Add files button ===
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        top_frame.grid_columnconfigure(0, weight=1)

        add_btn = ctk.CTkButton(
            top_frame,
            text="+ Add PDFs",
            command=self._add_files,
            width=120,
            fg_color=RUST,
            hover_color=RUST_HOVER,
            text_color=BTN_TEXT
        )
        add_btn.grid(row=0, column=0, sticky="w")

        # === Middle frame: Scrollable file list ===
        self.scrollable_list = ctk.CTkScrollableFrame(
            self, fg_color=CREAM_MID
        )
        self.scrollable_list.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.scrollable_list.grid_columnconfigure(0, weight=1)

        # Column header row (shown only when files are present)
        self.header_frame = ctk.CTkFrame(self.scrollable_list, fg_color="transparent")
        self.header_frame.grid_columnconfigure(2, weight=1)

        # Spacer matching grip (col 0) + index (col 1)
        ctk.CTkLabel(self.header_frame, text="", width=20).grid(row=0, column=0, padx=(8, 0))
        ctk.CTkLabel(self.header_frame, text="", width=30).grid(row=0, column=1, padx=(2, 5))

        header_name_btn = ctk.CTkButton(
            self.header_frame, text="File Name ↕", anchor="w",
            fg_color="transparent", hover_color=SELECTION_BG,
            text_color=(RUST, CREAM), font=ctk.CTkFont(size=12, weight="bold"),
            command=self._sort_by_name, width=0
        )
        header_name_btn.grid(row=0, column=2, padx=5, sticky="w")

        header_date_btn = ctk.CTkButton(
            self.header_frame, text="Date ↕",
            fg_color="transparent", hover_color=SELECTION_BG,
            text_color=(RUST, CREAM), font=ctk.CTkFont(size=12, weight="bold"),
            command=self._sort_by_date, width=0
        )
        header_date_btn.grid(row=0, column=3, padx=(5, 5))

        # Spacer matching up/down button columns
        ctk.CTkLabel(self.header_frame, text="", width=28).grid(row=0, column=4)
        ctk.CTkLabel(self.header_frame, text="", width=28).grid(row=0, column=5, padx=(0, 8))
        
        # Placeholder label when empty
        self.empty_label = ctk.CTkLabel(
            self.scrollable_list,
            text="No PDFs added yet.\nClick '+ Add PDFs' or drag files here.",
            text_color=WARM_GRAY,
            justify="center"
        )
        self.empty_label.grid(row=1, column=0, pady=50)
        
        # === Bottom frame: Remove/Clear left, Merge right ===
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        bottom_frame.grid_columnconfigure(2, weight=1)

        remove_btn = ctk.CTkButton(
            bottom_frame,
            text="✕ Remove",
            command=self._remove_selected,
            width=100,
            fg_color="transparent",
            border_color=RUST,
            border_width=2,
            text_color=RUST,
            hover_color=RUST
        )
        remove_btn.grid(row=0, column=0, padx=(0, 5))

        clear_btn = ctk.CTkButton(
            bottom_frame,
            text="Clear All",
            command=self._clear_all,
            width=100,
            fg_color=MUTED_RUST,
            hover_color=MUTED_RUST_HOVER,
            text_color=BTN_TEXT
        )
        clear_btn.grid(row=0, column=1, sticky="w")

        
        merge_btn = ctk.CTkButton(
            bottom_frame,
            text="Merge PDFs",
            command=self._merge_pdfs,
            width=150,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=RUST,
            hover_color=RUST_HOVER,
            text_color=BTN_TEXT
        )
        merge_btn.grid(row=0, column=3, sticky="e")
        
        # Track selected item
        self.selected_index = None
        self.file_rows = []  # List of row frames

        # Window-level drag/drop bindings so events fire even outside the list
        self.bind("<B1-Motion>", self._on_window_drag)
        self.bind("<ButtonRelease-1>", self._on_row_drop)

    def _style_titlebar(self):
        """Make the macOS title bar transparent and match the app background."""
        if sys.platform != "darwin":
            return
        try:
            self._ns_window = None
            for window in NSApp.windows():
                if "PDF Stitcher" in (window.title() or ""):
                    self._ns_window = window
                    window.setTitlebarAppearsTransparent_(True)
                    break
            self._apply_titlebar_color(ctk.get_appearance_mode())
        except Exception:
            pass  # Graceful fallback — title bar stays default

    def _on_appearance_change(self, mode):
        """Called by CustomTkinter when system appearance mode changes."""
        self._apply_titlebar_color("Dark" if mode == "Dark" or mode == 1 else "Light")

    def _apply_titlebar_color(self, mode):
        """Set the NSWindow background color to match the current appearance."""
        if not getattr(self, "_ns_window", None):
            return
        try:
            if mode == "Dark":
                # Use winfo_rgb to resolve any color name (e.g. "gray14") to RGB
                rgb = self.winfo_rgb(ctk.ThemeManager.theme["CTk"]["fg_color"][1])
                r, g, b = rgb[0] / 65535.0, rgb[1] / 65535.0, rgb[2] / 65535.0
            else:
                r = int(CREAM[1:3], 16) / 255.0
                g = int(CREAM[3:5], 16) / 255.0
                b = int(CREAM[5:7], 16) / 255.0
            ns_color = NSColor.colorWithSRGBRed_green_blue_alpha_(r, g, b, 1.0)
            self._ns_window.setBackgroundColor_(ns_color)
        except Exception:
            pass

    def _add_files(self):
        """Open file dialog to add PDF files."""
        filepaths = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF files", "*.pdf")],
            parent=self
        )
        
        for path in filepaths:
            if path not in [f["path"] for f in self.pdf_files]:
                # Get file creation time
                stat = os.stat(path)
                created = datetime.fromtimestamp(stat.st_birthtime)
                
                self.pdf_files.append({
                    "path": path,
                    "name": os.path.basename(path),
                    "created": created
                })
        
        self._refresh_list()
    
    def _refresh_list(self):
        """Refresh the list view with current files."""
        # Clear existing rows
        for row in self.file_rows:
            row.destroy()
        self.file_rows.clear()
        
        # Show/hide empty label
        if not self.pdf_files:
            self.header_frame.grid_forget()
            self.empty_label.grid(row=1, column=0, pady=50)
            self.selected_index = None
        else:
            self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
            self.empty_label.grid_forget()
        
        # Create rows for each file
        for idx, file_info in enumerate(self.pdf_files):
            row_frame = ctk.CTkFrame(
                self.scrollable_list,
                fg_color=SELECTION_BG if idx == self.selected_index else "transparent",
                corner_radius=6
            )
            row_frame.grid(row=idx * 2 + 2, column=0, pady=2, sticky="ew")
            row_frame.grid_columnconfigure(2, weight=1)

            # Drag grip icon
            grip_label = ctk.CTkLabel(
                row_frame, text="⠿", width=20,
                text_color=WARM_GRAY,
                font=ctk.CTkFont(size=14),
                cursor="hand2"
            )
            grip_label.grid(row=0, column=0, padx=(8, 0), pady=8)

            # Index number
            idx_label = ctk.CTkLabel(row_frame, text=f"{idx + 1}.", width=30, text_color=FILE_TEXT)
            idx_label.grid(row=0, column=1, padx=(2, 5), pady=8)

            # File name
            name_label = ctk.CTkLabel(
                row_frame,
                text=file_info["name"],
                anchor="w",
                text_color=FILE_TEXT
            )
            name_label.grid(row=0, column=2, padx=5, pady=8, sticky="ew")

            # Date created (smaller text)
            date_str = file_info["created"].strftime("%Y-%m-%d %H:%M")
            date_label = ctk.CTkLabel(
                row_frame,
                text=date_str,
                text_color=WARM_GRAY,
                font=ctk.CTkFont(size=11)
            )
            date_label.grid(row=0, column=3, padx=(5, 5), pady=8)

            # Inline move up/down buttons
            up_btn = ctk.CTkButton(
                row_frame, text="▲", width=28, height=28,
                fg_color="transparent", hover_color=MUTED_RUST,
                text_color=WARM_GRAY if idx > 0 else ("#D5CCC3", "#3A3A3A"),
                command=lambda i=idx: self._move_up(i),
                state="normal" if idx > 0 else "disabled"
            )
            up_btn.grid(row=0, column=4, padx=0, pady=2)

            down_btn = ctk.CTkButton(
                row_frame, text="▼", width=28, height=28,
                fg_color="transparent", hover_color=MUTED_RUST,
                text_color=WARM_GRAY if idx < len(self.pdf_files) - 1 else ("#D5CCC3", "#3A3A3A"),
                command=lambda i=idx: self._move_down(i),
                state="normal" if idx < len(self.pdf_files) - 1 else "disabled"
            )
            down_btn.grid(row=0, column=5, padx=(0, 8), pady=2)

            # Bind click on each row widget to identify which row was clicked
            for widget in [row_frame, grip_label, idx_label, name_label, date_label]:
                widget.bind("<Button-1>", lambda e, i=idx: self._on_row_click(e, i))

            self.file_rows.append(row_frame)
        
    
    def _select_item(self, index):
        """Select an item in the list."""
        self.selected_index = index
        self._refresh_list()

    # --- External drag-and-drop (from Finder via tkinterdnd2) ---

    def _setup_dnd(self):
        """Register the scrollable list as a drop target for files from Finder."""
        target = self.scrollable_list._parent_frame
        target.drop_target_register(DND_FILES)
        target.dnd_bind("<<DropEnter>>", self._on_drop_enter)
        target.dnd_bind("<<DropLeave>>", self._on_drop_leave)
        target.dnd_bind("<<Drop>>", self._on_drop)

    def _on_drop_enter(self, event):
        self.scrollable_list.configure(border_color=MUTED_RUST, border_width=2)
        return event.action

    def _on_drop_leave(self, event):
        self.scrollable_list.configure(border_width=0)
        return event.action

    def _on_drop(self, event):
        self.scrollable_list.configure(border_width=0)
        paths = self._parse_drop_data(event.data)

        added = 0
        existing_paths = {f["path"] for f in self.pdf_files}
        for path in paths:
            if not path.lower().endswith(".pdf"):
                continue
            if path in existing_paths:
                continue
            if not os.path.isfile(path):
                continue
            stat = os.stat(path)
            created = datetime.fromtimestamp(stat.st_birthtime)
            self.pdf_files.append({
                "path": path,
                "name": os.path.basename(path),
                "created": created,
            })
            existing_paths.add(path)
            added += 1

        if added:
            self._refresh_list()
        return event.action

    @staticmethod
    def _parse_drop_data(data):
        """Parse tkinterdnd2 drop data into a list of file paths."""
        results = []
        for match in re.finditer(r'\{([^}]+)\}|(\S+)', data):
            results.append(match.group(1) or match.group(2))
        return results

    # --- Internal drag-and-drop reorder ---

    def _on_row_click(self, event, index):
        """Handle click on a row — select it and prepare for potential drag."""
        self._drag_source_index = index
        self._select_item(index)

    def _on_window_drag(self, event):
        """Window-level drag handler — delegates to row drag if active."""
        if self._drag_source_index is not None:
            self._on_row_drag(event, self._drag_source_index)

    def _on_row_drag(self, event, source_index):
        """Handle dragging a row to reorder."""
        if self._drag_source_index is None:
            return
        if len(self.file_rows) < 2:
            return

        # Dim the source row and create ghost on first motion
        src_row = self.file_rows[self._drag_source_index]
        if not self._drag_active:
            self._drag_active = True
            src_row.configure(fg_color=DIMMED_ROW)
            for child in src_row.winfo_children():
                try:
                    child.configure(text_color=WARM_GRAY)
                except Exception:
                    pass
            # Create a floating ghost label showing the dragged file name
            file_name = self.pdf_files[self._drag_source_index]["name"]
            self._drag_ghost = ctk.CTkLabel(
                self,
                text=f"  {file_name}  ",
                fg_color=CREAM,
                corner_radius=4,
                text_color="#2B2B2B",
                font=ctk.CTkFont(size=13),
                anchor="w",
                height=30,
            )

        # Calculate absolute cursor position
        try:
            abs_x = event.widget.winfo_rootx() + event.x
            abs_y = event.widget.winfo_rooty() + event.y
        except Exception:
            return

        # Position the ghost near the cursor
        ghost_x = abs_x - self.winfo_rootx() + 12
        ghost_y = abs_y - self.winfo_rooty() - 15
        self._drag_ghost.place(x=ghost_x, y=ghost_y)
        self._drag_ghost.lift()

        # Get y position relative to the scrollable list
        y_in_list = abs_y - self.scrollable_list.winfo_rooty()

        # Determine target insertion index based on y position
        # target_index means "insert before this index"
        # target_index == len means "insert at the end"
        target_index = len(self.file_rows)
        for i, row in enumerate(self.file_rows):
            row_y = row.winfo_y()
            row_h = row.winfo_height()
            if y_in_list < row_y + row_h // 2:
                target_index = i
                break

        target_index = max(0, min(target_index, len(self.file_rows)))

        if target_index != self._drag_target_index:
            self._drag_target_index = target_index
            self._show_drag_indicator(target_index)

    def _show_drag_indicator(self, target_index):
        """Show a visual line indicating where the dragged item will be inserted."""
        # Remove old indicator
        if self._drag_indicator:
            self._drag_indicator.destroy()
            self._drag_indicator = None

        if target_index == self._drag_source_index or target_index == self._drag_source_index + 1:
            return

        self._drag_indicator = ctk.CTkFrame(
            self.scrollable_list,
            height=5,
            fg_color=RUST,
            corner_radius=2,
        )
        # Header is at row 0; file rows use grid rows 2,4,6,...
        # Indicator slots are at 1,3,5,...
        indicator_grid_row = target_index * 2 + 1
        self._drag_indicator.grid(row=indicator_grid_row, column=0, sticky="ew", padx=5, pady=0)

    def _on_row_drop(self, event):
        """Finalize the reorder on mouse release."""
        self._drag_active = False

        if self._drag_ghost:
            self._drag_ghost.destroy()
            self._drag_ghost = None

        if self._drag_indicator:
            self._drag_indicator.destroy()
            self._drag_indicator = None

        src = self._drag_source_index
        dst = self._drag_target_index
        self._drag_source_index = None
        self._drag_target_index = None

        if src is None or dst is None:
            self._refresh_list()
            return
        if dst == src or dst == src + 1:
            # No actual move needed (same position)
            self._refresh_list()
            return
        if not (0 <= src < len(self.pdf_files) and 0 <= dst <= len(self.pdf_files)):
            self._refresh_list()
            return

        # Move the item: pop first, then adjust insert index
        item = self.pdf_files.pop(src)
        insert_at = dst if dst < src else dst - 1
        self.pdf_files.insert(insert_at, item)
        self.selected_index = insert_at
        self._refresh_list()

    def _move_up(self, idx=None):
        """Move item up in the list."""
        if idx is None:
            idx = self.selected_index
        if idx is None or idx == 0:
            return
        self.pdf_files[idx], self.pdf_files[idx - 1] = self.pdf_files[idx - 1], self.pdf_files[idx]
        if self.selected_index == idx:
            self.selected_index = idx - 1
        self._refresh_list()

    def _move_down(self, idx=None):
        """Move item down in the list."""
        if idx is None:
            idx = self.selected_index
        if idx is None or idx >= len(self.pdf_files) - 1:
            return
        self.pdf_files[idx], self.pdf_files[idx + 1] = self.pdf_files[idx + 1], self.pdf_files[idx]
        if self.selected_index == idx:
            self.selected_index = idx + 1
        self._refresh_list()
    
    def _remove_selected(self):
        """Remove the selected item from the list."""
        if self.selected_index is None:
            return
        
        del self.pdf_files[self.selected_index]
        
        # Adjust selection
        if self.pdf_files:
            self.selected_index = min(self.selected_index, len(self.pdf_files) - 1)
        else:
            self.selected_index = None
        
        self._refresh_list()
    
    def _clear_all(self):
        """Remove all files from the list."""
        if not self.pdf_files:
            return
        
        if messagebox.askyesno("Clear All", "Remove all files from the list?", parent=self):
            self.pdf_files.clear()
            self.selected_index = None
            self._refresh_list()
    
    def _sort_by_name(self):
        """Sort files alphabetically by name."""
        if not self.pdf_files:
            return
        
        self.pdf_files.sort(key=lambda f: f["name"].lower())
        self.selected_index = None
        self._refresh_list()
    
    def _sort_by_date(self):
        """Sort files by creation date (oldest first)."""
        if not self.pdf_files:
            return
        
        self.pdf_files.sort(key=lambda f: f["created"])
        self.selected_index = None
        self._refresh_list()
    
    def _merge_pdfs(self):
        """Merge all PDFs and save to user-selected location."""
        if not self.pdf_files:
            messagebox.showwarning("No Files", "Please add PDF files to merge.", parent=self)
            return
        
        if len(self.pdf_files) < 2:
            messagebox.showwarning("Not Enough Files", "Please add at least 2 PDF files to merge.", parent=self)
            return
        
        # macOS Save As dialog
        output_path = filedialog.asksaveasfilename(
            title="Save Merged PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="merged.pdf",
            parent=self
        )
        
        if not output_path:
            return  # User cancelled
        
        try:
            writer = PdfWriter()
            
            for file_info in self.pdf_files:
                writer.append(file_info["path"])
            
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            messagebox.showinfo(
                "Success", 
                f"Merged {len(self.pdf_files)} PDFs successfully!\n\nSaved to:\n{output_path}",
                parent=self
            )
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge PDFs:\n{str(e)}", parent=self)


def main():
    app = PDFMergerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
