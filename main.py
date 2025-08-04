#!/usr/bin/env python3
"""
Direct main application with Fluent Design - bypassing src structure
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QFileDialog, QLabel, QScrollArea, QStackedWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

class MainWindow(QWidget):
    """Direct main window with Fluent Design components."""
    
    def __init__(self):
        super().__init__()
        self.current_document = None
        self.current_page = 0
        self.document_manager = None
        self.init_ui()
        self.apply_comprehensive_styling()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Import Fluent Design components inside the method
        from qfluentwidgets import PrimaryPushButton, TitleLabel, BodyLabel, CardWidget
        
        self.setWindowTitle("Modern EBook Reader - Fluent Design")
        self.setMinimumSize(800, 600)
        
        # Set explicit window styling for better visibility (will be overridden by comprehensive styling)
        self.setStyleSheet("""
            QWidget {
                background-color: #F3F3F3;
                color: #000000;
                font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            }
        """)

        # Create main layout with stacked widget for different views
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create stacked widget for home and document views
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Create home page
        self.create_home_page()

        # Create document viewer page
        self.create_document_page()
        
    def create_home_page(self):
        """Create the minimal home page."""
        from qfluentwidgets import PrimaryPushButton, TitleLabel, BodyLabel, CardWidget, CaptionLabel

        home_widget = QWidget()
        layout = QVBoxLayout(home_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Create title with minimal styling
        title = TitleLabel("Modern EBook Reader")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            TitleLabel {
                color: #000000;
                font-size: 32px;
                font-weight: 300;
                margin: 20px 0px;
                background-color: transparent;
            }
        """)
        layout.addWidget(title)

        # Create minimal card
        card = CardWidget()
        card.setStyleSheet("""
            CardWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
                padding: 40px;
            }
        """)
        card.setMaximumWidth(500)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(25)

        # Minimal welcome text
        text = BodyLabel("Open a document to begin reading")
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet("""
            BodyLabel {
                color: #666666;
                font-size: 18px;
                font-weight: 400;
                background-color: transparent;
                margin: 10px 0px;
            }
        """)
        card_layout.addWidget(text)

        # Open document button
        button = PrimaryPushButton("Open Document")
        button.setMinimumHeight(50)
        button.setMinimumWidth(200)
        button.setStyleSheet("""
            PrimaryPushButton {
                background-color: #0078D4;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                padding: 15px 30px;
            }
            PrimaryPushButton:hover {
                background-color: #106EBE;
            }
            PrimaryPushButton:pressed {
                background-color: #005A9E;
            }
        """)
        button.clicked.connect(self.open_file)
        card_layout.addWidget(button)

        # Center the card
        card_container = QHBoxLayout()
        card_container.addStretch()
        card_container.addWidget(card)
        card_container.addStretch()

        layout.addLayout(card_container)
        layout.addStretch()

        # Add theme toggle at bottom
        from qfluentwidgets import isDarkTheme

        theme_container = QHBoxLayout()
        theme_status = CaptionLabel(f"Theme: {'Dark' if isDarkTheme() else 'Light'}")
        theme_status.setStyleSheet("""
            CaptionLabel {
                color: #999999;
                font-size: 12px;
                background-color: transparent;
            }
        """)

        theme_button = PrimaryPushButton("Toggle")
        theme_button.setMaximumWidth(80)
        theme_button.setStyleSheet("""
            PrimaryPushButton {
                background-color: #6B6B6B;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                padding: 6px 12px;
            }
            PrimaryPushButton:hover {
                background-color: #5A5A5A;
            }
        """)
        theme_button.clicked.connect(self.toggle_theme)

        theme_container.addStretch()
        theme_container.addWidget(theme_status)
        theme_container.addWidget(theme_button)
        theme_container.addStretch()

        layout.addLayout(theme_container)

        # Store reference for theme updates
        self.theme_status = theme_status

        self.stacked_widget.addWidget(home_widget)

    def create_document_page(self):
        """Create the document viewer page with ribbon toolbar."""
        document_widget = QWidget()
        layout = QVBoxLayout(document_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create ribbon toolbar
        self.create_ribbon_toolbar(layout)

        # Create document display area
        self.document_scroll = QScrollArea()
        self.document_scroll.setWidgetResizable(True)
        self.document_scroll.setAlignment(Qt.AlignCenter)

        self.document_label = QLabel("No document loaded")
        self.document_label.setAlignment(Qt.AlignCenter)
        self.document_label.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                padding: 20px;
                font-size: 16px;
                color: #666666;
            }
        """)

        self.document_scroll.setWidget(self.document_label)
        layout.addWidget(self.document_scroll)

        self.stacked_widget.addWidget(document_widget)

    def create_ribbon_toolbar(self, parent_layout):
        """Create Microsoft Office-style ribbon toolbar."""
        from qfluentwidgets import (PrimaryPushButton, PushButton, ToolButton,
                                   FluentIcon as FIF, CardWidget)

        # Create ribbon container
        ribbon_card = CardWidget()
        ribbon_card.setFixedHeight(100)
        ribbon_card.setStyleSheet("""
            CardWidget {
                background-color: #F8F8F8;
                border: none;
                border-bottom: 2px solid #E0E0E0;
                border-radius: 0px;
                padding: 10px;
            }
        """)

        ribbon_layout = QHBoxLayout(ribbon_card)
        ribbon_layout.setContentsMargins(20, 10, 20, 10)
        ribbon_layout.setSpacing(30)

        # File Operations Section
        file_section = self.create_ribbon_section("File", [
            ("Open", FIF.FOLDER, self.open_file),
            ("Close", FIF.CLOSE, self.close_document),
        ])
        ribbon_layout.addWidget(file_section)

        # Add separator
        separator1 = QWidget()
        separator1.setFixedWidth(1)
        separator1.setStyleSheet("background-color: #D0D0D0;")
        ribbon_layout.addWidget(separator1)

        # View Controls Section
        view_section = self.create_ribbon_section("View", [
            ("Zoom In", FIF.ZOOM_IN, self.zoom_in),
            ("Zoom Out", FIF.ZOOM_OUT, self.zoom_out),
            ("Fit Window", FIF.FIT_PAGE, self.fit_to_window),
        ])
        ribbon_layout.addWidget(view_section)

        # Add separator
        separator2 = QWidget()
        separator2.setFixedWidth(1)
        separator2.setStyleSheet("background-color: #D0D0D0;")
        ribbon_layout.addWidget(separator2)

        # Navigation Section
        nav_section = self.create_ribbon_section("Navigation", [
            ("Previous", FIF.LEFT_ARROW, self.previous_page),
            ("Next", FIF.RIGHT_ARROW, self.next_page),
        ])
        ribbon_layout.addWidget(nav_section)

        # Add page info
        self.page_info_label = QLabel("No document")
        self.page_info_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                background-color: transparent;
                padding: 5px;
            }
        """)
        ribbon_layout.addWidget(self.page_info_label)

        ribbon_layout.addStretch()

        # Home button
        home_button = ToolButton(FIF.HOME)
        home_button.setText("Home")
        home_button.setStyleSheet("""
            ToolButton {
                background-color: #0078D4;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                padding: 8px 16px;
            }
            ToolButton:hover {
                background-color: #106EBE;
            }
        """)
        home_button.clicked.connect(self.go_home)
        ribbon_layout.addWidget(home_button)

        parent_layout.addWidget(ribbon_card)

    def create_ribbon_section(self, title, buttons):
        """Create a section of the ribbon with buttons."""
        from qfluentwidgets import CaptionLabel, ToolButton

        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(5)

        # Section title
        title_label = CaptionLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            CaptionLabel {
                color: #666666;
                font-size: 11px;
                font-weight: 600;
                background-color: transparent;
                margin-bottom: 5px;
            }
        """)
        section_layout.addWidget(title_label)

        # Buttons container
        buttons_container = QHBoxLayout()
        buttons_container.setSpacing(5)

        for text, icon, callback in buttons:
            button = ToolButton(icon)
            button.setText(text)
            button.setFixedSize(60, 50)
            button.setStyleSheet("""
                ToolButton {
                    background-color: transparent;
                    border: 1px solid transparent;
                    border-radius: 4px;
                    font-size: 10px;
                    color: #333333;
                    padding: 2px;
                }
                ToolButton:hover {
                    background-color: #E8E8E8;
                    border: 1px solid #D0D0D0;
                }
                ToolButton:pressed {
                    background-color: #D0D0D0;
                }
            """)
            button.clicked.connect(callback)
            buttons_container.addWidget(button)

        section_layout.addLayout(buttons_container)
        return section_widget

    def apply_comprehensive_styling(self):
        """Apply comprehensive styling to ensure visibility in all themes."""
        from qfluentwidgets import isDarkTheme

        # Apply global stylesheet with fallback colors
        global_style = """
            QWidget {
                font-family: 'Segoe UI', 'Segoe UI Variable', Tahoma, Arial, sans-serif;
                font-size: 14px;
            }

            /* Ensure all text is visible with high contrast */
            QLabel {
                color: #000000;
                background-color: transparent;
            }

            /* Card styling with proper borders and backgrounds */
            CardWidget {
                background-color: #FFFFFF;
                border: 2px solid #D0D0D0;
                border-radius: 8px;
            }

            /* Button styling with proper contrast */
            PrimaryPushButton {
                color: #FFFFFF;
                font-weight: 600;
                border: none;
                border-radius: 6px;
            }

            /* InfoBar styling */
            InfoBar {
                background-color: #F0F0F0;
                border: 1px solid #CCCCCC;
                color: #000000;
            }
        """

        # Apply theme-specific overrides with improved contrast
        if isDarkTheme():
            global_style += """
                QWidget {
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                }
                QLabel {
                    color: #FFFFFF;
                }
                CardWidget {
                    background-color: #2D2D2D;
                    border: 2px solid #404040;
                }
                TitleLabel {
                    color: #FFFFFF !important;
                }
                BodyLabel {
                    color: #E0E0E0 !important;
                }
                CaptionLabel {
                    color: #B0B0B0 !important;
                }
                QScrollArea {
                    background-color: #1E1E1E;
                    border: 1px solid #404040;
                }
                QScrollArea QLabel {
                    background-color: #2D2D2D;
                    border: 1px solid #404040;
                    color: #E0E0E0;
                }
            """
        else:
            global_style += """
                QWidget {
                    background-color: #F8F8F8;
                    color: #000000;
                }
                QLabel {
                    color: #000000;
                }
                CardWidget {
                    background-color: #FFFFFF;
                    border: 2px solid #E0E0E0;
                }
                TitleLabel {
                    color: #000000 !important;
                }
                BodyLabel {
                    color: #333333 !important;
                }
                CaptionLabel {
                    color: #666666 !important;
                }
                QScrollArea {
                    background-color: #F8F8F8;
                    border: 1px solid #E0E0E0;
                }
                QScrollArea QLabel {
                    background-color: #FFFFFF;
                    border: 1px solid #E0E0E0;
                    color: #333333;
                }
            """

        self.setStyleSheet(global_style)

    def open_file(self):
        """Open a document file."""
        from PyQt5.QtWidgets import QFileDialog
        from qfluentwidgets import InfoBar, InfoBarIcon, InfoBarPosition

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            "",
            "All Supported (*.pdf *.epub *.mobi);;PDF Files (*.pdf);;EPUB Files (*.epub);;MOBI Files (*.mobi)"
        )

        if file_path:
            self.load_document(file_path)

    def load_document(self, file_path):
        """Load and display a document."""
        from qfluentwidgets import InfoBar, InfoBarIcon

        try:
            # Import document manager
            from readers.document_manager import DocumentManager

            if not self.document_manager:
                self.document_manager = DocumentManager()

            # Load the document
            self.current_document = self.document_manager.load_document(file_path)
            self.current_page = 0

            # Display the document
            self.display_current_page()

            # Switch to document view
            self.stacked_widget.setCurrentIndex(1)

            # Show success message
            info_bar = InfoBar(
                icon=InfoBarIcon.SUCCESS,
                title="Document Loaded",
                content=f"Successfully opened: {Path(file_path).name}",
                orient=Qt.Horizontal,
                isClosable=True,
                duration=3000,
                parent=self
            )
            info_bar.show()

        except Exception as e:
            # Show error message
            info_bar = InfoBar(
                icon=InfoBarIcon.ERROR,
                title="Error Loading Document",
                content=f"Failed to load document: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                duration=5000,
                parent=self
            )
            info_bar.show()

    def display_current_page(self):
        """Display the current page of the document."""
        if not self.current_document:
            return

        try:
            # For PDF documents, get the page as a pixmap
            if hasattr(self.current_document, 'get_page'):
                pixmap = self.current_document.get_page(self.current_page)
                self.document_label.setPixmap(pixmap)
                self.document_label.setText("")

                # Update window title and page info
                page_count = self.current_document.get_page_count()
                self.setWindowTitle(f"Modern EBook Reader - Page {self.current_page + 1} of {page_count}")
                self.update_page_info()

            # For text-based documents (EPUB, MOBI), get text content
            elif hasattr(self.current_document, 'get_page_text'):
                text = self.current_document.get_page_text(self.current_page)
                self.document_label.setText(text)
                self.document_label.setPixmap(QPixmap())  # Clear any existing pixmap

                # Update styling for text display
                self.document_label.setStyleSheet("""
                    QLabel {
                        background-color: #FFFFFF;
                        border: 1px solid #E0E0E0;
                        padding: 30px;
                        font-size: 14px;
                        color: #333333;
                        line-height: 1.6;
                    }
                """)
                self.document_label.setWordWrap(True)
                self.document_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        except Exception as e:
            self.document_label.setText(f"Error displaying page: {str(e)}")
            self.document_label.setPixmap(QPixmap())

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

        if isDarkTheme():
            self.document_label.setStyleSheet("""
                QLabel {
                    background-color: #2D2D2D;
                    border: 1px solid #404040;
                    padding: 30px;
                    font-size: 14px;
                    color: #E0E0E0;
                    line-height: 1.6;
                }
            """)
        else:
            self.document_label.setStyleSheet("""
                QLabel {
                    background-color: #FFFFFF;
                    border: 1px solid #E0E0E0;
                    padding: 30px;
                    font-size: 14px;
                    color: #333333;
                    line-height: 1.6;
                }
            """)

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
        if self.current_document and self.current_page > 0:
            self.current_page -= 1
            self.display_current_page()
            self.update_page_info()

    def next_page(self):
        """Go to next page."""
        if self.current_document:
            page_count = self.current_document.get_page_count()
            if self.current_page < page_count - 1:
                self.current_page += 1
                self.display_current_page()
                self.update_page_info()

    def go_home(self):
        """Return to home screen."""
        self.stacked_widget.setCurrentIndex(0)
        self.setWindowTitle("Modern EBook Reader - Fluent Design")

    def update_page_info(self):
        """Update the page information display."""
        if self.current_document and hasattr(self, 'page_info_label'):
            page_count = self.current_document.get_page_count()
            self.page_info_label.setText(f"Page {self.current_page + 1} of {page_count}")
        elif hasattr(self, 'page_info_label'):
            self.page_info_label.setText("No document")


def main():
    """Main application entry point."""
    # Create QApplication first
    app = QApplication(sys.argv)
    app.setApplicationName("Modern EBook Reader")
    
    # Initialize Fluent Design theme with explicit light theme for better visibility
    from qfluentwidgets import setTheme, Theme, setThemeColor, isDarkTheme

    # Force light theme initially to ensure visibility
    setTheme(Theme.LIGHT)
    setThemeColor('#0078D4')  # Microsoft Blue

    print(f"Theme set to: {'Dark' if isDarkTheme() else 'Light'}")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    print("✅ Fluent Design application started successfully!")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
