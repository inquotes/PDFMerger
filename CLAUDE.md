# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDF Stitcher is a macOS desktop app for merging multiple PDF files. Built with Python, CustomTkinter (modern UI), and pypdf (PDF manipulation).

## Commands

```bash
# Setup
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python main.py

# Build macOS .app bundle
pyinstaller --name="PDF Stitcher" --windowed --icon=icon.icns main.py
```

No test suite or linter is configured.

## Architecture

Single-file app (`main.py`) with one class `PDFMergerApp(ctk.CTk)`.

- **Data model**: `self.pdf_files` — list of dicts with `path`, `name`, and `created` (datetime) keys
- **UI layout**: Three frames — top (add/sort controls), middle (scrollable file list), bottom (count display/merge button)
- **PDF merging**: Uses `pypdf.PdfWriter` to combine files sequentially
- **File dialogs**: Uses `tkinter.filedialog` for native macOS file pickers
- **Dark mode**: Follows system appearance via `ctk.set_appearance_mode("system")`
- **File metadata**: Uses `os.stat().st_birthtime` for creation date (macOS-specific)

## Dependencies

Core: `customtkinter >= 5.2.0`, `pypdf >= 4.0.0` (see `requirements.txt`)

## Packaging

PyInstaller is the active build system (`PDF Stitcher.spec`). `setup.py` exists as a legacy py2app alternative.
