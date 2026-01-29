#!/usr/bin/env python3
"""
PDF Stitcher - A native macOS app to merge PDF files
Uses CustomTkinter for modern UI and pypdf for merging
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pypdf import PdfWriter
from datetime import datetime


class PDFMergerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("PDF Stitcher")
        self.geometry("700x500")
        self.minsize(500, 400)
        
        # Set appearance
        ctk.set_appearance_mode("system")  # Follow macOS dark/light mode
        ctk.set_default_color_theme("blue")
        
        # Store PDF file paths with metadata
        self.pdf_files = []  # List of dicts: {"path": str, "name": str, "created": datetime}
        
        self._create_ui()
    
    def _create_ui(self):
        # Main container with padding
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === Top frame: Add files button and sort options ===
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        top_frame.grid_columnconfigure(1, weight=1)
        
        add_btn = ctk.CTkButton(
            top_frame, 
            text="+ Add PDFs", 
            command=self._add_files,
            width=120
        )
        add_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Sort options
        sort_label = ctk.CTkLabel(top_frame, text="Sort by:")
        sort_label.grid(row=0, column=2, padx=(10, 5))
        
        sort_name_btn = ctk.CTkButton(
            top_frame,
            text="Name",
            command=self._sort_by_name,
            width=80,
            fg_color="gray40",
            hover_color="gray30"
        )
        sort_name_btn.grid(row=0, column=3, padx=2)
        
        sort_date_btn = ctk.CTkButton(
            top_frame,
            text="Date Created",
            command=self._sort_by_date,
            width=100,
            fg_color="gray40",
            hover_color="gray30"
        )
        sort_date_btn.grid(row=0, column=4, padx=2)
        
        # === Middle frame: List view with scrollbar ===
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Scrollable frame for the file list
        self.scrollable_list = ctk.CTkScrollableFrame(list_frame, label_text="Files to Merge")
        self.scrollable_list.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.scrollable_list.grid_columnconfigure(0, weight=1)
        
        # Placeholder label when empty
        self.empty_label = ctk.CTkLabel(
            self.scrollable_list,
            text="No PDFs added yet.\nClick '+ Add PDFs' to get started.",
            text_color="gray50",
            justify="center"
        )
        self.empty_label.grid(row=0, column=0, pady=50)
        
        # === Right side buttons: Move Up/Down and Remove ===
        btn_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ns")
        
        move_up_btn = ctk.CTkButton(
            btn_frame,
            text="▲ Move Up",
            command=self._move_up,
            width=100
        )
        move_up_btn.pack(pady=(50, 5))
        
        move_down_btn = ctk.CTkButton(
            btn_frame,
            text="▼ Move Down",
            command=self._move_down,
            width=100
        )
        move_down_btn.pack(pady=5)
        
        remove_btn = ctk.CTkButton(
            btn_frame,
            text="✕ Remove",
            command=self._remove_selected,
            width=100,
            fg_color="firebrick",
            hover_color="darkred"
        )
        remove_btn.pack(pady=(20, 5))
        
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear All",
            command=self._clear_all,
            width=100,
            fg_color="gray40",
            hover_color="gray30"
        )
        clear_btn.pack(pady=5)
        
        # === Bottom frame: Merge button ===
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        bottom_frame.grid_columnconfigure(0, weight=1)
        
        self.file_count_label = ctk.CTkLabel(bottom_frame, text="0 files selected")
        self.file_count_label.grid(row=0, column=0, sticky="w")
        
        merge_btn = ctk.CTkButton(
            bottom_frame,
            text="Merge PDFs",
            command=self._merge_pdfs,
            width=150,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        merge_btn.grid(row=0, column=1, sticky="e")
        
        # Track selected item
        self.selected_index = None
        self.file_rows = []  # List of row frames
    
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
            self.empty_label.grid(row=0, column=0, pady=50)
            self.selected_index = None
        else:
            self.empty_label.grid_forget()
        
        # Create rows for each file
        for idx, file_info in enumerate(self.pdf_files):
            row_frame = ctk.CTkFrame(
                self.scrollable_list,
                fg_color="gray25" if idx == self.selected_index else "transparent",
                corner_radius=6
            )
            row_frame.grid(row=idx, column=0, pady=2, sticky="ew")
            row_frame.grid_columnconfigure(1, weight=1)
            
            # Index number
            idx_label = ctk.CTkLabel(row_frame, text=f"{idx + 1}.", width=30)
            idx_label.grid(row=0, column=0, padx=(10, 5), pady=8)
            
            # File name
            name_label = ctk.CTkLabel(
                row_frame, 
                text=file_info["name"],
                anchor="w"
            )
            name_label.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
            
            # Date created (smaller text)
            date_str = file_info["created"].strftime("%Y-%m-%d %H:%M")
            date_label = ctk.CTkLabel(
                row_frame,
                text=date_str,
                text_color="gray50",
                font=ctk.CTkFont(size=11)
            )
            date_label.grid(row=0, column=2, padx=(5, 10), pady=8)
            
            # Bind click events
            for widget in [row_frame, idx_label, name_label, date_label]:
                widget.bind("<Button-1>", lambda e, i=idx: self._select_item(i))
            
            self.file_rows.append(row_frame)
        
        # Update count label
        count = len(self.pdf_files)
        self.file_count_label.configure(text=f"{count} file{'s' if count != 1 else ''} selected")
    
    def _select_item(self, index):
        """Select an item in the list."""
        self.selected_index = index
        self._refresh_list()
    
    def _move_up(self):
        """Move selected item up in the list."""
        if self.selected_index is None or self.selected_index == 0:
            return
        
        idx = self.selected_index
        self.pdf_files[idx], self.pdf_files[idx - 1] = self.pdf_files[idx - 1], self.pdf_files[idx]
        self.selected_index = idx - 1
        self._refresh_list()
    
    def _move_down(self):
        """Move selected item down in the list."""
        if self.selected_index is None or self.selected_index >= len(self.pdf_files) - 1:
            return
        
        idx = self.selected_index
        self.pdf_files[idx], self.pdf_files[idx + 1] = self.pdf_files[idx + 1], self.pdf_files[idx]
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
