"""
Modern Document Viewer Widget for EBook Reader
A vibrant, contemporary interface for displaying PDF, EPUB, and MOBI documents.
Features colorful design, smooth animations, and modern visual elements.
"""

# Prefer PyQt5 if available to match the main application binding; fallback to PyQt6
try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QScrollArea, QFrame, QPushButton, QProgressBar,
                                QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy)
    from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
    from PyQt5.QtGui import QFont, QFontMetrics, QPalette, QLinearGradient, QBrush, QPainter
    QT_VERSION = 5
except ImportError:
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QScrollArea, QFrame, QPushButton, QProgressBar,
                                QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy)
    from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
    from PyQt6.QtGui import QFont, QFontMetrics, QPalette, QLinearGradient, QBrush, QPainter
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


class ModernPageCard(QWidget):
    """A modern, colorful card widget for displaying document pages."""

    def __init__(self, page_num, total_pages, parent=None):
        super().__init__(parent)
        self.page_num = page_num
        self.total_pages = total_pages
        self.setup_card_ui()

    def setup_card_ui(self):
        """Setup the modern card interface with gradients and shadows."""
        self.setFixedWidth(800)  # Standard reading width

        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create page indicator with gradient background
        self.page_indicator = self.create_page_indicator()
        layout.addWidget(self.page_indicator)

        # Create content container with modern styling
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(25, 25, 25, 25)

        # Apply modern card styling with gradients and shadows
        self.apply_modern_styling()

        layout.addWidget(self.content_container)

    def create_page_indicator(self):
        """Create a colorful page indicator with gradient background."""
        indicator = QLabel(f"Page {self.page_num + 1} of {self.total_pages}")
        indicator.setAlignment(Qt.AlignCenter)
        indicator.setFixedHeight(45)

        # Modern gradient styling for page indicator
        gradient_colors = [
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2)",  # Purple-blue
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f093fb, stop:1 #f5576c)",  # Pink-red
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4facfe, stop:1 #00f2fe)",  # Blue-cyan
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #43e97b, stop:1 #38f9d7)",  # Green-cyan
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fa709a, stop:1 #fee140)",  # Pink-yellow
        ]

        gradient = gradient_colors[self.page_num % len(gradient_colors)]

        indicator.setStyleSheet(f"""
            QLabel {{
                background: {gradient};
                color: white;
                font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 600;
                border-radius: 22px;
                margin: 8px 20px;
                padding: 8px 20px;
                letter-spacing: 0.5px;
            }}
        """)

        return indicator

    def apply_modern_styling(self):
        """Apply modern styling with gradients and shadows to the card."""
        # Create shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(Qt.gray)

        # Apply shadow to content container
        self.content_container.setGraphicsEffect(shadow)

        # Modern card styling with subtle gradients
        self.content_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #fafbfc);
                border: 1px solid #e9ecef;
                border-radius: 16px;
            }
        """)


class DocumentViewer(QWidget):
    """Modern, vibrant document viewer with contemporary design elements."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_document = None
        self.current_page = 0
        self.page_cards = []
        self.is_dark_theme = False

        try:
            self.init_modern_ui()
            self.setup_animations()
        except Exception as e:
            logger.exception("Failed to initialize modern document viewer: %s", e)
            self.create_fallback_ui(e)

    def init_modern_ui(self):
        """Initialize the modern, colorful document viewer interface."""
        # Main layout with modern spacing
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create modern header with reading progress
        self.create_modern_header()
        main_layout.addWidget(self.header_widget)

        # Create stylized scroll area with custom styling
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        if QT_VERSION == 6:
            self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        else:
            self.scroll_area.setAlignment(Qt.AlignHCenter)

        # Apply modern scroll area styling
        self.apply_scroll_area_styling()

        # Container for all page cards
        self.pages_container = QWidget()
        self.pages_layout = QVBoxLayout(self.pages_container)
        self.pages_layout.setContentsMargins(30, 30, 30, 30)
        self.pages_layout.setSpacing(25)

        if QT_VERSION == 6:
            self.pages_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        else:
            self.pages_layout.setAlignment(Qt.AlignHCenter)

        # Create beautiful welcome card
        self.create_welcome_card()

        self.scroll_area.setWidget(self.pages_container)
        main_layout.addWidget(self.scroll_area)

        # Apply overall modern theme
        self.apply_modern_theme()

    def create_fallback_ui(self, error):
        """Create a minimal fallback UI if modern initialization fails."""
        try:
            layout = QVBoxLayout(self)
            error_label = QLabel(f"Failed to initialize modern viewer: {error}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setWordWrap(True)
            layout.addWidget(error_label)
        except Exception:
            pass

    def create_modern_header(self):
        """Create a modern header with reading progress and controls."""
        self.header_widget = QWidget()
        self.header_widget.setFixedHeight(60)

        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(25, 10, 25, 10)

        # Reading progress bar with modern styling
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f0f0f0, stop:1 #e0e0e0);
            }
            QProgressBar::chunk {
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
            }
        """)

        # Progress label with modern typography
        self.progress_label = QLabel("Ready to read")
        self.progress_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
                font-size: 12px;
                font-weight: 500;
            }
        """)

        header_layout.addWidget(self.progress_label)
        header_layout.addWidget(self.progress_bar)

        # Apply header styling
        self.header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border-bottom: 1px solid #e9ecef;
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
        """Load a document with modern visual feedback."""
        self.current_document = document
        self.current_page = 0

        # Update progress label
        if hasattr(self, 'progress_label'):
            self.progress_label.setText("Loading document...")

        self.clear_pages()
        self.display_all_pages_modern()

    def clear_pages(self):
        """Clear all existing page widgets with smooth transition."""
        # Remove welcome card if it exists
        if hasattr(self, 'welcome_card') and self.welcome_card:
            self.pages_layout.removeWidget(self.welcome_card)
            self.welcome_card.deleteLater()

        # Remove all page cards
        for widget in getattr(self, 'page_cards', []):
            self.pages_layout.removeWidget(widget)
            widget.deleteLater()
        self.page_cards = []

    def display_all_pages_modern(self):
        """Display all pages using modern, colorful card design."""
        if not self.current_document:
            return

        try:
            page_count = self.current_document.get_page_count()
            logger.info("Displaying %d pages with modern design", page_count)

            # Update progress
            if hasattr(self, 'progress_label'):
                self.progress_label.setText(f"Reading: {page_count} pages")
                self.progress_bar.setMaximum(page_count)
                self.progress_bar.setValue(1)

            for page_num in range(page_count):
                # Create modern page card
                page_card = ModernPageCard(page_num, page_count, self)

                # Add page content to the card
                content_widget = self.create_modern_page_content(page_num)
                if content_widget:
                    page_card.content_layout.addWidget(content_widget)

                # Apply modern card styling with shadow effects
                page_card.apply_modern_styling()

                self.pages_layout.addWidget(page_card)
                self.page_cards.append(page_card)

        except Exception as e:
            logger.exception("Error displaying pages with modern design: %s", e)
            self.create_error_card(str(e))

    def create_error_card(self, error_message):
        """Create a modern error card."""
        error_card = QWidget()
        error_card.setFixedSize(600, 200)

        error_layout = QVBoxLayout(error_card)
        error_layout.setContentsMargins(30, 30, 30, 30)

        error_title = QLabel("⚠️ Unable to Load Document")
        error_title.setAlignment(Qt.AlignCenter)
        error_title.setStyleSheet("""
            QLabel {
                color: #dc3545;
                font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 10px;
            }
        """)

        error_details = QLabel(error_message)
        error_details.setAlignment(Qt.AlignCenter)
        error_details.setWordWrap(True)
        error_details.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
                font-size: 14px;
                line-height: 1.4;
            }
        """)

        error_layout.addWidget(error_title)
        error_layout.addWidget(error_details)

        error_card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fff5f5, stop:1 #ffe6e6);
                border: 2px solid #f8d7da;
                border-radius: 15px;
            }
        """)

        self.pages_layout.addWidget(error_card)
        self.page_cards.append(error_card)

    def setup_animations(self):
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
        """Smoothly scroll to the next page with animation."""
        if not self.current_document or not hasattr(self, 'page_cards') or not self.page_cards:
            return False

        page_count = self.current_document.get_page_count()
        if self.current_page < page_count - 1:
            self.current_page += 1
            self.smooth_scroll_to_page(self.current_page)
            self.update_progress()
            return True
        return False

    def previous_page(self):
        """Smoothly scroll to the previous page with animation."""
        if not self.current_document or not hasattr(self, 'page_cards') or not self.page_cards:
            return False

        if self.current_page > 0:
            self.current_page -= 1
            self.smooth_scroll_to_page(self.current_page)
            self.update_progress()
            return True
        return False

    def smooth_scroll_to_page(self, page_num):
        """Smoothly scroll to a specific page with animation."""
        if 0 <= page_num < len(self.page_cards):
            widget = self.page_cards[page_num]

            # Calculate target scroll position
            target_y = widget.y() - 50  # Add some padding

            # Animate scroll
            if hasattr(self, 'scroll_animation'):
                self.scroll_animation.setStartValue(self.scroll_area.verticalScrollBar().value())
                self.scroll_animation.setEndValue(target_y)
                self.scroll_animation.start()
            else:
                # Fallback to instant scroll
                self.scroll_area.ensureWidgetVisible(widget, 50, 50)

    def update_progress(self):
        """Update the reading progress indicator."""
        if hasattr(self, 'progress_bar') and self.current_document:
            page_count = self.current_document.get_page_count()
            self.progress_bar.setValue(self.current_page + 1)

            if hasattr(self, 'progress_label'):
                self.progress_label.setText(f"Page {self.current_page + 1} of {page_count}")

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
