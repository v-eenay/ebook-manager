#!/usr/bin/env python3
"""
Direct main application with Fluent Design - bypassing src structure
"""

import sys
from pathlib import Path
import logging
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QFileDialog, QLabel, QScrollArea, QStackedWidget)
from PyQt5.QtCore import Qt
# QPixmap import moved to safe_create_pixmap method to avoid early initialization

# Add the src directory to the Python path BEFORE importing project modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Initialize logging early
try:
    from utils.logger import setup_logging
    logger = setup_logging()
except Exception as _e:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ebook_reader")
    logger.error("Failed to initialize file logger: %s", _e)

class MainWindow(QWidget):
    """Direct main window with Fluent Design components."""

    def __init__(self):
        super().__init__()
        self.current_document = None
        self.current_page = 0
        self.document_manager = None
        try:
            self.init_ui()
            self.apply_comprehensive_styling()
        except Exception as e:
            logger.exception("Error during MainWindow initialization: %s", e)
            raise

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

        # Create document viewer widget (lazy import to avoid early widget creation)
        self.document_viewer = None
        self.document_viewer_container = QWidget()
        self.document_viewer_layout = QVBoxLayout(self.document_viewer_container)
        self.document_viewer_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.document_viewer_container)

        self.stacked_widget.addWidget(document_widget)

    def ensure_document_viewer(self):
        """Ensure document viewer is created when needed."""
        if self.document_viewer is None:
            logger.info("Creating DocumentViewer...")
            from ui.document_viewer import DocumentViewer
            self.document_viewer = DocumentViewer()
            self.document_viewer_layout.addWidget(self.document_viewer)
            logger.info("DocumentViewer created and added to layout")

    def create_ribbon_toolbar(self, parent_layout):
        """Create Microsoft Office-style ribbon toolbar with proper spacing."""
        from qfluentwidgets import (PrimaryPushButton, PushButton, ToolButton,
                                   FluentIcon as FIF, CardWidget)

        # Create ribbon container with proper height for Windows ribbon style
        ribbon_card = CardWidget()
        ribbon_card.setFixedHeight(120)
        try:
            ribbon_card.setStyleSheet("""
                CardWidget {
                    background-color: #F8F8F8;
                    border: none;
                    border-bottom: 2px solid #E0E0E0;
                    border-radius: 0px;
                    padding: 0px;
                }
            """)
        except Exception as e:
            logger.warning("Failed to apply ribbon styles: %s", e)

        ribbon_layout = QHBoxLayout(ribbon_card)
        ribbon_layout.setContentsMargins(15, 8, 15, 8)
        ribbon_layout.setSpacing(20)

        # File Operations Section
        file_section = self.create_ribbon_section("File", [
            ("Open", FIF.FOLDER, self.open_file),
            ("Close", FIF.CLOSE, self.close_document),
        ])
        ribbon_layout.addWidget(file_section)

        # Add vertical separator with proper styling
        separator1 = QWidget()
        separator1.setObjectName("separator")
        separator1.setFixedWidth(2)
        separator1.setFixedHeight(80)
        separator1.setStyleSheet("""
            QWidget[objectName="separator"] {
                background-color: #D0D0D0;
                border-radius: 1px;
                margin: 10px 5px;
            }
        """)
        ribbon_layout.addWidget(separator1)

        # View Controls Section
        view_section = self.create_ribbon_section("View", [
            ("Zoom In", FIF.ZOOM_IN, self.zoom_in),
            ("Zoom Out", FIF.ZOOM_OUT, self.zoom_out),
            ("Fit Window", FIF.FIT_PAGE, self.fit_to_window),
        ])
        ribbon_layout.addWidget(view_section)

        # Add vertical separator with proper styling
        separator2 = QWidget()
        separator2.setObjectName("separator")
        separator2.setFixedWidth(2)
        separator2.setFixedHeight(80)
        separator2.setStyleSheet("""
            QWidget[objectName="separator"] {
                background-color: #D0D0D0;
                border-radius: 1px;
                margin: 10px 5px;
            }
        """)
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
        """Create a section of the ribbon with properly spaced buttons."""
        from qfluentwidgets import CaptionLabel, ToolButton

        section_widget = QWidget()
        section_widget.setMinimumWidth(len(buttons) * 75 + 20)  # Ensure adequate width
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(10, 5, 10, 5)
        section_layout.setSpacing(8)

        # Buttons container first (larger visual element)
        buttons_container = QHBoxLayout()
        buttons_container.setSpacing(8)
        buttons_container.setContentsMargins(0, 0, 0, 0)

        for text, icon, callback in buttons:
            button = ToolButton(icon)
            button.setText(text)
            button.setFixedSize(65, 60)  # Larger buttons for better ribbon appearance
            button.setStyleSheet("""
                ToolButton {
                    background-color: transparent;
                    border: 1px solid transparent;
                    border-radius: 6px;
                    font-size: 9px;
                    color: #333333;
                    padding: 4px 2px;
                    text-align: center;
                }
                ToolButton:hover {
                    background-color: #E8E8E8;
                    border: 1px solid #D0D0D0;
                }
                ToolButton:pressed {
                    background-color: #D0D0D0;
                    border: 1px solid #B0B0B0;
                }
            """)
            button.clicked.connect(callback)
            buttons_container.addWidget(button)

        section_layout.addLayout(buttons_container)

        # Section title at bottom (ribbon style)
        title_label = CaptionLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            CaptionLabel {
                color: #666666;
                font-size: 10px;
                font-weight: 600;
                background-color: transparent;
                margin-top: 2px;
                padding: 2px;
            }
        """)
        section_layout.addWidget(title_label)

        return section_widget

    def safe_create_pixmap(self, *args):
        """Safely create a QPixmap, handling QGuiApplication issues."""
        try:
            # Check if QGuiApplication is available
            app = QApplication.instance()
            if app is None:
                return None

            # Check if the application is properly initialized
            if not hasattr(app, 'exec'):
                return None

            # Import QPixmap only when safe
            from PyQt5.QtGui import QPixmap

            # Create QPixmap
            if args:
                pixmap = QPixmap(*args)
            else:
                pixmap = QPixmap()

            # Verify the pixmap was created successfully
            if pixmap.isNull():
                return None

            return pixmap

        except Exception as e:
            # Silently handle errors to prevent crashes
            return None

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

        # Apply theme-specific overrides with comprehensive component coverage
        if isDarkTheme():
            global_style += """
                /* Main window and widgets */
                QWidget {
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                }

                /* All label types */
                QLabel {
                    color: #FFFFFF;
                    background-color: transparent;
                }
                TitleLabel {
                    color: #FFFFFF !important;
                    background-color: transparent !important;
                }
                BodyLabel {
                    color: #E0E0E0 !important;
                    background-color: transparent !important;
                }
                CaptionLabel {
                    color: #B0B0B0 !important;
                    background-color: transparent !important;
                }

                /* Card widgets */
                CardWidget {
                    background-color: #2D2D2D !important;
                    border: 2px solid #404040 !important;
                    color: #FFFFFF !important;
                }

                /* Scroll areas and document display */
                QScrollArea {
                    background-color: #1E1E1E;
                    border: 1px solid #404040;
                }
                QScrollArea QLabel {
                    background-color: #2D2D2D !important;
                    border: 1px solid #404040 !important;
                    color: #E0E0E0 !important;
                }

                /* Buttons */
                PrimaryPushButton {
                    background-color: #0078D4 !important;
                    color: #FFFFFF !important;
                    border: none !important;
                }
                PrimaryPushButton:hover {
                    background-color: #106EBE !important;
                }

                /* Ribbon toolbar */
                ToolButton {
                    background-color: transparent !important;
                    color: #E0E0E0 !important;
                    border: 1px solid transparent !important;
                }
                ToolButton:hover {
                    background-color: #404040 !important;
                    border: 1px solid #555555 !important;
                }

                /* Separators */
                QWidget[objectName="separator"] {
                    background-color: #404040 !important;
                }
            """
        else:
            global_style += """
                /* Main window and widgets */
                QWidget {
                    background-color: #F8F8F8;
                    color: #000000;
                }

                /* All label types */
                QLabel {
                    color: #000000;
                    background-color: transparent;
                }
                TitleLabel {
                    color: #000000 !important;
                    background-color: transparent !important;
                }
                BodyLabel {
                    color: #333333 !important;
                    background-color: transparent !important;
                }
                CaptionLabel {
                    color: #666666 !important;
                    background-color: transparent !important;
                }

                /* Card widgets */
                CardWidget {
                    background-color: #FFFFFF !important;
                    border: 2px solid #E0E0E0 !important;
                    color: #000000 !important;
                }

                /* Scroll areas and document display */
                QScrollArea {
                    background-color: #F8F8F8;
                    border: 1px solid #E0E0E0;
                }
                QScrollArea QLabel {
                    background-color: #FFFFFF !important;
                    border: 1px solid #E0E0E0 !important;
                    color: #333333 !important;
                }

                /* Buttons */
                PrimaryPushButton {
                    background-color: #0078D4 !important;
                    color: #FFFFFF !important;
                    border: none !important;
                }
                PrimaryPushButton:hover {
                    background-color: #106EBE !important;
                }

                /* Ribbon toolbar */
                ToolButton {
                    background-color: transparent !important;
                    color: #333333 !important;
                    border: 1px solid transparent !important;
                }
                ToolButton:hover {
                    background-color: #E8E8E8 !important;
                    border: 1px solid #D0D0D0 !important;
                }

                /* Separators */
                QWidget[objectName="separator"] {
                    background-color: #D0D0D0 !important;
                }
            """

        self.setStyleSheet(global_style)

        # Force update all child widgets
        self.update_all_widgets()

    def update_all_widgets(self):
        """Force update all child widgets to apply new theme."""
        # Update all child widgets recursively
        for widget in self.findChildren(QWidget):
            widget.update()
            widget.repaint()

        # Update main window
        self.update()
        self.repaint()

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
        """Load and display a document with comprehensive error handling."""
        try:
            from qfluentwidgets import InfoBar, InfoBarIcon

            # Import document manager safely
            from readers.document_manager import DocumentManager

            if not self.document_manager:
                self.document_manager = DocumentManager()

            # Verify file exists and is supported
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            if not self.document_manager.is_supported(file_path):
                raise ValueError(f"Unsupported file format: {Path(file_path).suffix}")

            # Load the document with error handling
            try:
                self.current_document = self.document_manager.load_document(file_path)
                self.current_page = 0

                # Verify document loaded successfully
                if not self.current_document:
                    raise RuntimeError("Document loaded but returned None")

            except Exception as load_error:
                raise RuntimeError(f"Failed to load document: {str(load_error)}")

            # Switch to document view first
            self.stacked_widget.setCurrentIndex(1)

            # Ensure document viewer is created and load document
            try:
                self.ensure_document_viewer()
                self.document_viewer.load_document(self.current_document)
                self.update_page_info()
            except Exception as display_error:
                # If display fails, log error
                logger.exception("Error displaying document: %s", display_error)

            # Show success message
            try:
                page_count = getattr(self.current_document, 'page_count', 'unknown')
                if hasattr(self.current_document, 'get_page_count'):
                    page_count = self.current_document.get_page_count()

                info_bar = InfoBar(
                    icon=InfoBarIcon.SUCCESS,
                    title="Document Loaded",
                    content=f"Successfully opened: {Path(file_path).name} ({page_count} pages)",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    duration=3000,
                    parent=self
                )
                info_bar.show()
            except:
                # If info bar fails, continue silently
                pass

        except Exception as e:
            # Comprehensive error handling
            try:
                from qfluentwidgets import InfoBar, InfoBarIcon

                error_msg = str(e)
                if "QPixmap" in error_msg or "QGuiApplication" in error_msg:
                    error_msg = "Graphics initialization error. Please restart the application and try again."
                elif "FileNotFoundError" in str(type(e)):
                    error_msg = "File not found. Please check the file path and try again."
                elif "ValueError" in str(type(e)):
                    error_msg = "Unsupported file format. Please select a PDF, EPUB, or MOBI file."

                info_bar = InfoBar(
                    icon=InfoBarIcon.ERROR,
                    title="Error Loading Document",
                    content=f"Failed to load document: {error_msg}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    duration=5000,
                    parent=self
                )
                info_bar.show()
            except Exception:
                # If even error display fails, log to console logger
                logger.exception("Error loading document: %s", e)

            # Reset state on error
            self.current_document = None
            self.current_page = 0

    def display_current_page(self):
        """Display the current page of the document with comprehensive error handling."""
        if not self.current_document:
            self.document_label.setText("No document loaded")
            return

        try:
            # For PDF documents, get the page as a pixmap
            if hasattr(self.current_document, 'get_page'):
                try:
                    # Safely create QPixmap in main thread
                    pixmap = self.current_document.get_page(self.current_page)
                    if pixmap is not None:
                        self.document_label.setPixmap(pixmap)
                        self.document_label.setText("")

                        # Update window title and page info
                        try:
                            page_count = self.current_document.get_page_count()
                            self.setWindowTitle(f"Modern EBook Reader - Page {self.current_page + 1} of {page_count}")
                            self.update_page_info()
                        except:
                            # If page info update fails, continue
                            pass
                    else:
                        raise Exception("Failed to create page pixmap")

                except Exception as pixmap_error:
                    # Fallback to text display if QPixmap creation fails
                    error_text = f"Error rendering page {self.current_page + 1}: Graphics display unavailable.\n\nThe document is loaded but cannot be displayed visually. This may be due to graphics initialization issues."
                    self.document_label.setText(error_text)
                    # Clear any existing pixmap safely
                    try:
                        empty_pixmap = self.safe_create_pixmap()
                        if empty_pixmap is not None:
                            self.document_label.setPixmap(empty_pixmap)
                    except:
                        pass  # Ignore pixmap clearing errors
                    self.document_label.setWordWrap(True)
                    self.document_label.setAlignment(Qt.AlignCenter)

            # For text-based documents (EPUB, MOBI), get text content
            elif hasattr(self.current_document, 'get_page_text'):
                try:
                    text = self.current_document.get_page_text(self.current_page)
                    self.document_label.setText(text)
                    # Only clear pixmap if we can safely create an empty one
                    try:
                        empty_pixmap = self.safe_create_pixmap()
                        if empty_pixmap is not None:
                            self.document_label.setPixmap(empty_pixmap)
                    except:
                        pass  # Ignore pixmap clearing errors

                    # Update styling for text display
                    try:
                        self.update_document_styling()
                    except:
                        pass  # Ignore styling errors
                    self.document_label.setWordWrap(True)
                    self.document_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
                except Exception as text_error:
                    self.document_label.setText(f"Error reading page text: {str(text_error)}")
                    self.document_label.setWordWrap(True)
                    self.document_label.setAlignment(Qt.AlignCenter)
            else:
                self.document_label.setText("Document format not supported for display")
                self.document_label.setWordWrap(True)
                self.document_label.setAlignment(Qt.AlignCenter)

        except Exception as e:
            # Ultimate fallback
            error_text = f"Critical error displaying page: {str(e)}"
            try:
                self.document_label.setText(error_text)
                self.document_label.setWordWrap(True)
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
