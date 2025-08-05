"""
Document Viewer Widget for Modern EBook Reader
Handles proper display of PDF, EPUB, and MOBI documents with Qt graphics.
"""

try:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
    from PyQt6.QtCore import Qt
    QT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
    from PyQt5.QtCore import Qt
    QT_VERSION = 5

# Lazy import QPixmap and QImage to avoid early initialization issues
def _get_qt_graphics():
    """Get QPixmap and QImage classes when needed."""
    if QT_VERSION == 6:
        from PyQt6.QtGui import QPixmap, QImage
    else:
        from PyQt5.QtGui import QPixmap, QImage
    return QPixmap, QImage


class DocumentViewer(QWidget):
    """Widget for displaying documents with proper Qt graphics handling."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_document = None
        self.current_page = 0
        self.init_ui()
        
    def init_ui(self):
        """Initialize the document viewer UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create scroll area for document display
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        # Create label for document content
        self.document_label = QLabel()
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
        self.document_label.setText("No document loaded")

        self.scroll_area.setWidget(self.document_label)
        layout.addWidget(self.scroll_area)

    def load_document(self, document):
        """Load a document for display."""
        self.current_document = document
        self.current_page = 0
        self.display_current_page()

    def display_current_page(self):
        """Display the current page of the document."""
        if not self.current_document:
            self.document_label.setText("No document loaded")
            return

        try:
            # Handle PDF documents
            if hasattr(self.current_document, 'get_page_image_data'):
                self.display_pdf_page()
            # Handle text-based documents (EPUB, MOBI)
            elif hasattr(self.current_document, 'get_page_text'):
                self.display_text_page()
            else:
                self.document_label.setText("Document format not supported for display")

        except Exception as e:
            self.document_label.setText(f"Error displaying page: {str(e)}")

    def display_pdf_page(self):
        """Display a PDF page as an image."""
        try:
            # Get Qt graphics classes
            QPixmap, QImage = _get_qt_graphics()

            # Get image data and dimensions from PDF reader
            img_data, width, height = self.current_document.get_page_image_data(self.current_page)

            # Create QImage from raw data
            qimg = QImage.fromData(img_data)
            if qimg.isNull():
                raise Exception("Failed to create QImage from PDF data")

            # Create QPixmap from QImage
            pixmap = QPixmap.fromImage(qimg)
            if pixmap.isNull():
                raise Exception("Failed to create QPixmap from QImage")

            # Display the pixmap
            self.document_label.setPixmap(pixmap)
            self.document_label.setText("")

            # Update styling for image display
            self.document_label.setStyleSheet("""
                QLabel {
                    background-color: #F8F8F8;
                    border: 1px solid #E0E0E0;
                    padding: 10px;
                }
            """)

        except Exception as e:
            # Fallback to error message
            self.document_label.setText(f"Error rendering PDF page: {str(e)}")
            try:
                QPixmap, _ = _get_qt_graphics()
                self.document_label.setPixmap(QPixmap())  # Clear any existing pixmap
            except:
                pass  # Ignore pixmap clearing errors

    def display_text_page(self):
        """Display a text-based page (EPUB, MOBI)."""
        try:
            # Get text content
            text = self.current_document.get_page_text(self.current_page)

            # Display text
            self.document_label.setText(text)
            # Clear any existing pixmap
            try:
                QPixmap, _ = _get_qt_graphics()
                self.document_label.setPixmap(QPixmap())
            except:
                pass  # Ignore pixmap clearing errors
            self.document_label.setWordWrap(True)
            self.document_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

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

        except Exception as e:
            self.document_label.setText(f"Error reading text: {str(e)}")

    def next_page(self):
        """Go to the next page."""
        if self.current_document and hasattr(self.current_document, 'get_page_count'):
            page_count = self.current_document.get_page_count()
            if self.current_page < page_count - 1:
                self.current_page += 1
                self.display_current_page()
                return True
        return False

    def previous_page(self):
        """Go to the previous page."""
        if self.current_document and self.current_page > 0:
            self.current_page -= 1
            self.display_current_page()
            return True
        return False

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
