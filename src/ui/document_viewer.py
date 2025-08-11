"""
Document Viewer - Clean, minimal document display focused on content
"""

try:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QTextEdit
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QPixmap, QImage
    QT_VERSION = 5
except ImportError:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QTextEdit
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPixmap, QImage
    QT_VERSION = 6

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
        """Initialize the ultra-minimal, professional UI focused on content."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create scroll area with minimal styling - maximize document space
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #FDFDFD;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #CCCCCC;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #AAAAAA;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        # Create content widget with minimal margins for maximum space
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)  # Reduced margins
        self.content_layout.setAlignment(Qt.AlignCenter)

        # Create minimal placeholder
        self.create_placeholder()

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

    def create_placeholder(self):
        """Create minimal placeholder content when no document is loaded."""
        placeholder = QLabel("Open a document to begin reading")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #999999;
                font-size: 14px;
                font-weight: 300;
                padding: 60px 20px;
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
        """Display a PDF page with minimal, professional styling."""
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

            # Create label with minimal styling - focus on content
            page_label = QLabel()
            page_label.setPixmap(pixmap)
            page_label.setAlignment(Qt.AlignCenter)
            page_label.setStyleSheet("""
                QLabel {
                    background-color: white;
                    border: 1px solid #F0F0F0;
                    padding: 5px;
                    margin: 5px;
                }
            """)

            self.content_layout.addWidget(page_label)

        except Exception as e:
            logger.exception("Error displaying PDF page: %s", e)
            self.display_error("Error displaying PDF page")

    def display_text_page(self):
        """Display a text-based page with professional typography."""
        try:
            # Get text content
            text = self.current_document.get_page_text(self.current_page)

            # Create text display with professional styling
            text_display = QTextEdit()
            text_display.setPlainText(text)
            text_display.setReadOnly(True)
            text_display.setStyleSheet("""
                QTextEdit {
                    background-color: white;
                    border: 1px solid #F0F0F0;
                    padding: 25px;
                    margin: 5px;
                    font-family: 'Segoe UI', 'Georgia', serif;
                    font-size: 15px;
                    line-height: 1.7;
                    color: #2C2C2C;
                    selection-background-color: #E3F2FD;
                }
                QScrollBar:vertical {
                    border: none;
                    background: transparent;
                    width: 8px;
                }
                QScrollBar::handle:vertical {
                    background: #CCCCCC;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #AAAAAA;
                }
            """)

            self.content_layout.addWidget(text_display)

        except Exception as e:
            logger.exception("Error displaying text page: %s", e)
            self.display_error("Error displaying text page")

    def display_error(self, message):
        """Display a minimal error message."""
        error_label = QLabel(message)
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setWordWrap(True)
        error_label.setStyleSheet("""
            QLabel {
                color: #C62828;
                font-size: 13px;
                font-weight: 400;
                padding: 15px;
                background-color: #FFF8F8;
                border: 1px solid #FFEBEE;
                margin: 10px;
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
            return True
        return False

    def next_page(self):
        """Navigate to next page."""
        if self.current_document:
            try:
                page_count = self.current_document.get_page_count()
                if self.current_page < page_count - 1:
                    self.current_page += 1
                    self.display_document()
                    return True
            except:
                pass
        return False

    def get_current_page(self):
        """Get current page number (1-based)."""
        return self.current_page + 1

    def get_total_pages(self):
        """Get total number of pages."""
        if self.current_document:
            try:
                return self.current_document.get_page_count()
            except:
                pass
        return 0

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
        self.display_document()
