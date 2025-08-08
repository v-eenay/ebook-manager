"""
Main Window for Modern EBook Reader
Complete Fluent Design implementation with document support.
"""

import os
from pathlib import Path

try:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QStackedWidget
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QIcon
    QT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QStackedWidget
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QIcon
    QT_VERSION = 5

class MainWindow(QWidget):
    """Main window with complete Fluent Design implementation."""

    def __init__(self):
        super().__init__()
        # Import document manager inside method to avoid widget construction during import
        from readers.document_manager import DocumentManager
        self.document_manager = DocumentManager()
        self.current_document = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface with Fluent Design."""
        # Import Fluent Design components inside the method
        from qfluentwidgets import (
            PrimaryPushButton, TitleLabel, BodyLabel, CardWidget,
            FluentIcon as FIF, InfoBar, InfoBarPosition,
            ToolButton, TransparentToolButton
        )

        self.setWindowTitle("Modern EBook Reader - Fluent Design")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # Create main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create navigation panel with simple buttons
        nav_panel = QWidget()
        nav_panel.setFixedWidth(200)
        nav_panel.setStyleSheet("""
            QWidget {
                background-color: #F3F3F3;
                border-right: 1px solid #E0E0E0;
            }
        """)

        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(10, 20, 10, 20)
        nav_layout.setSpacing(10)

        # Navigation title
        nav_title = TitleLabel("Navigation")
        nav_layout.addWidget(nav_title)

        # Navigation buttons
        self.welcome_btn = ToolButton(FIF.HOME, self)
        self.welcome_btn.setText("Welcome")
        self.welcome_btn.clicked.connect(self.show_welcome)
        nav_layout.addWidget(self.welcome_btn)

        self.reader_btn = ToolButton(FIF.BOOK_SHELF, self)
        self.reader_btn.setText("Reader")
        self.reader_btn.clicked.connect(self.show_reader)
        nav_layout.addWidget(self.reader_btn)

        nav_layout.addStretch()

        self.settings_btn = ToolButton(FIF.SETTING, self)
        self.settings_btn.setText("Settings")
        self.settings_btn.clicked.connect(self.show_settings)
        nav_layout.addWidget(self.settings_btn)

        # Create content area
        self.content_stack = QStackedWidget()

        # Create welcome page
        self.create_welcome_page()

        # Create reader page
        self.create_reader_page()

        # Add to main layout
        main_layout.addWidget(nav_panel)
        main_layout.addWidget(self.content_stack, 1)

        # Set welcome as default
        self.content_stack.setCurrentWidget(self.welcome_page)

    def create_welcome_page(self):
        """Create the welcome page with Fluent Design."""
        from qfluentwidgets import (
            PrimaryPushButton, TitleLabel, BodyLabel, CardWidget,
            FluentIcon as FIF, CaptionLabel
        )

        self.welcome_page = QWidget()
        layout = QVBoxLayout(self.welcome_page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Create title
        title = TitleLabel("Modern EBook Reader")
        if QT_VERSION == 6:
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Create welcome card
        welcome_card = CardWidget()
        welcome_card.setMaximumWidth(600)
        card_layout = QVBoxLayout(welcome_card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        # Welcome content
        welcome_text = BodyLabel(
            "Experience modern document reading with Microsoft Fluent Design System.\n\n"
            "Features:\n"
            "• PDF, EPUB, and MOBI support\n"
            "• Windows 11-style interface\n"
            "• Smooth animations and effects\n"
            "• High contrast accessibility\n"
            "• Modern navigation experience"
        )
        welcome_text.setWordWrap(True)
        if QT_VERSION == 6:
            welcome_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            welcome_text.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(welcome_text)

        # Open document button
        self.open_button = PrimaryPushButton("Open Document", FIF.FOLDER)
        self.open_button.setMinimumWidth(200)
        self.open_button.clicked.connect(self.open_file)
        card_layout.addWidget(self.open_button)

        # Supported formats
        formats_label = CaptionLabel("Supported formats: PDF, EPUB, MOBI")
        if QT_VERSION == 6:
            formats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            formats_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(formats_label)

        # Center the card
        card_container = QHBoxLayout()
        card_container.addStretch()
        card_container.addWidget(welcome_card)
        card_container.addStretch()

        layout.addLayout(card_container)
        layout.addStretch()

        self.content_stack.addWidget(self.welcome_page)

    def create_reader_page(self):
        """Create the reader page with Fluent Design and embed the DocumentViewer."""
        from qfluentwidgets import BodyLabel, CardWidget

        self.reader_page = QWidget()
        layout = QVBoxLayout(self.reader_page)
        layout.setContentsMargins(20, 20, 20, 20)

        # Create reader card
        reader_card = CardWidget()
        reader_layout = QVBoxLayout(reader_card)
        reader_layout.setContentsMargins(10, 10, 10, 10)

        # Lazy-create the document viewer container
        from ui.document_viewer import DocumentViewer
        self.document_viewer = DocumentViewer(self)
        reader_layout.addWidget(self.document_viewer)

        # Fallback/info label shown when no document is loaded
        self.reader_content = BodyLabel("No document loaded. Please open a document from the Welcome page.")
        self.reader_content.setWordWrap(True)
        if QT_VERSION == 6:
            self.reader_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.reader_content.setAlignment(Qt.AlignCenter)
        # Start with info label visible until a document is loaded
        self.reader_content.setVisible(True)
        reader_layout.addWidget(self.reader_content)

        layout.addWidget(reader_card)
        self.content_stack.addWidget(self.reader_page)

    def show_welcome(self):
        """Show the welcome page."""
        self.content_stack.setCurrentWidget(self.welcome_page)

    def show_reader(self):
        """Show the reader page."""
        self.content_stack.setCurrentWidget(self.reader_page)

    def show_settings(self):
        """Show settings (placeholder)."""
        from qfluentwidgets import InfoBar, InfoBarPosition
        InfoBar.info(
            title="Settings",
            content="Settings panel coming soon!",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

    def open_file(self):
        """Open a document file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            "",
            "All Supported (*.pdf *.epub *.mobi);;PDF Files (*.pdf);;EPUB Files (*.epub);;MOBI Files (*.mobi)"
        )

        if file_path:
            self.load_document(file_path)

    def load_document(self, file_path):
        """Load a document and display it in the embedded DocumentViewer."""
        from qfluentwidgets import InfoBar, InfoBarPosition
        import traceback

        try:
            # Load document using document manager
            document = self.document_manager.load_document(file_path)
            if document:
                self.current_document = document

                # Ensure the document viewer exists and load the document into it
                if hasattr(self, 'document_viewer') and self.document_viewer is not None:
                    try:
                        self.document_viewer.load_document(self.current_document)
                    except Exception as display_error:
                        # Detailed error and fallback
                        tb_str = traceback.format_exc()
                        from qfluentwidgets import InfoBar
                        InfoBar.error(
                            title="Display Error",
                            content=(
                                "Failed to display the document. This may be due to graphics initialization issues or an unsupported format. "
                                "Please try restarting the app or opening a different file. See log for details."
                            ),
                            orient=Qt.Horizontal,
                            isClosable=True,
                            position=InfoBarPosition.TOP,
                            duration=6000,
                            parent=self
                        )
                        try:
                            from utils.logger import setup_logging
                            setup_logging().error("Display error: %s\n%s", display_error, tb_str)
                        except Exception:
                            pass

                # Hide the placeholder info label once a document is loaded
                if hasattr(self, 'reader_content'):
                    self.reader_content.setVisible(False)

                # Switch to reader view
                self.show_reader()

                # Show success message
                InfoBar.success(
                    title="Document Loaded",
                    content=f"Successfully opened {Path(file_path).name}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )

        except Exception as e:
            # Show error message
            InfoBar.error(
                title="Error Loading Document",
                content=f"Failed to load document: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

    def closeEvent(self, event):
        """Handle window close event."""
        # Clean up resources
        if self.current_document:
            self.current_document = None
        event.accept()
