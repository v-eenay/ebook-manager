"""
Document Viewer - Clean, minimal document display focused on content
"""

try:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QTextEdit
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPixmap, QImage
    QT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QTextEdit
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QPixmap, QImage
    QT_VERSION = 5

# Logger
try:
    from utils.logger import setup_logging
    logger = setup_logging()
except Exception:
    import logging
    logger = logging.getLogger("ebook_reader")


class DocumentViewer(QWidget):
    """Clean, minimal document viewer focused on content display."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_document = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.init_ui()

    def init_ui(self):
        """Initialize the clean, minimal UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create scroll area for document content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #F8F8F8;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #C0C0C0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A0A0A0;
            }
        """)

        # Create content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setAlignment(Qt.AlignCenter)

        # Create placeholder label
        self.create_placeholder()

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

    def create_placeholder(self):
        """Create placeholder content when no document is loaded."""
        placeholder = QLabel("No document loaded")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 16px;
                padding: 40px;
                background-color: transparent;
            }
        """)
        self.content_layout.addWidget(placeholder)

    def load_document(self, document):
        """Load and display a document."""
        self.current_document = document
        self.current_page = 0
        self.display_document()

    def display_document(self):
        """Display the current document."""
        if not self.current_document:
            return

        # Clear existing content
        self.clear_content()

        try:
            # Handle PDF documents
            if hasattr(self.current_document, 'get_page_image_data'):
                self.display_pdf_page()
            # Handle text-based documents
            elif hasattr(self.current_document, 'get_page_text'):
                self.display_text_page()
            else:
                self.display_error("Unsupported document format")

        except Exception as e:
            logger.exception("Error displaying document: %s", e)
            self.display_error(f"Error displaying document: {str(e)}")

    def display_pdf_page(self):
        """Display a PDF page."""
        try:
            # Get image data from PDF reader
            img_data, _, _ = self.current_document.get_page_image_data(self.current_page)

            # Create QImage from raw data
            qimg = QImage.fromData(img_data)
            if qimg.isNull():
                raise Exception("Failed to create QImage from PDF data")

            # Apply zoom
            if self.zoom_level != 1.0:
                width = int(qimg.width() * self.zoom_level)
                height = int(qimg.height() * self.zoom_level)
                if QT_VERSION == 6:
                    qimg = qimg.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                else:
                    qimg = qimg.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # Create QPixmap from QImage
            pixmap = QPixmap.fromImage(qimg)
            if pixmap.isNull():
                raise Exception("Failed to create QPixmap from QImage")

            # Create label to display the page
            page_label = QLabel()
            page_label.setPixmap(pixmap)
            page_label.setAlignment(Qt.AlignCenter)
            page_label.setStyleSheet("""
                QLabel {
                    background-color: white;
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    padding: 10px;
                    margin: 10px;
                }
            """)

            self.content_layout.addWidget(page_label)

        except Exception as e:
            logger.exception("Error displaying PDF page: %s", e)
            self.display_error("Error displaying PDF page")

    def display_text_page(self):
        """Display a text-based page."""
        try:
            # Get text content
            text = self.current_document.get_page_text(self.current_page)

            # Create text display
            text_display = QTextEdit()
            text_display.setPlainText(text)
            text_display.setReadOnly(True)
            text_display.setStyleSheet("""
                QTextEdit {
                    background-color: white;
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    padding: 20px;
                    margin: 10px;
                    font-family: 'Segoe UI', Georgia, serif;
                    font-size: 14px;
                    line-height: 1.6;
                    color: #333333;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #F0F0F0;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background: #C0C0C0;
                    border-radius: 6px;
                    min-height: 20px;
                }
            """)

            self.content_layout.addWidget(text_display)

        except Exception as e:
            logger.exception("Error displaying text page: %s", e)
            self.display_error("Error displaying text page")

    def display_error(self, message):
        """Display an error message."""
        error_label = QLabel(message)
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setWordWrap(True)
        error_label.setStyleSheet("""
            QLabel {
                color: #D32F2F;
                font-size: 14px;
                padding: 20px;
                background-color: #FFEBEE;
                border: 1px solid #FFCDD2;
                border-radius: 4px;
                margin: 20px;
            }
        """)
        self.content_layout.addWidget(error_label)

    def clear_content(self):
        """Clear all content from the viewer."""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def previous_page(self):
        """Navigate to previous page."""
        if self.current_document and self.current_page > 0:
            self.current_page -= 1
            self.display_document()

    def next_page(self):
        """Navigate to next page."""
        if self.current_document:
            try:
                page_count = self.current_document.get_page_count()
                if self.current_page < page_count - 1:
                    self.current_page += 1
                    self.display_document()
            except:
                pass

    def zoom_in(self):
        """Zoom in on the document."""
        self.zoom_level = min(self.zoom_level * 1.2, 3.0)
        self.display_document()

    def zoom_out(self):
        """Zoom out on the document."""
        self.zoom_level = max(self.zoom_level / 1.2, 0.3)
        self.display_document()

    def fit_to_window(self):
        """Fit document to window."""
        self.zoom_level = 1.0
        self.display_document()n PDF page styling with subtle gradients
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
