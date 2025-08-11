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
        # Import Qt after path setup
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        from ui.main_window import MainWindow
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Modern EBook Reader")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("EBook Reader")
        
        # Enable high DPI scaling
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
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
                self.document_label.setAlignment(Qt.AlignCenter)
            except Exception:
                # If even setting text fails, log it
                logger.exception("Critical display error: %s", e)

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        from qfluentwidgets import toggleTheme, isDarkTheme, InfoBar, InfoBarIcon, InfoBarPosition

        toggleTheme()
        theme_name = "Dark" if isDarkTheme() else "Light"

        # Update theme status label
        self.theme_status.setText(f"Theme: {theme_name}")

        # Reapply comprehensive styling for the new theme
        self.apply_comprehensive_styling()

        # Update document display if document is loaded
        if self.current_document and hasattr(self, 'document_label'):
            self.update_document_styling()

        # Show theme change notification with proper animation
        info_bar = InfoBar(
            icon=InfoBarIcon.SUCCESS,
            title="Theme Changed",
            content=f"Switched to {theme_name} theme",
            orient=Qt.Horizontal,
            isClosable=True,
            duration=2000,
            parent=self
        )
        info_bar.show()

    def update_document_styling(self):
        """Update document display styling based on current theme."""
        from qfluentwidgets import isDarkTheme

        if not hasattr(self, 'document_label'):
            return

        if isDarkTheme():
            self.document_label.setStyleSheet("""
                QLabel {
                    background-color: #2D2D2D !important;
                    border: 1px solid #404040 !important;
                    padding: 30px;
                    font-size: 14px;
                    color: #E0E0E0 !important;
                    line-height: 1.6;
                }
            """)
            # Update scroll area styling
            if hasattr(self, 'document_scroll'):
                self.document_scroll.setStyleSheet("""
                    QScrollArea {
                        background-color: #1E1E1E !important;
                        border: 1px solid #404040 !important;
                    }
                """)
        else:
            self.document_label.setStyleSheet("""
                QLabel {
                    background-color: #FFFFFF !important;
                    border: 1px solid #E0E0E0 !important;
                    padding: 30px;
                    font-size: 14px;
                    color: #333333 !important;
                    line-height: 1.6;
                }
            """)
            # Update scroll area styling
            if hasattr(self, 'document_scroll'):
                self.document_scroll.setStyleSheet("""
                    QScrollArea {
                        background-color: #F8F8F8 !important;
                        border: 1px solid #E0E0E0 !important;
                    }
                """)

        # Force update
        self.document_label.update()
        if hasattr(self, 'document_scroll'):
            self.document_scroll.update()

    def close_document(self):
        """Close the current document and return to home."""
        if self.current_document:
            if hasattr(self.current_document, 'close'):
                self.current_document.close()
            self.current_document = None
            self.current_page = 0
        self.go_home()

    def zoom_in(self):
        """Zoom in on the document."""
        from qfluentwidgets import InfoBar, InfoBarIcon
        info_bar = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title="Zoom In",
            content="Zoom functionality coming soon",
            orient=Qt.Horizontal,
            isClosable=True,
            duration=2000,
            parent=self
        )
        info_bar.show()

    def zoom_out(self):
        """Zoom out on the document."""
        from qfluentwidgets import InfoBar, InfoBarIcon
        info_bar = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title="Zoom Out",
            content="Zoom functionality coming soon",
            orient=Qt.Horizontal,
            isClosable=True,
            duration=2000,
            parent=self
        )
        info_bar.show()

    def fit_to_window(self):
        """Fit document to window."""
        from qfluentwidgets import InfoBar, InfoBarIcon
        info_bar = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title="Fit to Window",
            content="Fit to window functionality coming soon",
            orient=Qt.Horizontal,
            isClosable=True,
            duration=2000,
            parent=self
        )
        info_bar.show()

    def previous_page(self):
        """Go to previous page."""
        if hasattr(self, 'document_viewer') and self.document_viewer is not None:
            if self.document_viewer.previous_page():
                self.update_page_info()

    def next_page(self):
        """Go to next page."""
        if hasattr(self, 'document_viewer') and self.document_viewer is not None:
            if self.document_viewer.next_page():
                self.update_page_info()

    def go_home(self):
        """Return to home screen."""
        self.stacked_widget.setCurrentIndex(0)
        self.setWindowTitle("Modern EBook Reader - Fluent Design")

    def update_page_info(self):
        """Update the page information display."""
        if hasattr(self, 'document_viewer') and self.document_viewer.current_document:
            current_page = self.document_viewer.get_current_page()
            page_count = self.document_viewer.get_page_count()
            self.setWindowTitle(f"Modern EBook Reader - Page {current_page} of {page_count}")
            if hasattr(self, 'page_info_label'):
                self.page_info_label.setText(f"Page {current_page} of {page_count}")
        else:
            self.setWindowTitle("Modern EBook Reader - Fluent Design")
            if hasattr(self, 'page_info_label'):
                self.page_info_label.setText("No document")


def main():
    """Main application entry point."""
    # Create QApplication first
    app = QApplication(sys.argv)
    app.setApplicationName("Modern EBook Reader")

    # Install a global exception hook to log unhandled exceptions
    def _excepthook(exc_type, exc_value, exc_tb):
        try:
            import traceback
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
            logger.error("Unhandled exception: %s: %s\n%s", exc_type.__name__, exc_value, tb_str)
        finally:
            try:
                from PyQt5.QtWidgets import QMessageBox
                # Only show GUI dialog if a QApplication exists
                if QApplication.instance() is not None:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Application Error")
                    msg.setText("An unexpected error occurred. The application will attempt to continue.")
                    msg.setInformativeText(str(exc_value))
                    msg.setDetailedText(tb_str)
                    msg.exec_()
            except Exception:
                pass
    sys.excepthook = _excepthook

    # Initialize Fluent Design theme with explicit light theme for better visibility
    try:
        from qfluentwidgets import setTheme, Theme, setThemeColor, isDarkTheme
        setTheme(Theme.LIGHT)
        setThemeColor('#0078D4')  # Microsoft Blue
        logger.info("Theme set to: %s", 'Dark' if isDarkTheme() else 'Light')
    except Exception as e:
        logger.warning("Failed to initialize theme: %s", e)

    # Create and show main window
    try:
        window = MainWindow()
        window.show()
        logger.info("Application window created and shown successfully")
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        logger.exception("Error creating main window: %s\n%s", e, tb_str)
        try:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Startup Error",
                                 f"Failed to start the application.\n\nDetails: {e}\n\nSee ebook-reader.log for a full stack trace.")
        except Exception:
            pass
        # Exit gracefully
        return 1

    try:
        logger.info("✅ Fluent Design application started successfully!")
        return app.exec_()
    except Exception as e:
        logger.exception("Application runtime error: %s", e)
        return 1

if __name__ == "__main__":
    main()
