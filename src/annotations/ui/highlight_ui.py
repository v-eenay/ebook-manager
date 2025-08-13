"""
Highlight UI Components
User interface elements for text highlighting functionality
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMenu, QMessageBox, QComboBox,
    QFrame, QScrollArea, QGroupBox, QFormLayout, QDialogButtonBox,
    QTextEdit, QColorDialog, QButtonGroup, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint, QSize
from PyQt5.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont, QPalette, QPixmap,
    QTextCharFormat, QTextCursor, QPainterPath
)
from qfluentwidgets import (
    PushButton, LineEdit, TextEdit, ListWidget, ComboBox,
    BodyLabel, CaptionLabel, ScrollArea
)
import logging
from typing import List, Optional, Dict, Tuple
from datetime import datetime

from ..models import Highlight, AnnotationCategory, HighlightColor, TextSelection, Point
from ..highlight_manager import HighlightManager

logger = logging.getLogger("ebook_reader")

class HighlightRenderer(QWidget):
    """Widget that renders highlights as overlays on document content"""
    
    highlight_clicked = pyqtSignal(str)  # highlight_id
    highlight_hovered = pyqtSignal(str)  # highlight_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlights = []
        self.hovered_highlight = None
        self.scale_factor = 1.0
        self.page_offset = QPoint(0, 0)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Make widget transparent for overlay effect
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: transparent;")
    
    def set_highlights(self, highlights: List[Highlight]):
        """Set the highlights to render"""
        self.highlights = highlights
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
        """Paint highlights as overlays"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for highlight in self.highlights:
            self._paint_highlight(painter, highlight)
    
    def _paint_highlight(self, painter: QPainter, highlight: Highlight):
        """Paint a single highlight"""
        try:
            # Calculate scaled positions
            start_pos = self._scale_point(highlight.text_selection.start_position)
            end_pos = self._scale_point(highlight.text_selection.end_position)
            
            # Create highlight rectangle
            rect = QRect(
                start_pos.x() + self.page_offset.x(),
                start_pos.y() + self.page_offset.y(),
                end_pos.x() - start_pos.x(),
                max(end_pos.y() - start_pos.y(), 20)  # Minimum height
            )
            
            # Set highlight color with transparency
            color = QColor(highlight.color)
            if highlight.id == self.hovered_highlight:
                color.setAlpha(180)  # More opaque on hover
            else:
                color.setAlpha(120)  # Semi-transparent
            
            # Draw highlight background
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(rect)
            
            # Draw border for hovered highlight
            if highlight.id == self.hovered_highlight:
                border_color = QColor(highlight.color).darker(150)
                painter.setPen(QPen(border_color, 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(rect)
            
            # Store rect for hit testing
            highlight._render_rect = rect
            
        except Exception as e:
            logger.error(f"Failed to paint highlight {highlight.id}: {e}")
    
    def _scale_point(self, point: Point) -> QPoint:
        """Scale a point according to current scale factor"""
        return QPoint(
            int(point.x * self.scale_factor),
            int(point.y * self.scale_factor)
        )
    
    def mousePressEvent(self, event):
        """Handle mouse clicks on highlights"""
        if event.button() == Qt.LeftButton:
            clicked_highlight = self._get_highlight_at_position(event.pos())
            if clicked_highlight:
                self.highlight_clicked.emit(clicked_highlight.id)
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse hover over highlights"""
        hovered_highlight = self._get_highlight_at_position(event.pos())
        
        if hovered_highlight:
            if self.hovered_highlight != hovered_highlight.id:
                self.hovered_highlight = hovered_highlight.id
                self.highlight_hovered.emit(hovered_highlight.id)
                self.update()
                
                # Set tooltip
                tooltip = f"{hovered_highlight.highlighted_text[:100]}"
                if hovered_highlight.note:
                    tooltip += f"\n\nNote: {hovered_highlight.note}"
                self.setToolTip(tooltip)
        else:
            if self.hovered_highlight:
                self.hovered_highlight = None
                self.update()
                self.setToolTip("")
        
        super().mouseMoveEvent(event)
    
    def _get_highlight_at_position(self, pos: QPoint) -> Optional[Highlight]:
        """Get highlight at the given position"""
        for highlight in self.highlights:
            if hasattr(highlight, '_render_rect') and highlight._render_rect.contains(pos):
                return highlight
        return None

class HighlightColorSelector(QWidget):
    """Widget for selecting highlight colors"""
    
    color_selected = pyqtSignal(str)  # color value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_color = HighlightColor.YELLOW.value
        self.init_ui()
    
    def init_ui(self):
        """Initialize the color selector UI"""
        layout = QGridLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Create button group for exclusive selection
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        # Predefined colors
        colors = [
            (HighlightColor.YELLOW.value, "Yellow", 0, 0),
            (HighlightColor.GREEN.value, "Green", 0, 1),
            (HighlightColor.BLUE.value, "Blue", 0, 2),
            (HighlightColor.PINK.value, "Pink", 1, 0),
            (HighlightColor.ORANGE.value, "Orange", 1, 1),
            (HighlightColor.PURPLE.value, "Purple", 1, 2),
        ]
        
        for color_value, color_name, row, col in colors:
            button = self._create_color_button(color_value, color_name)
            self.button_group.addButton(button)
            layout.addWidget(button, row, col)
        
        # Custom color button
        custom_button = QPushButton("Custom...")
        custom_button.setFixedSize(60, 30)
        custom_button.clicked.connect(self.show_custom_color_dialog)
        layout.addWidget(custom_button, 2, 0, 1, 3)
        
        # Select yellow by default
        if self.button_group.buttons():
            self.button_group.buttons()[0].setChecked(True)
    
    def _create_color_button(self, color: str, name: str) -> QPushButton:
        """Create a color selection button"""
        button = QPushButton()
        button.setFixedSize(60, 30)
        button.setCheckable(True)
        button.setToolTip(f"Highlight with {name}")
        
        # Set button style with color
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 2px solid #ccc;
                border-radius: 4px;
            }}
            QPushButton:checked {{
                border-color: #0078d4;
                border-width: 3px;
            }}
            QPushButton:hover {{
                border-color: #666;
            }}
        """)
        
        button.clicked.connect(lambda: self._on_color_selected(color))
        return button
    
    def _on_color_selected(self, color: str):
        """Handle color selection"""
        self.selected_color = color
        self.color_selected.emit(color)
    
    def show_custom_color_dialog(self):
        """Show custom color selection dialog"""
        color = QColorDialog.getColor(QColor(self.selected_color), self)
        if color.isValid():
            color_hex = color.name()
            self.selected_color = color_hex
            self.color_selected.emit(color_hex)
    
    def get_selected_color(self) -> str:
        """Get the currently selected color"""
        return self.selected_color
    
    def set_selected_color(self, color: str):
        """Set the selected color"""
        self.selected_color = color
        # Update button selection if it's a predefined color
        for button in self.button_group.buttons():
            button_color = button.toolTip().split()[-1].lower()  # Extract color from tooltip
            if color.lower() in button_color:
                button.setChecked(True)
                break

class HighlightDialog(QDialog):
    """Dialog for editing highlight properties"""
    
    highlight_saved = pyqtSignal(object)  # Highlight object
    
    def __init__(self, highlight: Optional[Highlight] = None,
                 categories: List[AnnotationCategory] = None, parent=None):
        super().__init__(parent)
        self.highlight = highlight
        self.categories = categories or []
        self.is_editing = highlight is not None
        
        self.init_ui()
        self.setup_connections()
        
        if self.is_editing:
            self.load_highlight_data()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Edit Highlight" if self.is_editing else "Add Note to Highlight")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title_label = BodyLabel("Highlight Properties")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Highlighted text (read-only)
        if self.highlight:
            text_label = BodyLabel("Highlighted Text:")
            layout.addWidget(text_label)
            
            text_display = QTextEdit()
            text_display.setPlainText(self.highlight.highlighted_text)
            text_display.setReadOnly(True)
            text_display.setMaximumHeight(80)
            text_display.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ccc;")
            layout.addWidget(text_display)
        
        # Form layout
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(8)
        
        # Color selection
        self.color_selector = HighlightColorSelector()
        form_layout.addRow("Color:", self.color_selector)
        
        # Note input
        self.note_input = TextEdit()
        self.note_input.setPlaceholderText("Add a note to this highlight (optional)...")
        self.note_input.setMaximumHeight(100)
        form_layout.addRow("Note:", self.note_input)
        
        # Category selection
        self.category_combo = ComboBox()
        self.category_combo.addItem("Default", "default")
        for category in self.categories:
            self.category_combo.addItem(category.name, category.id)
        form_layout.addRow("Category:", self.category_combo)
        
        layout.addWidget(form_widget)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("Save Changes" if self.is_editing else "Add Note")
        
        layout.addWidget(button_box)
        
        # Connect buttons
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.color_selector.color_selected.connect(self.on_color_changed)
    
    def on_color_changed(self, color: str):
        """Handle color change"""
        if self.highlight:
            self.highlight.color = color
    
    def load_highlight_data(self):
        """Load existing highlight data into form"""
        if self.highlight:
            self.color_selector.set_selected_color(self.highlight.color)
            self.note_input.setPlainText(self.highlight.note)
            
            # Set category
            for i in range(self.category_combo.count()):
                if self.category_combo.itemData(i) == self.highlight.category:
                    self.category_combo.setCurrentIndex(i)
                    break
    
    def get_highlight_data(self) -> Dict:
        """Get highlight data from form"""
        return {
            'color': self.color_selector.get_selected_color(),
            'note': self.note_input.toPlainText().strip(),
            'category': self.category_combo.currentData()
        }
    
    def accept(self):
        """Handle dialog acceptance"""
        data = self.get_highlight_data()
        
        if self.highlight:
            # Update existing highlight
            self.highlight.color = data['color']
            self.highlight.note = data['note']
            self.highlight.category = data['category']
            self.highlight.update_timestamp()
        
        self.highlight_saved.emit(self.highlight)
        super().accept()

class HighlightListItem(QWidget):
    """Custom list item for highlights"""
    
    highlight_clicked = pyqtSignal(str)  # highlight_id
    highlight_edited = pyqtSignal(str)   # highlight_id
    highlight_deleted = pyqtSignal(str)  # highlight_id
    
    def __init__(self, highlight: Highlight, parent=None):
        super().__init__(parent)
        self.highlight = highlight
        self.init_ui()
    
    def init_ui(self):
        """Initialize the list item UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        
        # Header with color indicator and page
        header_layout = QHBoxLayout()
        
        # Color indicator
        color_indicator = QWidget()
        color_indicator.setFixedSize(16, 16)
        color_indicator.setStyleSheet(f"""
            background-color: {self.highlight.color};
            border: 1px solid #ccc;
            border-radius: 8px;
        """)
        header_layout.addWidget(color_indicator)
        
        # Highlighted text preview
        text_preview = self.highlight.highlighted_text[:50]
        if len(self.highlight.highlighted_text) > 50:
            text_preview += "..."
        
        text_label = BodyLabel(f'"{text_preview}"')
        text_label.setStyleSheet("font-weight: bold; color: #333;")
        header_layout.addWidget(text_label)
        
        header_layout.addStretch()
        
        # Page number
        page_label = CaptionLabel(f"Page {self.highlight.page_number}")
        page_label.setStyleSheet("color: #666;")
        header_layout.addWidget(page_label)
        
        layout.addLayout(header_layout)
        
        # Note (if exists)
        if self.highlight.note:
            note_label = CaptionLabel(self.highlight.note)
            note_label.setStyleSheet("color: #888; font-style: italic;")
            note_label.setWordWrap(True)
            layout.addWidget(note_label)
        
        # Footer with date and category
        footer_layout = QHBoxLayout()
        
        # Date
        date_str = self.highlight.created_at.strftime("%m/%d/%Y %H:%M")
        date_label = CaptionLabel(date_str)
        date_label.setStyleSheet("color: #999; font-size: 10px;")
        footer_layout.addWidget(date_label)
        
        footer_layout.addStretch()
        
        # Category (if not default)
        if self.highlight.category != "default":
            category_label = CaptionLabel(self.highlight.category)
            category_label.setStyleSheet("color: #0078d4; font-size: 10px;")
            footer_layout.addWidget(category_label)
        
        layout.addLayout(footer_layout)
        
        # Style the widget
        self.setStyleSheet("""
            HighlightListItem {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                margin: 2px;
            }
            HighlightListItem:hover {
                background-color: #f5f5f5;
                border-color: #0078d4;
            }
        """)
        
        # Make clickable
        self.setCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks"""
        if event.button() == Qt.LeftButton:
            self.highlight_clicked.emit(self.highlight.id)
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())
        super().mousePressEvent(event)
    
    def show_context_menu(self, position):
        """Show context menu for highlight"""
        menu = QMenu(self)
        
        edit_action = menu.addAction("Edit Highlight")
        edit_action.triggered.connect(lambda: self.highlight_edited.emit(self.highlight.id))
        
        delete_action = menu.addAction("Delete Highlight")
        delete_action.triggered.connect(self.confirm_delete)
        
        menu.exec_(position)
    
    def confirm_delete(self):
        """Confirm highlight deletion"""
        reply = QMessageBox.question(
            self, "Delete Highlight",
            f"Are you sure you want to delete this highlight?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.highlight_deleted.emit(self.highlight.id)

class HighlightPanel(QWidget):
    """Panel for managing highlights"""
    
    highlight_selected = pyqtSignal(str, int)  # document_path, page_number
    highlight_edited = pyqtSignal(str)         # highlight_id
    highlight_deleted = pyqtSignal(str)        # highlight_id
    
    def __init__(self, highlight_manager: HighlightManager, parent=None):
        super().__init__(parent)
        self.highlight_manager = highlight_manager
        self.current_document = None
        self.highlights = []
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = BodyLabel("Highlights")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        # Color filter
        self.color_filter = ComboBox()
        self.color_filter.addItem("All Colors", "")
        filter_layout.addWidget(self.color_filter)
        
        # Category filter
        self.category_filter = ComboBox()
        self.category_filter.addItem("All Categories", "")
        filter_layout.addWidget(self.category_filter)
        
        layout.addLayout(filter_layout)
        
        # Search
        self.search_input = LineEdit()
        self.search_input.setPlaceholderText("Search highlights...")
        layout.addWidget(self.search_input)
        
        # Highlights list
        self.highlights_scroll = ScrollArea()
        self.highlights_scroll.setWidgetResizable(True)
        self.highlights_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.highlights_container = QWidget()
        self.highlights_layout = QVBoxLayout(self.highlights_container)
        self.highlights_layout.setContentsMargins(0, 0, 0, 0)
        self.highlights_layout.setSpacing(4)
        self.highlights_layout.addStretch()
        
        self.highlights_scroll.setWidget(self.highlights_container)
        layout.addWidget(self.highlights_scroll)
        
        # Status label
        self.status_label = CaptionLabel("No highlights")
        self.status_label.setStyleSheet("color: #888; text-align: center;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.search_input.textChanged.connect(self.filter_highlights)
        self.color_filter.currentTextChanged.connect(self.filter_highlights)
        self.category_filter.currentTextChanged.connect(self.filter_highlights)
    
    def set_document(self, document_path: str):
        """Set the current document and load its highlights"""
        self.current_document = document_path
        self.load_highlights()
    
    def load_highlights(self):
        """Load highlights for the current document"""
        if not self.current_document:
            self.highlights = []
        else:
            self.highlights = self.highlight_manager.get_highlights(self.current_document)
        
        self.update_filters()
        self.display_highlights()
    
    def update_filters(self):
        """Update filter options"""
        # Update color filter
        current_color = self.color_filter.currentData()
        self.color_filter.clear()
        self.color_filter.addItem("All Colors", "")
        
        colors = set(h.color for h in self.highlights)
        for color in sorted(colors):
            color_name = self._get_color_name(color)
            self.color_filter.addItem(color_name, color)
        
        # Restore selection
        for i in range(self.color_filter.count()):
            if self.color_filter.itemData(i) == current_color:
                self.color_filter.setCurrentIndex(i)
                break
        
        # Update category filter
        current_category = self.category_filter.currentData()
        self.category_filter.clear()
        self.category_filter.addItem("All Categories", "")
        
        categories = set(h.category for h in self.highlights if h.category != "default")
        for category in sorted(categories):
            self.category_filter.addItem(category, category)
        
        # Restore selection
        for i in range(self.category_filter.count()):
            if self.category_filter.itemData(i) == current_category:
                self.category_filter.setCurrentIndex(i)
                break
    
    def _get_color_name(self, color: str) -> str:
        """Get display name for color"""
        color_names = {
            HighlightColor.YELLOW.value: "Yellow",
            HighlightColor.GREEN.value: "Green",
            HighlightColor.BLUE.value: "Blue",
            HighlightColor.PINK.value: "Pink",
            HighlightColor.ORANGE.value: "Orange",
            HighlightColor.PURPLE.value: "Purple",
        }
        return color_names.get(color, color)
    
    def display_highlights(self):
        """Display filtered highlights in the list"""
        # Clear existing items
        while self.highlights_layout.count() > 1:  # Keep the stretch
            item = self.highlights_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Filter highlights
        filtered_highlights = self.get_filtered_highlights()
        
        # Add highlight items
        for highlight in filtered_highlights:
            item_widget = HighlightListItem(highlight)
            item_widget.highlight_clicked.connect(self.on_highlight_clicked)
            item_widget.highlight_edited.connect(self.highlight_edited.emit)
            item_widget.highlight_deleted.connect(self.highlight_deleted.emit)
            
            self.highlights_layout.insertWidget(self.highlights_layout.count() - 1, item_widget)
        
        # Update status
        if filtered_highlights:
            self.status_label.setText(f"{len(filtered_highlights)} highlight(s)")
        else:
            self.status_label.setText("No highlights found")
    
    def get_filtered_highlights(self) -> List[Highlight]:
        """Get highlights filtered by search and filters"""
        filtered = self.highlights
        
        # Filter by search text
        search_text = self.search_input.text().strip().lower()
        if search_text:
            filtered = [
                h for h in filtered
                if (search_text in h.highlighted_text.lower() or 
                    search_text in h.note.lower())
            ]
        
        # Filter by color
        color_filter = self.color_filter.currentData()
        if color_filter:
            filtered = [h for h in filtered if h.color == color_filter]
        
        # Filter by category
        category_filter = self.category_filter.currentData()
        if category_filter:
            filtered = [h for h in filtered if h.category == category_filter]
        
        # Sort by page number, then by position
        filtered.sort(key=lambda h: (h.page_number, h.text_selection.start_char_index))
        
        return filtered
    
    def filter_highlights(self):
        """Apply filters and update display"""
        self.display_highlights()
    
    def on_highlight_clicked(self, highlight_id: str):
        """Handle highlight selection"""
        highlight = next((h for h in self.highlights if h.id == highlight_id), None)
        if highlight:
            self.highlight_selected.emit(highlight.document_path, highlight.page_number)
    
    def refresh(self):
        """Refresh the highlight list"""
        self.load_highlights()