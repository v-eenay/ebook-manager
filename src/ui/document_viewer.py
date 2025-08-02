"""
Document Viewer Widget
Handles the display and interaction with document content.
"""

try:
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QLabel, 
                                QSizePolicy, QFrame)
    from PyQt6.QtCore import Qt, pyqtSignal, QSize
    from PyQt6.QtGui import QPixmap, QPainter, QWheelEvent, QKeyEvent
    QT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QLabel, 
                                QSizePolicy, QFrame)
    from PyQt5.QtCore import Qt, pyqtSignal, QSize
    from PyQt5.QtGui import QPixmap, QPainter
    QT_VERSION = 5


class DocumentViewer(QWidget):
    """Widget for displaying document content with zoom and navigation."""
    
    # Signals
    page_changed = pyqtSignal(int, int)  # current_page, total_pages
    zoom_changed = pyqtSignal(float)     # zoom_level
    
    def __init__(self):
        super().__init__()
        self.document = None
        self.current_page = 1
        self.zoom_level = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 5.0
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the document viewer UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area for document content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #F8F9FA;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #F8F9FA;
                width: 12px;
                border: none;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #BDBDBD;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #9E9E9E;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        if QT_VERSION == 6:
            self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
            # Create content label for displaying pages
            self.content_label = QLabel()
            self.content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.scroll_area.setAlignment(Qt.AlignCenter)
            self.scroll_area.setFrameStyle(QFrame.NoFrame)
            # Create content label for displaying pages
            self.content_label = QLabel()
            self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                margin: 16px;
                padding: 16px;
                color: #212121;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        self.content_label.setText("No document loaded")
        self.content_label.setMinimumSize(400, 300)
        
        self.scroll_area.setWidget(self.content_label)
        layout.addWidget(self.scroll_area)
        
        # Enable mouse wheel events
        if QT_VERSION == 6:
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        else:
            self.setFocusPolicy(Qt.StrongFocus)
        
    def set_document(self, document):
        """Set the document to display."""
        self.document = document
        self.current_page = 1
        self.zoom_level = 1.0
        
        if document:
            self.display_current_page()
            self.page_changed.emit(self.current_page, document.get_page_count())
            self.zoom_changed.emit(self.zoom_level)
        else:
            self.content_label.setText("No document loaded")
            
    def display_current_page(self):
        """Display the current page of the document."""
        if not self.document:
            return
            
        try:
            # Get the page content (this will be implemented by document readers)
            page_content = self.document.get_page(self.current_page - 1)  # 0-based indexing
            
            if isinstance(page_content, QPixmap):
                # Scale the pixmap according to zoom level
                if QT_VERSION == 6:
                    scaled_pixmap = page_content.scaled(
                        page_content.size() * self.zoom_level,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                else:
                    scaled_pixmap = page_content.scaled(
                        page_content.size() * self.zoom_level,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                self.content_label.setPixmap(scaled_pixmap)
                self.content_label.resize(scaled_pixmap.size())
            else:
                # Handle text content (for EPUB/MOBI) with better formatting
                formatted_text = str(page_content)
                # Ensure good contrast and readability for text content
                self.content_label.setStyleSheet("""
                    QLabel {
                        background-color: #FFFFFF;
                        border: 1px solid #E0E0E0;
                        border-radius: 4px;
                        margin: 16px;
                        padding: 24px;
                        color: #212121;
                        font-family: Georgia, 'Times New Roman', serif;
                        font-size: 16px;
                        line-height: 1.8;
                        text-align: left;
                    }
                """)
                self.content_label.setText(formatted_text)

        except Exception as e:
            # Error message with high contrast
            self.content_label.setStyleSheet("""
                QLabel {
                    background-color: #FFF3E0;
                    border: 1px solid #FFB74D;
                    border-radius: 4px;
                    margin: 16px;
                    padding: 24px;
                    color: #E65100;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    font-size: 16px;
                    line-height: 1.6;
                    text-align: center;
                }
            """)
            self.content_label.setText(f"Error displaying page: {str(e)}")
            
    def previous_page(self):
        """Navigate to the previous page."""
        if self.document and self.current_page > 1:
            self.current_page -= 1
            self.display_current_page()
            self.page_changed.emit(self.current_page, self.document.get_page_count())
            
    def next_page(self):
        """Navigate to the next page."""
        if self.document and self.current_page < self.document.get_page_count():
            self.current_page += 1
            self.display_current_page()
            self.page_changed.emit(self.current_page, self.document.get_page_count())
            
    def zoom_in(self):
        """Increase zoom level."""
        if self.zoom_level < self.max_zoom:
            self.zoom_level = min(self.zoom_level * 1.2, self.max_zoom)
            self.display_current_page()
            self.zoom_changed.emit(self.zoom_level)
            
    def zoom_out(self):
        """Decrease zoom level."""
        if self.zoom_level > self.min_zoom:
            self.zoom_level = max(self.zoom_level / 1.2, self.min_zoom)
            self.display_current_page()
            self.zoom_changed.emit(self.zoom_level)
            
    def set_zoom(self, zoom_level):
        """Set specific zoom level."""
        self.zoom_level = max(self.min_zoom, min(zoom_level, self.max_zoom))
        self.display_current_page()
        self.zoom_changed.emit(self.zoom_level)
        
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming and navigation."""
        if QT_VERSION == 6:
            delta = event.angleDelta().y()
            modifiers = event.modifiers()
        else:
            delta = event.delta()
            modifiers = event.modifiers()
            
        ctrl_modifier = Qt.KeyboardModifier.ControlModifier if QT_VERSION == 6 else Qt.ControlModifier
        if modifiers & ctrl_modifier:
            # Zoom with Ctrl+wheel
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            # Page navigation with wheel
            if delta > 0:
                self.previous_page()
            else:
                self.next_page()
                
    def keyPressEvent(self, event):
        """Handle key press events."""
        key = event.key()
        
        # Define key constants for compatibility
        if QT_VERSION == 6:
            key_left = Qt.Key.Key_Left
            key_right = Qt.Key.Key_Right
            key_pageup = Qt.Key.Key_PageUp
            key_pagedown = Qt.Key.Key_PageDown
            key_home = Qt.Key.Key_Home
            key_end = Qt.Key.Key_End
        else:
            key_left = Qt.Key_Left
            key_right = Qt.Key_Right
            key_pageup = Qt.Key_PageUp
            key_pagedown = Qt.Key_PageDown
            key_home = Qt.Key_Home
            key_end = Qt.Key_End

        if key == key_left or key == key_pageup:
            self.previous_page()
        elif key == key_right or key == key_pagedown:
            self.next_page()
        elif key == key_home:
            if self.document:
                self.current_page = 1
                self.display_current_page()
                self.page_changed.emit(self.current_page, self.document.get_page_count())
        elif key == key_end:
            if self.document:
                self.current_page = self.document.get_page_count()
                self.display_current_page()
                self.page_changed.emit(self.current_page, self.document.get_page_count())
        else:
            super().keyPressEvent(event)
