"""
Annotation Toolbar - Quick access to annotation tools
"""

from PyQt5.QtWidgets import (
    QToolBar, QAction, QActionGroup, QMenu, QWidgetAction, 
    QWidget, QHBoxLayout, QPushButton, QButtonGroup
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from qfluentwidgets import PushButton
import logging

from ..models import HighlightColor

logger = logging.getLogger("ebook_reader")

class ColorButton(QPushButton):
    """Button that displays a color for highlight selection"""
    
    color_selected = pyqtSignal(str)  # color value
    
    def __init__(self, color: str, color_name: str, parent=None):
        super().__init__(parent)
        self.color = color
        self.color_name = color_name
        
        self.setFixedSize(24, 24)
        self.setToolTip(f"Highlight with {color_name}")
        self.setCheckable(True)
        
        # Create color icon
        self.update_icon()
        
        self.clicked.connect(lambda: self.color_selected.emit(self.color))
    
    def update_icon(self):
        """Update the button icon with the color"""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw color circle
        painter.setBrush(QColor(self.color))
        painter.setPen(QColor("#333"))
        painter.drawEllipse(2, 2, 16, 16)
        
        painter.end()
        
        self.setIcon(QIcon(pixmap))

class HighlightColorPalette(QWidget):
    """Widget containing highlight color selection buttons"""
    
    color_selected = pyqtSignal(str)  # color value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the color palette UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # Create button group for exclusive selection
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        # Add color buttons
        colors = [
            (HighlightColor.YELLOW.value, "Yellow"),
            (HighlightColor.GREEN.value, "Green"),
            (HighlightColor.BLUE.value, "Blue"),
            (HighlightColor.PINK.value, "Pink"),
            (HighlightColor.ORANGE.value, "Orange"),
            (HighlightColor.PURPLE.value, "Purple"),
        ]
        
        for color_value, color_name in colors:
            button = ColorButton(color_value, color_name)
            button.color_selected.connect(self.color_selected.emit)
            
            self.button_group.addButton(button)
            layout.addWidget(button)
        
        # Select yellow by default
        if self.button_group.buttons():
            self.button_group.buttons()[0].setChecked(True)
    
    def get_selected_color(self) -> str:
        """Get the currently selected color"""
        for button in self.button_group.buttons():
            if button.isChecked():
                return button.color
        return HighlightColor.YELLOW.value  # Default
    
    def set_selected_color(self, color: str):
        """Set the selected color"""
        for button in self.button_group.buttons():
            if button.color == color:
                button.setChecked(True)
                break

class AnnotationToolbar(QToolBar):
    """Main toolbar for annotation tools"""
    
    # Bookmark signals
    add_bookmark_requested = pyqtSignal()
    toggle_bookmarks_panel = pyqtSignal()
    
    # Highlight signals
    highlight_mode_toggled = pyqtSignal(bool)  # enabled
    highlight_color_changed = pyqtSignal(str)  # color
    
    # Note signals
    add_note_requested = pyqtSignal()
    toggle_notes_panel = pyqtSignal()
    
    # General signals
    toggle_annotations_panel = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Annotations", parent)
        self.highlight_mode = False
        self.init_actions()
        self.init_widgets()
    
    def init_actions(self):
        """Initialize toolbar actions"""
        # Bookmark actions
        self.add_bookmark_action = QAction("Bookmark", self)
        self.add_bookmark_action.setToolTip("Add/remove bookmark on current page (Ctrl+B)")
        self.add_bookmark_action.setShortcut("Ctrl+B")
        self.add_bookmark_action.triggered.connect(self.add_bookmark_requested.emit)
        self.addAction(self.add_bookmark_action)
        
        # Highlight mode toggle
        self.highlight_action = QAction("Highlight", self)
        self.highlight_action.setToolTip("Toggle highlight mode (Ctrl+H)")
        self.highlight_action.setShortcut("Ctrl+H")
        self.highlight_action.setCheckable(True)
        self.highlight_action.triggered.connect(self.toggle_highlight_mode)
        self.addAction(self.highlight_action)
        
        # Note action
        self.add_note_action = QAction("Note", self)
        self.add_note_action.setToolTip("Add note at cursor position (Ctrl+N)")
        self.add_note_action.setShortcut("Ctrl+N")
        self.add_note_action.triggered.connect(self.add_note_requested.emit)
        self.addAction(self.add_note_action)
        
        self.addSeparator()
        
        # Panel toggles
        self.bookmarks_panel_action = QAction("Bookmarks Panel", self)
        self.bookmarks_panel_action.setToolTip("Show/hide bookmarks panel")
        self.bookmarks_panel_action.setCheckable(True)
        self.bookmarks_panel_action.triggered.connect(self.toggle_bookmarks_panel.emit)
        self.addAction(self.bookmarks_panel_action)
        
        self.annotations_panel_action = QAction("Annotations Panel", self)
        self.annotations_panel_action.setToolTip("Show/hide annotations panel")
        self.annotations_panel_action.setCheckable(True)
        self.annotations_panel_action.triggered.connect(self.toggle_annotations_panel.emit)
        self.addAction(self.annotations_panel_action)
    
    def init_widgets(self):
        """Initialize toolbar widgets"""
        self.addSeparator()
        
        # Highlight color palette
        self.color_palette = HighlightColorPalette()
        self.color_palette.color_selected.connect(self.highlight_color_changed.emit)
        self.color_palette.setVisible(False)  # Hidden by default
        
        palette_action = QWidgetAction(self)
        palette_action.setDefaultWidget(self.color_palette)
        self.addAction(palette_action)
    
    def toggle_highlight_mode(self, enabled: bool):
        """Toggle highlight mode"""
        self.highlight_mode = enabled
        self.color_palette.setVisible(enabled)
        self.highlight_mode_toggled.emit(enabled)
        
        # Update action text
        if enabled:
            self.highlight_action.setText("Exit Highlight")
            self.highlight_action.setToolTip("Exit highlight mode (Ctrl+H)")
        else:
            self.highlight_action.setText("Highlight")
            self.highlight_action.setToolTip("Toggle highlight mode (Ctrl+H)")
    
    def set_bookmark_exists(self, exists: bool):
        """Update bookmark action based on whether bookmark exists on current page"""
        if exists:
            self.add_bookmark_action.setText("Remove Bookmark")
            self.add_bookmark_action.setToolTip("Remove bookmark from current page (Ctrl+B)")
        else:
            self.add_bookmark_action.setText("Add Bookmark")
            self.add_bookmark_action.setToolTip("Add bookmark to current page (Ctrl+B)")
    
    def set_panel_visibility(self, panel_name: str, visible: bool):
        """Update panel toggle actions"""
        if panel_name == "bookmarks":
            self.bookmarks_panel_action.setChecked(visible)
        elif panel_name == "annotations":
            self.annotations_panel_action.setChecked(visible)
    
    def get_selected_highlight_color(self) -> str:
        """Get the currently selected highlight color"""
        return self.color_palette.get_selected_color()
    
    def set_highlight_color(self, color: str):
        """Set the selected highlight color"""
        self.color_palette.set_selected_color(color)
    
    def enable_actions(self, enabled: bool):
        """Enable/disable all actions (when no document is loaded)"""
        for action in self.actions():
            if not action.isSeparator():
                action.setEnabled(enabled)
    
    def set_highlight_mode(self, enabled: bool):
        """Set highlight mode state (external control)"""
        self.highlight_action.setChecked(enabled)
        self.toggle_highlight_mode(enabled)