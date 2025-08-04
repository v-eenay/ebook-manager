#!/usr/bin/env python3
"""
Modern EBook Reader - Python + Qt Implementation
A clean, minimal ebook reader supporting PDF, EPUB, and MOBI formats.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
    QT_VERSION = 6
except ImportError:
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QIcon
        QT_VERSION = 5
    except ImportError:
        print("Error: Neither PyQt6 nor PyQt5 is installed.")
        print("Please install one of them using:")
        print("  pip install PyQt6")
        print("  or")
        print("  pip install PyQt5")
        sys.exit(1)

def main():
    """Main application entry point with Fluent Design System."""
    # Enable high DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Create standard Qt application (Fluent widgets work with QApplication)
    app = QApplication(sys.argv)
    app.setApplicationName("Modern EBook Reader")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Modern EBook Reader")

    # Initialize Fluent Design theme first
    from qfluentwidgets import setTheme, Theme, setThemeColor
    setTheme(Theme.AUTO)  # Automatic light/dark theme detection
    setThemeColor('#0078D4')  # Microsoft Blue

    # Import main window after theme is set
    from ui.main_window import MainWindow

    # Set application icon
    icon_path = Path(__file__).parent / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Start the event loop
    sys.exit(app.exec() if QT_VERSION == 6 else app.exec_())


if __name__ == "__main__":
    main()
