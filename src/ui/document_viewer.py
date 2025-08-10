"""
Document Viewer Widget for Modern EBook Reader
Handles proper display of PDF, EPUB, and MOBI documents with Qt graphics.
"""

# Prefer PyQt5 if available to match the main application binding; fallback to PyQt6
try:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
    from PyQt5.QtCore import Qt
    QT_VERSION = 5
except ImportError:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
    from PyQt6.QtCore import Qt
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


class DocumentViewer(QWidget):
    """Widget for displaying documents with proper Qt graphics handling."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_document = None
        self.current_page = 0
        try:
            self.init_ui()
        except Exception as e:
            # Avoid crashing; raise after setting a safe text
            try:
                # Minimal fallback label if layout fails
                self.setLayout(QVBoxLayout())
                lbl = QLabel(f"Failed to initialize viewer UI: {e}")
                self.layout().addWidget(lbl)
            except Exception:
                pass
            raise

    def init_ui(self):
        """Initialize the document viewer UI (continuous vertical scroll)."""
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        if QT_VERSION == 6:
            self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop)
        else:
            self.scroll_area.setAlignment(Qt.AlignTop)

        # Container inside scroll area for stacking page widgets vertically
        self.container = QWidget()
        self.pages_layout = QVBoxLayout(self.container)
        self.pages_layout.setContentsMargins(20, 20, 20, 20)
        self.pages_layout.setSpacing(20)
        if QT_VERSION == 6:
            self.pages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        else:
            self.pages_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.container)
        root_layout.addWidget(self.scroll_area)

        # State
        self.page_widgets = []

    def load_document(self, document):
        """Load a document for continuous scrolling display."""
        self.current_document = document
        self.current_page = 0
        self.clear_pages()
        self.display_all_pages()

    def clear_pages(self):
        """Clear all existing page widgets."""
        # Remove all page widgets from layout
        for widget in self.page_widgets:
            self.pages_layout.removeWidget(widget)
            widget.deleteLater()
        self.page_widgets.clear()

    def display_all_pages(self):
        """Display all pages of the document in a continuous scroll."""
        if not self.current_document:
            placeholder = QLabel("No document loaded")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("""
                QLabel {
                    background-color: #FFFFFF;
                    border: 1px solid #E0E0E0;
                    padding: 40px;
                    font-size: 16px;
                    color: #666666;
                    border-radius: 8px;
                }
            """)
            self.pages_layout.addWidget(placeholder)
            self.page_widgets.append(placeholder)
            return

        try:
            page_count = self.current_document.get_page_count()
            logger.info("Displaying %d pages for continuous scroll", page_count)

            for page_num in range(page_count):
                # Create a container for page number + page content
                page_container = QWidget()
                container_layout = QVBoxLayout(page_container)
                container_layout.setContentsMargins(0, 0, 0, 0)
                container_layout.setSpacing(5)

                # Add page number indicator
                page_indicator = QLabel(f"Page {page_num + 1} of {page_count}")
                page_indicator.setAlignment(Qt.AlignCenter)
                page_indicator.setStyleSheet("""
                    QLabel {
                        background-color: #F0F0F0;
                        border: 1px solid #D0D0D0;
                        padding: 5px 15px;
                        margin: 5px;
                        font-size: 12px;
                        font-weight: bold;
                        color: #666666;
                        border-radius: 15px;
                    }
                """)
                container_layout.addWidget(page_indicator)

                # Add the actual page content
                page_widget = self.create_page_widget(page_num)
                if page_widget:
                    container_layout.addWidget(page_widget)

                self.pages_layout.addWidget(page_container)
                self.page_widgets.append(page_container)

        except Exception as e:
            logger.exception("Error displaying all pages: %s", e)
            error_label = QLabel(f"Error loading document pages: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setWordWrap(True)
            self.pages_layout.addWidget(error_label)
            self.page_widgets.append(error_label)

    def create_page_widget(self, page_num):
        """Create a widget for a single page."""
        try:
            # Handle PDF documents
            if hasattr(self.current_document, 'get_page_image_data'):
                return self.create_pdf_page_widget(page_num)
            # Handle text-based documents (EPUB, MOBI)
            elif hasattr(self.current_document, 'get_page_text') or hasattr(self.current_document, 'get_page'):
                return self.create_text_page_widget(page_num)
            else:
                error_label = QLabel(f"Page {page_num + 1}: Unsupported format")
                error_label.setAlignment(Qt.AlignCenter)
                return error_label

        except Exception as e:
            logger.exception("Error creating page widget %d: %s", page_num, e)
            error_label = QLabel(f"Page {page_num + 1}: Error loading page")
            error_label.setAlignment(Qt.AlignCenter)
            return error_label

    def create_pdf_page_widget(self, page_num):
        """Create a widget for a PDF page."""
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

            # Create label to display the page with page number
            page_label = QLabel()
            page_label.setPixmap(pixmap)
            page_label.setAlignment(Qt.AlignCenter)
            page_label.setToolTip(f"Page {page_num + 1}")
            page_label.setStyleSheet("""
                QLabel {
                    background-color: #FFFFFF;
                    border: 2px solid #E0E0E0;
                    padding: 15px;
                    margin: 8px;
                    border-radius: 10px;
                    box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
                }
            """)

            return page_label

        except Exception as e:
            logger.exception("Error creating PDF page widget %d: %s", page_num, e)
            error_label = QLabel(f"Page {page_num + 1}: Error rendering PDF page")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setWordWrap(True)
            return error_label

    def create_text_page_widget(self, page_num):
        """Create a widget for a text-based page (EPUB, MOBI)."""
        try:
            # Get text content (support readers that expose get_page_text or generic get_page)
            if hasattr(self.current_document, 'get_page_text'):
                text = self.current_document.get_page_text(page_num)
            else:
                text = self.current_document.get_page(page_num)

            # Create label to display the text with page number
            page_label = QLabel(text)
            page_label.setWordWrap(True)
            page_label.setToolTip(f"Page {page_num + 1}")
            if QT_VERSION == 6:
                page_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            else:
                page_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

            # Style the text page with better visual separation
            page_label.setStyleSheet("""
                QLabel {
                    background-color: #FFFFFF;
                    border: 2px solid #E0E0E0;
                    padding: 35px;
                    margin: 8px;
                    font-size: 14px;
                    color: #333333;
                    line-height: 1.6;
                    border-radius: 10px;
                    box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
                }
            """)

            return page_label

        except Exception as e:
            logger.exception("Error creating text page widget %d: %s", page_num, e)
            error_label = QLabel(f"Page {page_num + 1}: Error reading text")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setWordWrap(True)
            return error_label

    def next_page(self):
        """Scroll to the next page in continuous view."""
        if not self.current_document or not self.page_widgets:
            return False

        page_count = self.current_document.get_page_count()
        if self.current_page < page_count - 1:
            self.current_page += 1
            self.scroll_to_page(self.current_page)
            return True
        return False

    def previous_page(self):
        """Scroll to the previous page in continuous view."""
        if not self.current_document or not self.page_widgets:
            return False

        if self.current_page > 0:
            self.current_page -= 1
            self.scroll_to_page(self.current_page)
            return True
        return False

    def scroll_to_page(self, page_num):
        """Scroll to a specific page in the continuous view."""
        if 0 <= page_num < len(self.page_widgets):
            widget = self.page_widgets[page_num]
            # Scroll to the widget
            self.scroll_area.ensureWidgetVisible(widget, 50, 50)

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
