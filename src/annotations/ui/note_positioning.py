"""
Note Positioning System
Handles note placement and positioning in document viewers
"""

from PyQt5.QtWidgets import QWidget, QMenu, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QTimer
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QMouseEvent
import logging
from typing import Optional, List, Callable

from ..models import Note, Point

logger = logging.getLogger("ebook_reader")

class NotePositionHandler(QWidget):
    """Handles note positioning in document viewers"""
    
    note_position_selected = pyqtSignal(object)  # Point object
    note_creation_requested = pyqtSignal(object)  # Point object
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.note_mode = False
        self.pending_position = None
        self.notes = []
        self.hovered_note = None
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Make widget transparent for overlay
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: transparent;")
    
    def set_note_mode(self, enabled: bool):
        """Enable or disable note creation mode"""
        self.note_mode = enabled
        
        if enabled:
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            self.pending_position = None
        
        self.update()
    
    def set_notes(self, notes: List[Note]):
        """Set the notes to display"""
        self.notes = notes
        self.update()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse clicks for note positioning"""
        if event.button() == Qt.LeftButton:
            if self.note_mode:
                # Create note at clicked position
                position = Point(event.pos().x(), event.pos().y())
                self.note_creation_requested.emit(position)
                self.set_note_mode(False)  # Exit note mode after creation
            else:
                # Check if clicking on existing note
                clicked_note = self._get_note_at_position(event.pos())
                if clicked_note:
                    self._show_note_context_menu(clicked_note, event.globalPos())
        
        elif event.button() == Qt.RightButton and not self.note_mode:
            # Right-click context menu for note creation
            self._show_creation_context_menu(event.pos(), event.globalPos())
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse hover over notes"""
        if not self.note_mode:
            hovered_note = self._get_note_at_position(event.pos())
            
            if hovered_note != self.hovered_note:
                self.hovered_note = hovered_note
                self.update()
                
                # Set tooltip
                if hovered_note:
                    tooltip = f"Note: {hovered_note.plain_text[:100]}"
                    if len(hovered_note.plain_text) > 100:
                        tooltip += "..."
                    self.setToolTip(tooltip)
                else:
                    self.setToolTip("")
        
        super().mouseMoveEvent(event)
    
    def paintEvent(self, event):
        """Paint note indicators"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw note indicators
        for note in self.notes:
            self._paint_note_indicator(painter, note)
        
        # Draw pending position in note mode
        if self.note_mode and self.pending_position:
            self._paint_pending_position(painter, self.pending_position)
    
    def _paint_note_indicator(self, painter: QPainter, note: Note):
        """Paint a note indicator"""
        try:
            # Calculate position
            x = int(note.position.x)
            y = int(note.position.y)
            
            # Determine colors
            if note == self.hovered_note:
                bg_color = QColor(255, 140, 0)  # Orange hover
                border_color = QColor(255, 127, 0)
            else:
                bg_color = QColor(255, 165, 0)  # Orange
                border_color = QColor(255, 140, 0)
            
            # Draw note indicator circle
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(border_color, 2))
            painter.drawEllipse(x - 8, y - 8, 16, 16)
            
            # Draw note icon (simple lines)
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawLine(x - 4, y - 2, x + 4, y - 2)
            painter.drawLine(x - 4, y, x + 4, y)
            painter.drawLine(x - 4, y + 2, x + 2, y + 2)
            
            # Store position for hit testing
            note._render_position = QPoint(x, y)
            note._render_radius = 8
            
        except Exception as e:
            logger.error(f"Failed to paint note indicator {note.id}: {e}")
    
    def _paint_pending_position(self, painter: QPainter, position: Point):
        """Paint pending note position"""
        x = int(position.x)
        y = int(position.y)
        
        # Draw pending indicator
        painter.setBrush(QBrush(QColor(255, 165, 0, 128)))
        painter.setPen(QPen(QColor(255, 140, 0), 2, Qt.DashLine))
        painter.drawEllipse(x - 8, y - 8, 16, 16)
    
    def _get_note_at_position(self, pos: QPoint) -> Optional[Note]:
        """Get note at the given position"""
        for note in self.notes:
            if hasattr(note, '_render_position') and hasattr(note, '_render_radius'):
                distance = (pos - note._render_position).manhattanLength()
                if distance <= note._render_radius:
                    return note
        return None
    
    def _show_note_context_menu(self, note: Note, global_pos: QPoint):
        """Show context menu for existing note"""
        menu = QMenu(self)
        
        # View/Edit note
        view_action = menu.addAction("View Note")
        view_action.triggered.connect(lambda: self._emit_note_action("view", note))
        
        edit_action = menu.addAction("Edit Note")
        edit_action.triggered.connect(lambda: self._emit_note_action("edit", note))
        
        # Reply to note
        reply_action = menu.addAction("Reply to Note")
        reply_action.triggered.connect(lambda: self._emit_note_action("reply", note))
        
        menu.addSeparator()
        
        # Delete note
        delete_action = menu.addAction("Delete Note")
        delete_action.triggered.connect(lambda: self._emit_note_action("delete", note))
        
        menu.exec_(global_pos)
    
    def _show_creation_context_menu(self, pos: QPoint, global_pos: QPoint):
        """Show context menu for note creation"""
        menu = QMenu(self)
        
        add_action = menu.addAction("Add Note Here")
        add_action.triggered.connect(lambda: self._create_note_at_position(pos))
        
        menu.exec_(global_pos)
    
    def _create_note_at_position(self, pos: QPoint):
        """Create note at specified position"""
        position = Point(pos.x(), pos.y())
        self.note_creation_requested.emit(position)
    
    def _emit_note_action(self, action: str, note: Note):
        """Emit note action signal"""
        # This will be connected to main window methods
        if hasattr(self.parent(), f'handle_note_{action}'):
            getattr(self.parent(), f'handle_note_{action}')(note)

class NotePlacementManager:
    """Manages note placement and interaction in document viewers"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.position_handler = None
        self.note_mode = False
    
    def enable_note_mode(self, enabled: bool):
        """Enable or disable note creation mode"""
        self.note_mode = enabled
        
        if enabled:
            self._setup_note_positioning()
        else:
            self._cleanup_note_positioning()
    
    def _setup_note_positioning(self):
        """Setup note positioning handling"""
        if not self.main_window.document_viewer:
            return
        
        try:
            # Create note position handler
            self.position_handler = NotePositionHandler(self.main_window.document_viewer)
            self.position_handler.note_creation_requested.connect(self._on_note_creation_requested)
            
            # Show the position handler
            self.position_handler.show()
            self.position_handler.raise_()
            self.position_handler.resize(self.main_window.document_viewer.size())
            
            # Enable note mode
            self.position_handler.set_note_mode(True)
            
            # Update cursor and UI feedback
            self.main_window.statusBar().showMessage("Note mode enabled - Click to add a note", 3000)
            
            logger.info("Note positioning enabled")
            
        except Exception as e:
            logger.error(f"Failed to setup note positioning: {e}")
    
    def _cleanup_note_positioning(self):
        """Cleanup note positioning handling"""
        if self.position_handler:
            self.position_handler.hide()
            self.position_handler.deleteLater()
            self.position_handler = None
        
        self.main_window.statusBar().showMessage("Note mode disabled", 2000)
        logger.info("Note positioning disabled")
    
    def _on_note_creation_requested(self, position: Point):
        """Handle note creation request"""
        if not self.main_window.annotation_manager:
            return
        
        try:
            # Show note creation dialog
            self.main_window.show_add_note_dialog(position)
            
        except Exception as e:
            logger.error(f"Failed to handle note creation: {e}")
    
    def update_note_display(self, notes: List[Note]):
        """Update note display in position handler"""
        if self.position_handler:
            self.position_handler.set_notes(notes)
    
    def is_note_mode_active(self) -> bool:
        """Check if note mode is currently active"""
        return self.note_mode and self.position_handler is not None

class NoteRenderer(QWidget):
    """Renders note indicators as overlays on document content"""
    
    note_clicked = pyqtSignal(str)  # note_id
    note_hovered = pyqtSignal(str)  # note_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notes = []
        self.hovered_note = None
        self.scale_factor = 1.0
        self.page_offset = QPoint(0, 0)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Make widget transparent for overlay effect
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: transparent;")
    
    def set_notes(self, notes: List[Note]):
        """Set the notes to render"""
        self.notes = notes
        self.update()
    
    def set_scale_factor(self, scale: float):
        """Set the scale factor for rendering"""
        self.scale_factor = scale
        self.update()
    
    def set_page_offset(self, offset: QPoint):
        """Set the page offset for rendering"""
        self.page_offset = offset
        self.update()
    
    def paintEvent(self, event):
        """Paint note indicators as overlays"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for note in self.notes:
            self._paint_note(painter, note)
    
    def _paint_note(self, painter: QPainter, note: Note):
        """Paint a single note indicator"""
        try:
            # Calculate scaled position
            x = int(note.position.x * self.scale_factor) + self.page_offset.x()
            y = int(note.position.y * self.scale_factor) + self.page_offset.y()
            
            # Determine colors based on hover state
            if note.id == self.hovered_note:
                bg_color = QColor(255, 140, 0, 200)  # More opaque on hover
                border_color = QColor(255, 127, 0)
            else:
                bg_color = QColor(255, 165, 0, 150)  # Semi-transparent
                border_color = QColor(255, 140, 0)
            
            # Draw note indicator
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(border_color, 2))
            painter.drawEllipse(x - 10, y - 10, 20, 20)
            
            # Draw note icon
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawLine(x - 5, y - 3, x + 5, y - 3)
            painter.drawLine(x - 5, y, x + 5, y)
            painter.drawLine(x - 5, y + 3, x + 3, y + 3)
            
            # Store position for hit testing
            note._render_position = QPoint(x, y)
            note._render_radius = 10
            
        except Exception as e:
            logger.error(f"Failed to paint note {note.id}: {e}")
    
    def mousePressEvent(self, event):
        """Handle mouse clicks on notes"""
        if event.button() == Qt.LeftButton:
            clicked_note = self._get_note_at_position(event.pos())
            if clicked_note:
                self.note_clicked.emit(clicked_note.id)
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse hover over notes"""
        hovered_note = self._get_note_at_position(event.pos())
        
        if hovered_note:
            if self.hovered_note != hovered_note.id:
                self.hovered_note = hovered_note.id
                self.note_hovered.emit(hovered_note.id)
                self.update()
                
                # Set tooltip
                tooltip = f"Note: {hovered_note.plain_text[:100]}"
                if len(hovered_note.plain_text) > 100:
                    tooltip += "..."
                self.setToolTip(tooltip)
        else:
            if self.hovered_note:
                self.hovered_note = None
                self.update()
                self.setToolTip("")
        
        super().mouseMoveEvent(event)
    
    def _get_note_at_position(self, pos: QPoint) -> Optional[Note]:
        """Get note at the given position"""
        for note in self.notes:
            if hasattr(note, '_render_position') and hasattr(note, '_render_radius'):
                distance = (pos - note._render_position).manhattanLength()
                if distance <= note._render_radius:
                    return note
        return None