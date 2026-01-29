# PDF Merger

A native macOS desktop app to merge PDF files with a modern, intuitive interface.

![macOS](https://img.shields.io/badge/macOS-10.14+-blue)
![Python](https://img.shields.io/badge/python-3.13+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

✨ **Modern UI** - Built with CustomTkinter, automatically adapts to macOS dark/light mode  
📄 **Easy File Management** - Add multiple PDFs with native file picker  
🔄 **Flexible Ordering** - Reorder files with Move Up/Down buttons  
📊 **Smart Sorting** - Sort by filename (A-Z) or creation date  
💾 **Native Integration** - Uses macOS native "Save As" dialog  
🎯 **Simple & Fast** - All features in one clean interface

## Screenshots

<!-- Add screenshot here later -->
*Screenshot coming soon*

## Requirements

- macOS 10.14 or later
- Python 3.13+ with Tkinter support
- Homebrew (for easy installation)

## Installation

### 1. Install Python with Tkinter

```bash
brew install python-tk@3.13
```

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/PDFMerger.git
cd PDFMerger
```

### 3. Set Up Virtual Environment

```bash
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Running the App

```bash
source venv/bin/activate
python main.py
```

### Using the App

1. **Add PDFs** - Click "+ Add PDFs" and select files
2. **Reorder** - Click a file to select it, then use Move Up/Down buttons
3. **Sort** - Use "Name" or "Date Created" buttons to auto-sort
4. **Remove** - Select and click "Remove" to delete, or "Clear All" to start over
5. **Merge** - Click "Merge PDFs" and choose where to save the result

## Building as a .app

*Coming soon - Instructions for packaging with py2app or PyInstaller*

## Dependencies

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern UI framework
- [pypdf](https://github.com/py-pdf/pypdf) - PDF manipulation library

## Development

### Project Structure

```
PDFMerger/
├── main.py           # Main application code
├── requirements.txt  # Python dependencies
├── venv/            # Virtual environment (not in git)
└── README.md        # This file
```

### Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project however you'd like.

## Roadmap

- [ ] Package as standalone .app
- [ ] Add drag-and-drop support
- [ ] Page range selection for individual PDFs
- [ ] PDF preview thumbnails
- [ ] Remember last used directory
- [ ] Batch processing presets

## Author

Built with ❤️ for macOS

---

*If you find this useful, consider giving it a ⭐ on GitHub!*
