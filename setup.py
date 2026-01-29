"""
Setup script for building PDF Stitcher as a macOS .app bundle
"""

from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': 'PDF Stitcher',
        'CFBundleDisplayName': 'PDF Stitcher',
        'CFBundleGetInfoString': 'Merge PDF files with ease',
        'CFBundleIdentifier': 'com.inquotes.pdfstitcher',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2026',
        'NSHighResolutionCapable': True,
    },
    'packages': ['customtkinter', 'pypdf', 'PIL', 'darkdetect', 'packaging'],
    'includes': ['tkinter'],
}

setup(
    name='PDF Stitcher',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
