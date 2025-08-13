"""
Text Selection System
Handles text selection detection and highlighting in document viewers
"""

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect, QTimer
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QMouseEvent
import logging
from typing import Optional, Tuple, List

from ..models import TextSelection, Point

logger = logging.getLogger("ebook_reader")

class TextSelectionHandler(QWidget):
    """Handles text selection in document viewers"""
    
    text_selected = pyqtSignal(object)  # TextSelection object
    selection_cleared = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        self.current_selection = None
        self.selection_timer = QTimer()
        self.selection_timer.setSingleShot(True)
        self.selection_timer.timeout.connect(self.finalize_selection)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Make widget transparent for overlay
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: transparent;")
    
    def mousePressEvent(self, event: QMouseEvent):
        """Start text selection"""
        if event.button() == Qt.LeftButton:
            self.start_selection(event.pos())
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Update text selection"""
        if self.is_selecting:
            self.update_selection(event.pos())
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """End text selection"""
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.end_selection(event.pos())
        super().mouseReleaseEvent(event)
    
    def start_selection(self, pos: QPoint):
        """Start a new text selection"""
        self.selection_start = pos
        self.selection_end = pos
        self.is_selecting = True
        self.current_selection = None
        self.update()
    
    def update_selection(self, pos: QPoint):
        """Update the current selection"""
        if self.is_selecting:
            self.selection_end = pos
            self.update()
    
    def end_selection(self, pos: QPoint):
        """End the current selection"""
        if not self.is_selecting:
            return
        
        self.selection_end = pos
        self.is_selecting = False
        
        # Check if we have a valid selection
        if self.selection_start and self.selection_end:
            distance = (self.selection_start - self.selection_end).manhattanLength()
            if distance > 10:  # Minimum selection distance
                # Delay finalization to allow for double-click detection
                self.selection_timer.start(100)
            else:
                self.clear_selection()
    
    def finalize_selection(self):
        """Finalize the text selection"""
        if self.selection_start and self.selection_end:
            # Create text selection object
            selection = self.create_text_selection()
            if selection:
                self.current_selection = selection
                self.text_selected.emit(selection)
                logger.debug(f"Text selection created: {selection.selected_text[:50]}...")
    
    def create_text_selection(self) -> Optional[TextSelection]:
        """Create a TextSelection object from current selection"""
        if not self.selection_start or not self.selection_end:
            return None
        
        try:
            # Normalize selection coordinates
            start_x = min(self.selection_start.x(), self.selection_end.x())
            start_y = min(self.selection_start.y(), self.selection_end.y())
            end_x = max(self.selection_start.x(), self.selection_end.x())
            end_y = max(self.selection_start.y(), self.selection_end.y())
            
            # Create selection object
            selection = TextSelection(
                start_position=Point(start_x, start_y),
                end_position=Point(end_x, end_y),
                start_char_index=0,  # Will be calculated by document viewer
                end_char_index=0,    # Will be calculated by document viewer
                selected_text=""     # Will be extracted by document viewer
            )
            
            return selection
            
        except Exception as e:
            logger.error(f"Failed to create text selection: {e}")
            return None
    
    def clear_selection(self):
        """Clear the current selection"""
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        self.current_selection = None
        self.selection_timer.stop()
        self.update()
        self.selection_cleared.emit()
    
    def get_current_selection(self) -> Optional[TextSelection]:
        """Get the current text selection"""
        return self.current_selection
    
    def paintEvent(self, event):
        """Paint the selection overlay"""
        if not self.is_selecting or not self.selection_start or not self.selection_end:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw selection rectangle
        rect = QRect(self.selection_start, self.selection_end).normalized()
        
        # Selection color
        selection_color = QColor(0, 120, 215, 80)  # Semi-transparent blue
        painter.setBrush(QBrush(selection_color))
        painter.setPen(QPen(QColor(0, 120, 215), 2))
        
        painter.drawRect(rect)

class DocumentTextExtractor:
    """Extracts text from document viewers for text selection"""
    
    def __init__(self, document_viewer):
        self.document_viewer = document_viewer
    
    def extract_text_from_selection(self, selection: TextSelection) -> TextSelection:
        """Extract actual text from a selection area"""
        try:
            # This is a placeholder implementation
            # In a real implementation, this would:
            # 1. Convert screen coordinates to document coordinates
            # 2. Find the text within the selection area
            # 3. Calculate character indices
            # 4. Extract the selected text
            
            # For now, return a mock selection
            selection.selected_text = "Selected text placeholder"
            selection.start_char_index = 0
            selection.end_char_index = len(selection.selected_text)
            
            return selection
            
        except Exception as e:
            logger.error(f"Failed to extract text from selection: {e}")
            return selection

class HighlightModeManager:
    """Manages highlight mode state and interactions"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.highlight_mode = False
        self.current_color = "#FFFF00"  # Yellow default
        self.text_selector = None
        self.text_extractor = None
    
    def enable_highlight_mode(self, enabled: bool):
        """Enable or disable highlight mode"""
        self.highlight_mode = enabled
        
        if enabled:
            self._setup_text_selection()
        else:
            self._cleanup_text_selection()
    
    def set_highlight_color(self, color: str):
        """Set the current highlight color"""
        self.current_color = color
    
    def _setup_text_selection(self):
        """Setup text selection handling"""
        if not self.main_window.document_viewer:
            return
        
        try:
            # Create text selection handler
            self.text_selector = TextSelectionHandler(self.main_window.document_viewer)
            self.text_selector.text_selected.connect(self._on_text_selected)
            self.text_selector.selection_cleared.connect(self._on_selection_cleared)
            
            # Create text extractor
            self.text_extractor = DocumentTextExtractor(self.main_window.document_viewer)
            
            # Show the selection overlay
            self.text_selector.show()
            self.text_selector.raise_()
            
            # Update cursor
            self.main_window.document_viewer.setCursor(Qt.IBeamCursor)
            
            logger.info("Text selection enabled for highlighting")
            
        except Exception as e:
            logger.error(f"Failed to setup text selection: {e}")
    
    def _cleanup_text_selection(self):
        """Cleanup text selection handling"""
        if self.text_selector:
            self.text_selector.hide()
            self.text_selector.deleteLater()
            self.text_selector = None
        
        if self.main_window.document_viewer:
            self.main_window.document_viewer.setCursor(Qt.ArrowCursor)
        
        self.text_extractor = None
        logger.info("Text selection disabled")
    
    def _on_text_selected(self, selection: TextSelection):
        """Handle text selection for highlighting"""
        if not self.highlight_mode or not self.main_window.annotation_manager:
            return
        
        try:
            # Extract actual text from selection
            if self.text_extractor:
                selection = self.text_extractor.extract_text_from_selection(selection)
            
            # Create highlight
            current_page = self.main_window.get_current_page()
            if current_page is None:
                return
            
            highlight = self.main_window.annotation_manager.create_highlight(
                document_path=self.main_window.current_document.file_path,
                page_number=current_page,
                text_selection=selection,
                color=self.current_color
            )
            
            if highlight:
                # Update UI
                self.main_window.update_highlight_display()
                if hasattr(self.main_window, 'highlight_panel'):
                    self.main_window.highlight_panel.refresh()
                
                logger.info(f"Created highlight: {highlight.highlighted_text[:50]}...")
            
            # Clear selection
            self.text_selector.clear_selection()
            
        except Exception as e:
            logger.error(f"Failed to create highlight from selection: {e}")
    
    def _on_selection_cleared(self):
        """Handle selection clearing"""
        pass  # Nothing to do for now

class SelectionContextMenu:
    """Context menu for text selections"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def show_selection_menu(self, selection: TextSelection, position: QPoint):
        """Show context menu for text selection"""
        from PyQt5.QtWidgets import QMenu
        
        menu = QMenu(self.main_window)
        
        # Highlight actions
        highlight_menu = menu.addMenu("Highlight")
        
        colors = [
            ("#FFFF00", "Yellow"),
            ("#00FF00", "Green"), 
            ("#0080FF", "Blue"),
            ("#FF69B4", "Pink"),
            ("#FFA500", "Orange"),
            ("#8A2BE2", "Purple")
        ]
        
        for color, name in colors:
            action = highlight_menu.addAction(f"Highlight with {name}")
            action.triggered.connect(lambda checked, c=color: self._create_highlight(selection, c))
        
        # Note action
        note_action = menu.addAction("Add Note")
        note_action.triggered.connect(lambda: self._add_note(selection))
        
        menu.exec_(position)
    
    def _create_highlight(self, selection: TextSelection, color: str):
        """Create highlight with specified color"""
        if not self.main_window.annotation_manager:
            return
        
        try:
            current_page = self.main_window.get_current_page()
            if current_page is None:
                return
            
            highlight = self.main_window.annotation_manager.create_highlight(
                document_path=self.main_window.current_document.file_path,
                page_number=current_page,
                text_selection=selection,
                color=color
            )
            
            if highlight:
                self.main_window.update_highlight_display()
                logger.info(f"Created highlight with color {color}")
                
        except Exception as e:
            logger.error(f"Failed to create highlight: {e}")
    
    def _add_note(self, selection: TextSelection):
        """Add note at selection position"""
        # This will be implemented when we add note functionality
        pass