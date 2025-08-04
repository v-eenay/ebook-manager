"""
Document Viewer Widget
Handles the display and interaction with document content using Fluent Design.
"""

try:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
    from PyQt6.QtCore import Qt, pyqtSignal, QSize
    from PyQt6.QtGui import QPixmap, QPainter, QWheelEvent, QKeyEvent
    QT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
    from PyQt5.QtCore import Qt, pyqtSignal, QSize
    from PyQt5.QtGui import QPixmap, QPainter
    QT_VERSION = 5

# Fluent Design System imports
from qfluentwidgets import (
    ScrollArea, CardWidget, BodyLabel, TitleLabel, SubtitleLabel,
    ToolButton, FluentIcon as FIF, InfoBar, InfoBarPosition,
    TransparentToolButton, PrimaryPushButton, isDarkTheme
)


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
        
        # Create Fluent Design scroll area for document content
        self.scroll_area = ScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            ScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        # Create Fluent Design card container for document content
        self.content_card = CardWidget()
        self.content_card.setMinimumSize(400, 300)

        # Create content layout within the card
        card_layout = QVBoxLayout(self.content_card)
        card_layout.setContentsMargins(20, 20, 20, 20)

        # Create content label for displaying pages
        self.content_label = BodyLabel()
        if QT_VERSION == 6:
            self.content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setText("No document loaded")
        self.content_label.setWordWrap(True)

        # Add content label to card layout
        card_layout.addWidget(self.content_label)

        # Set the card as the scroll area widget
        self.scroll_area.setWidget(self.content_card)
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
                # Handle text content (for EPUB/MOBI) with Fluent Design styling
                formatted_text = str(page_content)
                self.content_label.setText(formatted_text)
                # Use Fluent Design body text styling
                self.content_label.setStyleSheet("""
                    BodyLabel {
                        font-family: Georgia, 'Times New Roman', serif;
                        font-size: 18px;
                        line-height: 1.8;
                        padding: 16px;
                    }
                """)

        except Exception as e:
            # Error message with Fluent Design error styling
            error_text = f"Error displaying page: {str(e)}"
            self.content_label.setText(error_text)
            self.content_label.setStyleSheet("""
                BodyLabel {
                    color: #D13438;
                    font-weight: 600;
                    padding: 16px;
                }
            """)
            
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
