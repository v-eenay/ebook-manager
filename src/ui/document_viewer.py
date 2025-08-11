"""
Revolutionary Document Viewer - Completely New UI Design
A bold, modern interface with dark theme, neon accents, and futuristic styling.
"""

# Prefer PyQt5 if available to match the main application binding; fallback to PyQt6
try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QScrollArea, QFrame, QPushButton, QSlider,
                                QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy,
                                QStackedWidget, QTextEdit, QGraphicsView, QGraphicsScene,
                                QGraphicsPixmapItem)
    from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect
    from PyQt5.QtGui import (QFont, QFontMetrics, QPalette, QLinearGradient, QBrush, QPainter,
                            QColor, QPen, QPixmap, QIcon)
    QT_VERSION = 5
except ImportError:
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QScrollArea, QFrame, QPushButton, QSlider,
                                QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy,
                                QStackedWidget, QTextEdit, QGraphicsView, QGraphicsScene,
                                QGraphicsPixmapItem)
    from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect
    from PyQt6.QtGui import (QFont, QFontMetrics, QPalette, QLinearGradient, QBrush, QPainter,
                            QColor, QPen, QPixmap, QIcon)
    QT_VERSION = 6

# Logger (no Qt dependency)
try:
    from utils.logger import setup_logging
    logger = setup_logging()
except Exception:
    import logging
    logger = logging.getLogger("ebook_reader")

# Lazy import QPixmap and QImage to avoid early initialization issues
def _get_qt_graphics():
    """Get QPixmap and QImage classes when needed."""
    if QT_VERSION == 6:
        from PyQt6.QtGui import QPixmap, QImage
    else:
        from PyQt5.QtGui import QPixmap, QImage
    return QPixmap, QImage


class FuturisticPageViewer(QWidget):
    """Revolutionary page viewer with dark theme and neon accents."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page_num = 0
        self.total_pages = 0
        self.setup_futuristic_ui()

    def setup_futuristic_ui(self):
        """Setup the futuristic dark interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create neon page indicator
        self.page_indicator = self.create_neon_indicator()
        layout.addWidget(self.page_indicator)

        # Create content area with dark theme
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        # Apply dark futuristic styling
        self.apply_dark_theme()

        layout.addWidget(self.content_area)

    def create_neon_indicator(self):
        """Create a neon-style page indicator."""
        indicator = QLabel("Ready to Read")
        indicator.setAlignment(Qt.AlignCenter)
        indicator.setFixedHeight(50)

        indicator.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: #00ff88;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #00ff88;
                border-radius: 25px;
                margin: 10px;
                padding: 10px;
                text-shadow: 0 0 10px #00ff88;
                letter-spacing: 2px;
            }
        """)

        return indicator

    def apply_dark_theme(self):
        """Apply futuristic dark theme styling."""
        self.setStyleSheet("""
            FuturisticPageViewer {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f0f23, stop:1 #1a1a2e);
            }
        """)

        self.content_area.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #16213e, stop:1 #0f0f23);
                border: 1px solid #00ff88;
                border-radius: 15px;
                margin: 15px;
            }
        """)

    def update_indicator(self, page_num, total_pages):
        """Update the neon indicator with current page info."""
        self.current_page_num = page_num
        self.total_pages = total_pages

        # Cycle through different neon colors
        colors = ['#00ff88', '#ff0080', '#0080ff', '#ff8000', '#8000ff']
        color = colors[page_num % len(colors)]

        self.page_indicator.setText(f"◆ PAGE {page_num + 1} OF {total_pages} ◆")
        self.page_indicator.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: {color};
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid {color};
                border-radius: 25px;
                margin: 10px;
                padding: 10px;
                text-shadow: 0 0 10px {color};
                letter-spacing: 2px;
            }}
        """)


class DocumentViewer(QWidget):
    """Revolutionary document viewer with completely new dark UI design."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_document = None
        self.current_page = 0
        self.page_viewers = []

        try:
            self.init_revolutionary_ui()
        except Exception as e:
            logger.exception("Failed to initialize revolutionary document viewer: %s", e)
            self.create_simple_fallback(e)

    def init_revolutionary_ui(self):
        """Initialize the completely new revolutionary dark UI."""
        # Main dark layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create futuristic control panel
        self.create_control_panel()
        main_layout.addWidget(self.control_panel)

        # Create main viewing area with dark theme
        self.viewing_area = QStackedWidget()
        self.viewing_area.setStyleSheet("""
            QStackedWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f0f23, stop:1 #1a1a2e);
                border: 2px solid #00ff88;
                border-radius: 20px;
                margin: 10px;
            }
        """)

        # Create welcome screen
        self.create_futuristic_welcome()

        main_layout.addWidget(self.viewing_area)

        # Apply revolutionary theme
        self.apply_revolutionary_theme()

    def create_simple_fallback(self, error):
        """Create a simple fallback UI if initialization fails."""
        try:
            layout = QVBoxLayout(self)
            error_label = QLabel(f"Viewer initialization failed: {error}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setWordWrap(True)
            error_label.setStyleSheet("""
                QLabel {
                    background: #2d2d2d;
                    color: #ff6b6b;
                    padding: 20px;
                    border-radius: 10px;
                    font-size: 14px;
                }
            """)
            layout.addWidget(error_label)
        except Exception:
            pass

    def create_control_panel(self):
        """Create a futuristic control panel with neon styling."""
        self.control_panel = QWidget()
        self.control_panel.setFixedHeight(80)

        panel_layout = QHBoxLayout(self.control_panel)
        panel_layout.setContentsMargins(20, 10, 20, 10)
        panel_layout.setSpacing(20)

        # Document title with neon glow
        self.doc_title = QLabel("◆ NO DOCUMENT LOADED ◆")
        self.doc_title.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: #00ff88;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #00ff88;
                border-radius: 15px;
                padding: 15px 25px;
                text-shadow: 0 0 15px #00ff88;
                letter-spacing: 1px;
            }
        """)

        # Progress slider with neon styling
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(100)
        self.progress_slider.setValue(0)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 2px solid #0080ff;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #0f0f23);
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0080ff, stop:1 #00ff88);
                border: 2px solid #ffffff;
                width: 20px;
                margin: -8px 0;
                border-radius: 12px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00ff88, stop:1 #0080ff);
                box-shadow: 0 0 10px #00ff88;
            }
        """)

        panel_layout.addWidget(self.doc_title)
        panel_layout.addWidget(self.progress_slider, 1)

        # Apply control panel styling
        self.control_panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #16213e, stop:1 #0f0f23);
                border-bottom: 3px solid #00ff88;
            }
        """)

    def create_futuristic_welcome(self):
        """Create a futuristic welcome screen with animated elements."""
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(50, 50, 50, 50)
        welcome_layout.setSpacing(30)

        # Animated title with neon effect
        title = QLabel("◆ QUANTUM READER ◆")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #00ff88;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 42px;
                font-weight: bold;
                text-shadow: 0 0 20px #00ff88, 0 0 40px #00ff88;
                letter-spacing: 4px;
                margin: 30px;
            }
        """)

        # Subtitle with different neon color
        subtitle = QLabel("▼ INITIALIZE DOCUMENT PROTOCOL ▼")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #ff0080;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 18px;
                font-weight: bold;
                text-shadow: 0 0 15px #ff0080;
                letter-spacing: 2px;
                margin: 20px;
            }
        """)

        # Status indicator
        status = QLabel("STATUS: AWAITING INPUT")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("""
            QLabel {
                color: #0080ff;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                font-weight: bold;
                text-shadow: 0 0 10px #0080ff;
                letter-spacing: 1px;
                border: 2px solid #0080ff;
                border-radius: 20px;
                padding: 15px 30px;
                margin: 20px;
            }
        """)

        welcome_layout.addWidget(title)
        welcome_layout.addWidget(subtitle)
        welcome_layout.addWidget(status)

        # Add to viewing area
        self.viewing_area.addWidget(welcome_widget)

    def apply_revolutionary_theme(self):
        """Apply the revolutionary dark theme to the entire viewer."""
        self.setStyleSheet("""
            DocumentViewer {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f0f23, stop:1 #1a1a2e);
                color: #ffffff;
            }
        """)

    def apply_scroll_area_styling(self):
        """Apply modern styling to the scroll area."""
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fafbfc, stop:1 #f1f3f4);
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6fd8, stop:1 #6a4190);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

    def apply_modern_theme(self):
        """Apply the overall modern theme to the viewer."""
        self.setStyleSheet("""
            DocumentViewer {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fafbfc, stop:1 #f1f3f4);
            }
        """)

    def create_welcome_card(self):
        """Create a beautiful welcome card when no document is loaded."""
        self.welcome_card = QWidget()
        self.welcome_card.setFixedSize(600, 400)

        welcome_layout = QVBoxLayout(self.welcome_card)
        welcome_layout.setContentsMargins(40, 40, 40, 40)
        welcome_layout.setSpacing(20)

        # Welcome title with gradient text effect
        title = QLabel("📚 Ready to Read")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #667eea;
                font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 10px;
            }
        """)

        # Subtitle
        subtitle = QLabel("Open a document to begin your reading journey")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
                font-size: 16px;
                font-weight: 400;
                line-height: 1.5;
            }
        """)

        welcome_layout.addWidget(title)
        welcome_layout.addWidget(subtitle)

        # Apply modern card styling
        self.welcome_card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid #e9ecef;
                border-radius: 20px;
            }
        """)

        self.pages_layout.addWidget(self.welcome_card)

    def load_document(self, document):
        """Load a document with revolutionary futuristic interface."""
        self.current_document = document
        self.current_page = 0

        # Update control panel
        if hasattr(self, 'doc_title'):
            self.doc_title.setText("◆ LOADING DOCUMENT ◆")

        self.clear_viewing_area()
        self.display_document_revolutionary()

    def clear_viewing_area(self):
        """Clear the viewing area for new content."""
        # Clear all widgets from the stacked widget
        while self.viewing_area.count() > 0:
            widget = self.viewing_area.widget(0)
            self.viewing_area.removeWidget(widget)
            widget.deleteLater()

        self.page_viewers = []

    def display_document_revolutionary(self):
        """Display document with revolutionary futuristic design."""
        if not self.current_document:
            self.create_futuristic_welcome()
            return

        try:
            page_count = self.current_document.get_page_count()
            logger.info("Displaying %d pages with revolutionary design", page_count)

            # Update control panel
            if hasattr(self, 'doc_title'):
                self.doc_title.setText(f"◆ DOCUMENT LOADED: {page_count} PAGES ◆")

            if hasattr(self, 'progress_slider'):
                self.progress_slider.setMaximum(page_count)
                self.progress_slider.setValue(1)

            # Create page viewers for each page
            for page_num in range(page_count):
                page_viewer = FuturisticPageViewer(self)
                page_viewer.update_indicator(page_num, page_count)

                # Add page content
                content_widget = self.create_futuristic_page_content(page_num)
                if content_widget:
                    page_viewer.content_layout.addWidget(content_widget)

                self.viewing_area.addWidget(page_viewer)
                self.page_viewers.append(page_viewer)

            # Show first page
            if self.page_viewers:
                self.viewing_area.setCurrentIndex(0)

        except Exception as e:
            logger.exception("Error displaying document with revolutionary design: %s", e)
            self.create_futuristic_error(str(e))

    def create_futuristic_error(self, error_message):
        """Create a futuristic error display."""
        error_widget = QWidget()
        error_layout = QVBoxLayout(error_widget)
        error_layout.setContentsMargins(50, 50, 50, 50)

        error_title = QLabel("◆ SYSTEM ERROR ◆")
        error_title.setAlignment(Qt.AlignCenter)
        error_title.setStyleSheet("""
            QLabel {
                color: #ff0080;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 28px;
                font-weight: bold;
                text-shadow: 0 0 20px #ff0080;
                letter-spacing: 3px;
                margin: 20px;
            }
        """)

        error_details = QLabel(f"ERROR: {error_message}")
        error_details.setAlignment(Qt.AlignCenter)
        error_details.setWordWrap(True)
        error_details.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                border: 2px solid #ff0080;
                border-radius: 15px;
                padding: 20px;
                margin: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #0f0f23);
            }
        """)

        error_layout.addWidget(error_title)
        error_layout.addWidget(error_details)

        self.viewing_area.addWidget(error_widget)

    def create_futuristic_page_content(self, page_num):
        """Create futuristic page content with neon styling."""
        try:
            # Handle PDF documents
            if hasattr(self.current_document, 'get_page_image_data'):
                return self.create_futuristic_pdf_page(page_num)
            # Handle text-based documents
            elif hasattr(self.current_document, 'get_page_text') or hasattr(self.current_document, 'get_page'):
                return self.create_futuristic_text_page(page_num)
            else:
                return self.create_unsupported_futuristic_page(page_num)

        except Exception as e:
            logger.exception("Error creating futuristic page content %d: %s", page_num, e)
            return self.create_page_error_futuristic(page_num, str(e))

    def create_futuristic_pdf_page(self, page_num):
        """Create a futuristic PDF page display."""
        try:
            # Get Qt graphics classes
            QPixmap, QImage = _get_qt_graphics()

            # Get image data from PDF reader
            img_data, _, _ = self.current_document.get_page_image_data(page_num)

            # Create QImage from raw data
            qimg = QImage.fromData(img_data)
            if qimg.isNull():
                raise Exception("Failed to create QImage from PDF data")

            # Create QPixmap from QImage
            pixmap = QPixmap.fromImage(qimg)
            if pixmap.isNull():
                raise Exception("Failed to create QPixmap from QImage")

            # Create futuristic PDF container
            pdf_container = QWidget()
            pdf_layout = QVBoxLayout(pdf_container)
            pdf_layout.setContentsMargins(20, 20, 20, 20)

            # Create label to display the PDF page
            page_label = QLabel()
            page_label.setPixmap(pixmap)
            page_label.setAlignment(Qt.AlignCenter)
            page_label.setToolTip(f"PDF Page {page_num + 1}")

            # Futuristic PDF styling with neon borders
            page_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #1a1a2e, stop:1 #0f0f23);
                    border: 3px solid #00ff88;
                    border-radius: 15px;
                    padding: 15px;
                    margin: 10px;
                }
            """)

            pdf_layout.addWidget(page_label)
            return pdf_container

        except Exception as e:
            logger.exception("Error creating futuristic PDF page %d: %s", page_num, e)
            return self.create_page_error_futuristic(page_num, "PDF rendering error")

    def create_futuristic_text_page(self, page_num):
        """Create a futuristic text page display."""
        try:
            # Get text content
            if hasattr(self.current_document, 'get_page_text'):
                text = self.current_document.get_page_text(page_num)
            else:
                text = self.current_document.get_page(page_num)

            # Create futuristic text container
            text_container = QWidget()
            text_layout = QVBoxLayout(text_container)
            text_layout.setContentsMargins(20, 20, 20, 20)

            # Create styled text display
            text_display = QTextEdit()
            text_display.setPlainText(text)
            text_display.setReadOnly(True)

            # Futuristic text styling with neon accents
            text_display.setStyleSheet("""
                QTextEdit {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #1a1a2e, stop:1 #0f0f23);
                    color: #ffffff;
                    border: 3px solid #0080ff;
                    border-radius: 15px;
                    padding: 20px;
                    margin: 10px;
                    font-family: 'Segoe UI Variable', 'Segoe UI', Georgia, serif;
                    font-size: 16px;
                    line-height: 1.8;
                    selection-background-color: #00ff88;
                    selection-color: #000000;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #0f0f23;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background: #0080ff;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #00ff88;
                }
            """)

            text_layout.addWidget(text_display)
            return text_container

        except Exception as e:
            logger.exception("Error creating futuristic text page %d: %s", page_num, e)
            return self.create_page_error_futuristic(page_num, "Text reading error")

    def create_unsupported_futuristic_page(self, page_num):
        """Create a futuristic unsupported format display."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)

        icon_label = QLabel("⚠")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                color: #ff8000;
                font-size: 64px;
                text-shadow: 0 0 20px #ff8000;
                margin: 20px;
            }
        """)

        message_label = QLabel(f"◆ UNSUPPORTED FORMAT - PAGE {page_num + 1} ◆")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("""
            QLabel {
                color: #ff8000;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 16px;
                font-weight: bold;
                text-shadow: 0 0 10px #ff8000;
                letter-spacing: 1px;
                border: 2px solid #ff8000;
                border-radius: 15px;
                padding: 20px;
                margin: 20px;
            }
        """)

        layout.addWidget(icon_label)
        layout.addWidget(message_label)

        return container

    def create_page_error_futuristic(self, page_num, error_message):
        """Create a futuristic page error display."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)

        icon_label = QLabel("✖")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                color: #ff0080;
                font-size: 48px;
                text-shadow: 0 0 20px #ff0080;
                margin: 20px;
            }
        """)

        title_label = QLabel(f"◆ ERROR - PAGE {page_num + 1} ◆")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #ff0080;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 18px;
                font-weight: bold;
                text-shadow: 0 0 15px #ff0080;
                letter-spacing: 2px;
                margin: 10px;
            }
        """)

        error_label = QLabel(error_message)
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setWordWrap(True)
        error_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                border: 2px solid #ff0080;
                border-radius: 10px;
                padding: 15px;
                margin: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #0f0f23);
            }
        """)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(error_label)

        return container

    def next_page(self):
        """Setup smooth animations for UI interactions."""
        # Animation for scroll position changes
        self.scroll_animation = QPropertyAnimation(self.scroll_area.verticalScrollBar(), b"value")
        self.scroll_animation.setDuration(300)
        self.scroll_animation.setEasingCurve(QEasingCurve.OutCubic)

    def create_modern_page_content(self, page_num):
        """Create modern, styled content for a single page."""
        try:
            # Handle PDF documents with modern styling
            if hasattr(self.current_document, 'get_page_image_data'):
                return self.create_modern_pdf_page(page_num)
            # Handle text-based documents with modern styling
            elif hasattr(self.current_document, 'get_page_text') or hasattr(self.current_document, 'get_page'):
                return self.create_modern_text_page(page_num)
            else:
                return self.create_unsupported_format_widget(page_num)

        except Exception as e:
            logger.exception("Error creating modern page content %d: %s", page_num, e)
            return self.create_page_error_widget(page_num, str(e))

    def create_modern_pdf_page(self, page_num):
        """Create a modern, styled PDF page widget."""
        try:
            # Get Qt graphics classes
            QPixmap, QImage = _get_qt_graphics()

            # Get image data from PDF reader
            img_data, _, _ = self.current_document.get_page_image_data(page_num)

            # Create QImage from raw data
            qimg = QImage.fromData(img_data)
            if qimg.isNull():
                raise Exception("Failed to create QImage from PDF data")

            # Create QPixmap from QImage
            pixmap = QPixmap.fromImage(qimg)
            if pixmap.isNull():
                raise Exception("Failed to create QPixmap from QImage")

            # Create modern page container
            page_container = QWidget()
            page_layout = QVBoxLayout(page_container)
            page_layout.setContentsMargins(0, 0, 0, 0)

            # Create label to display the PDF page
            page_label = QLabel()
            page_label.setPixmap(pixmap)
            page_label.setAlignment(Qt.AlignCenter)
            page_label.setToolTip(f"PDF Page {page_num + 1}")

            # Modern PDF page styling with subtle gradients
            page_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #fafafa);
                    border: 2px solid #e3f2fd;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 5px;
                }
            """)

            page_layout.addWidget(page_label)
            return page_container

        except Exception as e:
            logger.exception("Error creating modern PDF page %d: %s", page_num, e)
            return self.create_page_error_widget(page_num, "PDF rendering error")

    def create_modern_text_page(self, page_num):
        """Create a modern, styled text page widget."""
        try:
            # Get text content
            if hasattr(self.current_document, 'get_page_text'):
                text = self.current_document.get_page_text(page_num)
            else:
                text = self.current_document.get_page(page_num)

            # Create modern text container
            text_container = QWidget()
            text_layout = QVBoxLayout(text_container)
            text_layout.setContentsMargins(0, 0, 0, 0)

            # Create styled text label
            text_label = QLabel(text)
            text_label.setWordWrap(True)
            text_label.setToolTip(f"Text Page {page_num + 1}")

            if QT_VERSION == 6:
                text_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            else:
                text_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

            # Modern text styling with beautiful typography
            text_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #fefefe, stop:1 #f8f9fa);
                    border: 2px solid #e8f5e8;
                    border-radius: 12px;
                    padding: 40px;
                    margin: 5px;
                    font-family: 'Segoe UI Variable', 'Segoe UI', Georgia, serif;
                    font-size: 15px;
                    color: #2d3436;
                    line-height: 1.7;
                    letter-spacing: 0.3px;
                }
            """)

            text_layout.addWidget(text_label)
            return text_container

        except Exception as e:
            logger.exception("Error creating modern text page %d: %s", page_num, e)
            return self.create_page_error_widget(page_num, "Text reading error")

    def create_unsupported_format_widget(self, page_num):
        """Create a widget for unsupported document formats."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)

        icon_label = QLabel("📄")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; margin-bottom: 15px;")

        message_label = QLabel(f"Page {page_num + 1}: Unsupported Format")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
                font-size: 16px;
                font-weight: 500;
            }
        """)

        layout.addWidget(icon_label)
        layout.addWidget(message_label)

        container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fff8e1, stop:1 #ffecb3);
                border: 2px solid #ffcc02;
                border-radius: 12px;
            }
        """)

        return container

    def create_page_error_widget(self, page_num, error_message):
        """Create a modern error widget for page loading failures."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)

        icon_label = QLabel("⚠️")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 36px; margin-bottom: 10px;")

        title_label = QLabel(f"Page {page_num + 1}: Loading Error")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #dc3545;
                font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 5px;
            }
        """)

        error_label = QLabel(error_message)
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setWordWrap(True)
        error_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
                font-size: 12px;
            }
        """)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(error_label)

        container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fff5f5, stop:1 #ffe6e6);
                border: 2px solid #f8d7da;
                border-radius: 12px;
            }
        """)

        return container

    def next_page(self):
        """Navigate to the next page with futuristic transition."""
        if not self.current_document or not hasattr(self, 'page_viewers') or not self.page_viewers:
            return False

        page_count = self.current_document.get_page_count()
        if self.current_page < page_count - 1:
            self.current_page += 1
            self.viewing_area.setCurrentIndex(self.current_page)
            self.update_futuristic_progress()
            return True
        return False

    def previous_page(self):
        """Navigate to the previous page with futuristic transition."""
        if not self.current_document or not hasattr(self, 'page_viewers') or not self.page_viewers:
            return False

        if self.current_page > 0:
            self.current_page -= 1
            self.viewing_area.setCurrentIndex(self.current_page)
            self.update_futuristic_progress()
            return True
        return False

    def update_futuristic_progress(self):
        """Update the futuristic progress indicators."""
        if hasattr(self, 'progress_slider') and self.current_document:
            page_count = self.current_document.get_page_count()
            self.progress_slider.setValue(self.current_page + 1)

            # Update control panel title with current page
            if hasattr(self, 'doc_title'):
                colors = ['#00ff88', '#ff0080', '#0080ff', '#ff8000', '#8000ff']
                color = colors[self.current_page % len(colors)]

                self.doc_title.setText(f"◆ PAGE {self.current_page + 1} OF {page_count} ◆")
                self.doc_title.setStyleSheet(f"""
                    QLabel {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #1a1a2e, stop:1 #16213e);
                        color: {color};
                        font-family: 'Consolas', 'Courier New', monospace;
                        font-size: 18px;
                        font-weight: bold;
                        border: 2px solid {color};
                        border-radius: 15px;
                        padding: 15px 25px;
                        text-shadow: 0 0 15px {color};
                        letter-spacing: 1px;
                    }}
                """)

    def get_current_page(self):
        """Get the current page number (1-based)."""
        return self.current_page + 1

    def get_page_count(self):
        """Get the total number of pages."""
        if self.current_document and hasattr(self.current_document, 'get_page_count'):
            return self.current_document.get_page_count()
        return 0

    def update_theme_styling(self, is_dark_theme=False):
        """Update styling based on theme."""
        if is_dark_theme:
            self.document_label.setStyleSheet("""
                QLabel {
                    background-color: #2D2D2D;
                    border: 1px solid #404040;
                    padding: 20px;
                    font-size: 14px;
                    color: #E0E0E0;
                    line-height: 1.6;
                }
            """)
            self.scroll_area.setStyleSheet("""
                QScrollArea {
                    background-color: #1E1E1E;
                    border: 1px solid #404040;
                }
            """)
        else:
            self.document_label.setStyleSheet("""
                QLabel {
                    background-color: #FFFFFF;
                    border: 1px solid #E0E0E0;
                    padding: 20px;
                    font-size: 14px;
                    color: #333333;
                    line-height: 1.6;
                }
            """)
            self.scroll_area.setStyleSheet("""
                QScrollArea {
                    background-color: #F8F8F8;
                    border: 1px solid #E0E0E0;
                }
            """)
