#!/usr/bin/env python3
"""
Modern EBook Reader - Clean Application Entry Point
"""

import sys
from pathlib import Path
import logging

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Initialize logging
try:
    from utils.logger import setup_logging
    logger = setup_logging()
except Exception as e:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ebook_reader")
    logger.error("Failed to initialize file logger: %s", e)

def main():
    """Main application entry point."""
    try:
        # Import Qt after path setup - use PyQt5 for qfluentwidgets compatibility
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        # Set high DPI scaling BEFORE creating QApplication
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Modern EBook Reader")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("EBook Reader")
        
        # Import MainWindow AFTER QApplication is created to avoid widget creation issues
        from ui.main_window import MainWindow
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Start event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.exception("Failed to start application: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
