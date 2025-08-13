"""
Note UI Components
User interface elements for note and comment functionality
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMenu, QMessageBox, QComboBox,
    QFrame, QScrollArea, QGroupBox, QFormLayout, QDialogButtonBox,
    QTextEdit, QLineEdit, QSplitter, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QAbstractItemView, QToolBar, QAction, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize, QTimer
from PyQt5.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont, QPalette, QPixmap,
    QTextCharFormat, QTextCursor, QIcon, QTextDocument
)
from qfluentwidgets import (
    PushButton, LineEdit, TextEdit, ListWidget, ComboBox,
    BodyLabel, CaptionLabel, ScrollArea, TreeWidget
)
import logging
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import html

from ..models import Note, AnnotationCategory, Point
from ..note_manager import NoteManager

logger = logging.getLogger("ebook_reader")

class RichTextEditor(QTextEdit):
    """Rich text editor for note content"""
    
    content_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_editor()
        self.setup_toolbar()
        
        # Connect signals
        self.textChanged.connect(self.content_changed.emit)
    
    def setup_editor(self):
        """Setup the rich text editor"""
        self.setMinimumHeight(150)
        self.setMaximumHeight(300)
        
        # Set font
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        
        # Enable rich text
        self.setAcceptRichText(True)
        
        # Set placeholder
        self.setPlaceholderText("Enter your note here... You can use rich text formatting.")
        
        # Style the editor
        self.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                selection-background-color: #0078d4;
            }
            QTextEdit:focus {
                border-color: #0078d4;
            }
        """)
    
    def setup_toolbar(self):
        """Setup formatting toolbar"""
        # This will be added as a separate widget above the editor
        pass
    
    def get_plain_text(self) -> str:
        """Get plain text content"""
        return self.toPlainText()
    
    def get_html_content(self) -> str:
        """Get HTML content"""
        return self.toHtml()
    
    def set_html_content(self, html_content: str):
        """Set HTML content"""
        self.setHtml(html_content)
    
    def set_plain_content(self, plain_content: str):
        """Set plain text content"""
        self.setPlainText(plain_content)
    
    def insert_text(self, text: str):
        """Insert text at cursor position"""
        cursor = self.textCursor()
        cursor.insertText(text)
    
    def apply_bold(self):
        """Apply bold formatting"""
        cursor = self.textCursor()
        format = cursor.charFormat()
        format.setFontWeight(QFont.Bold if format.fontWeight() != QFont.Bold else QFont.Normal)
        cursor.setCharFormat(format)
    
    def apply_italic(self):
        """Apply italic formatting"""
        cursor = self.textCursor()
        format = cursor.charFormat()
        format.setFontItalic(not format.fontItalic())
        cursor.setCharFormat(format)
    
    def apply_underline(self):
        """Apply underline formatting"""
        cursor = self.textCursor()
        format = cursor.charFormat()
        format.setFontUnderline(not format.fontUnderline())
        cursor.setCharFormat(format)

class NoteFormattingToolbar(QToolBar):
    """Formatting toolbar for rich text editor"""
    
    def __init__(self, editor: RichTextEditor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setup_actions()
    
    def setup_actions(self):
        """Setup formatting actions"""
        # Bold action
        self.bold_action = QAction("B", self)
        self.bold_action.setToolTip("Bold (Ctrl+B)")
        self.bold_action.setCheckable(True)
        self.bold_action.setShortcut("Ctrl+B")
        self.bold_action.triggered.connect(self.editor.apply_bold)
        self.addAction(self.bold_action)
        
        # Italic action
        self.italic_action = QAction("I", self)
        self.italic_action.setToolTip("Italic (Ctrl+I)")
        self.italic_action.setCheckable(True)
        self.italic_action.setShortcut("Ctrl+I")
        self.italic_action.triggered.connect(self.editor.apply_italic)
        self.addAction(self.italic_action)
        
        # Underline action
        self.underline_action = QAction("U", self)
        self.underline_action.setToolTip("Underline (Ctrl+U)")
        self.underline_action.setCheckable(True)
        self.underline_action.setShortcut("Ctrl+U")
        self.underline_action.triggered.connect(self.editor.apply_underline)
        self.addAction(self.underline_action)
        
        self.addSeparator()
        
        # Clear formatting action
        self.clear_action = QAction("Clear", self)
        self.clear_action.setToolTip("Clear formatting")
        self.clear_action.triggered.connect(self.clear_formatting)
        self.addAction(self.clear_action)
        
        # Style the toolbar
        self.setStyleSheet("""
            QToolBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #f8f8f8;
                spacing: 2px;
                padding: 2px;
            }
            QToolBar QAction {
                padding: 4px 8px;
                margin: 1px;
                border-radius: 2px;
            }
            QToolBar QAction:hover {
                background-color: #e0e0e0;
            }
            QToolBar QAction:checked {
                background-color: #0078d4;
                color: white;
            }
        """)
    
    def clear_formatting(self):
        """Clear all formatting"""
        cursor = self.editor.textCursor()
        format = QTextCharFormat()
        cursor.setCharFormat(format)

class NoteIndicator(QWidget):
    """Visual note indicator for document margins"""
    
    clicked = pyqtSignal(str)  # note_id
    
    def __init__(self, note: Note, parent=None):
        super().__init__(parent)
        self.note = note
        self.setFixedSize(20, 20)
        self.setToolTip(f"Note: {note.plain_text[:100]}...")
        self.setCursor(Qt.PointingHandCursor)
        
        # Style the indicator
        self.setStyleSheet("""
            NoteIndicator {
                background-color: #FFA500;
                border: 2px solid #FF8C00;
                border-radius: 10px;
            }
            NoteIndicator:hover {
                background-color: #FF8C00;
                border-color: #FF7F00;
            }
        """)
    
    def paintEvent(self, event):
        """Custom paint event for note icon"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw note icon (simple document shape)
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QColor(255, 255, 255))
        
        # Simple note shape
        points = [
            (4, 3), (16, 3), (16, 13), (13, 16), (4, 16)
        ]
        
        from PyQt5.QtGui import QPolygon
        from PyQt5.QtCore import QPoint
        polygon = QPolygon([QPoint(x, y) for x, y in points])
        painter.drawPolygon(polygon)
        
        # Draw fold line
        painter.drawLine(13, 13, 16, 13)
        painter.drawLine(13, 13, 13, 16)
    
    def mousePressEvent(self, event):
        """Handle click events"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.note.id)
        super().mousePressEvent(event)

class NoteDialog(QDialog):
    """Dialog for creating and editing notes"""
    
    note_saved = pyqtSignal(object)  # Note object
    
    def __init__(self, note: Optional[Note] = None, 
                 categories: List[AnnotationCategory] = None, 
                 position: Optional[Point] = None, parent=None):
        super().__init__(parent)
        self.note = note
        self.categories = categories or []
        self.position = position
        self.is_editing = note is not None
        
        self.init_ui()
        self.setup_connections()
        
        if self.is_editing:
            self.load_note_data()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Edit Note" if self.is_editing else "Add Note")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title section
        title_label = BodyLabel("Note Details")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Form layout
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(8)
        
        # Category selection
        self.category_combo = ComboBox()
        self.category_combo.addItem("Default", "default")
        for category in self.categories:
            self.category_combo.addItem(category.name, category.id)
        form_layout.addRow("Category:", self.category_combo)
        
        layout.addWidget(form_widget)
        
        # Rich text editor with toolbar
        editor_group = QGroupBox("Note Content")
        editor_layout = QVBoxLayout(editor_group)
        
        # Create rich text editor
        self.content_editor = RichTextEditor()
        
        # Create formatting toolbar
        self.formatting_toolbar = NoteFormattingToolbar(self.content_editor)
        
        editor_layout.addWidget(self.formatting_toolbar)
        editor_layout.addWidget(self.content_editor)
        
        layout.addWidget(editor_group)
        
        # Position info (if creating new note)
        if not self.is_editing and self.position:
            pos_label = CaptionLabel(f"Position: ({self.position.x:.0f}, {self.position.y:.0f})")
            pos_label.setStyleSheet("color: #666; font-style: italic;")
            layout.addWidget(pos_label)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("Save Note" if self.is_editing else "Add Note")
        
        layout.addWidget(button_box)
        
        # Connect buttons
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.content_editor.content_changed.connect(self.validate_input)
        self.validate_input()  # Initial validation
    
    def validate_input(self):
        """Validate input and enable/disable OK button"""
        content = self.content_editor.get_plain_text().strip()
        ok_button = self.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok)
        ok_button.setEnabled(bool(content))
    
    def load_note_data(self):
        """Load existing note data into form"""
        if self.note:
            self.content_editor.set_html_content(self.note.content)
            
            # Set category
            for i in range(self.category_combo.count()):
                if self.category_combo.itemData(i) == self.note.category:
                    self.category_combo.setCurrentIndex(i)
                    break
    
    def get_note_data(self) -> Dict:
        """Get note data from form"""
        return {
            'content': self.content_editor.get_html_content(),
            'plain_text': self.content_editor.get_plain_text(),
            'category': self.category_combo.currentData()
        }
    
    def accept(self):
        """Handle dialog acceptance"""
        data = self.get_note_data()
        
        if self.is_editing and self.note:
            # Update existing note
            self.note.content = data['content']
            self.note.plain_text = data['plain_text']
            self.note.category = data['category']
            self.note.update_timestamp()
        else:
            # Create new note (will be handled by caller)
            pass
        
        self.note_saved.emit(self.note)
        super().accept()

class NoteListItem(QWidget):
    """Custom list item for notes"""
    
    note_clicked = pyqtSignal(str)  # note_id
    note_edited = pyqtSignal(str)   # note_id
    note_deleted = pyqtSignal(str)  # note_id
    note_replied = pyqtSignal(str)  # note_id
    
    def __init__(self, note: Note, is_reply: bool = False, parent=None):
        super().__init__(parent)
        self.note = note
        self.is_reply = is_reply
        self.init_ui()
    
    def init_ui(self):
        """Initialize the list item UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12 if not self.is_reply else 24, 8, 12, 8)
        layout.setSpacing(6)
        
        # Header with page and date
        header_layout = QHBoxLayout()
        
        # Reply indicator
        if self.is_reply:
            reply_label = CaptionLabel("↳ Reply")
            reply_label.setStyleSheet("color: #0078d4; font-weight: bold;")
            header_layout.addWidget(reply_label)
        
        # Page number
        page_label = BodyLabel(f"Page {self.note.page_number}")
        page_label.setStyleSheet("font-weight: bold; color: #333;")
        header_layout.addWidget(page_label)
        
        header_layout.addStretch()
        
        # Date
        date_str = self.note.created_at.strftime("%m/%d/%Y %H:%M")
        date_label = CaptionLabel(date_str)
        date_label.setStyleSheet("color: #666;")
        header_layout.addWidget(date_label)
        
        layout.addLayout(header_layout)
        
        # Note content preview
        content_preview = self.note.plain_text[:200]
        if len(self.note.plain_text) > 200:
            content_preview += "..."
        
        content_label = BodyLabel(content_preview)
        content_label.setWordWrap(True)
        content_label.setStyleSheet("color: #333; line-height: 1.4;")
        layout.addWidget(content_label)
        
        # Footer with category
        footer_layout = QHBoxLayout()
        
        # Category (if not default)
        if self.note.category != "default":
            category_label = CaptionLabel(f"Category: {self.note.category}")
            category_label.setStyleSheet("color: #0078d4; font-size: 10px;")
            footer_layout.addWidget(category_label)
        
        footer_layout.addStretch()
        
        # Position info
        pos_label = CaptionLabel(f"({self.note.position.x:.0f}, {self.note.position.y:.0f})")
        pos_label.setStyleSheet("color: #999; font-size: 10px;")
        footer_layout.addWidget(pos_label)
        
        layout.addLayout(footer_layout)
        
        # Style the widget
        border_color = "#e0e0e0" if not self.is_reply else "#d0d0d0"
        bg_color = "white" if not self.is_reply else "#f8f8f8"
        
        self.setStyleSheet(f"""
            NoteListItem {{
                border: 1px solid {border_color};
                border-radius: 4px;
                background-color: {bg_color};
                margin: 2px;
            }}
            NoteListItem:hover {{
                background-color: #f0f0f0;
                border-color: #0078d4;
            }}
        """)
        
        # Make clickable
        self.setCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks"""
        if event.button() == Qt.LeftButton:
            self.note_clicked.emit(self.note.id)
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())
        super().mousePressEvent(event)
    
    def show_context_menu(self, position):
        """Show context menu for note"""
        menu = QMenu(self)
        
        edit_action = menu.addAction("Edit Note")
        edit_action.triggered.connect(lambda: self.note_edited.emit(self.note.id))
        
        if not self.is_reply:
            reply_action = menu.addAction("Reply to Note")
            reply_action.triggered.connect(lambda: self.note_replied.emit(self.note.id))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("Delete Note")
        delete_action.triggered.connect(self.confirm_delete)
        
        menu.exec_(position)
    
    def confirm_delete(self):
        """Confirm note deletion"""
        reply = QMessageBox.question(
            self, "Delete Note",
            f"Are you sure you want to delete this note?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.note_deleted.emit(self.note.id)

class NotePanel(QWidget):
    """Panel for managing notes"""
    
    note_selected = pyqtSignal(str, int)  # document_path, page_number
    note_edited = pyqtSignal(str)         # note_id
    note_deleted = pyqtSignal(str)        # note_id
    note_replied = pyqtSignal(str)        # note_id
    
    def __init__(self, note_manager: NoteManager, parent=None):
        super().__init__(parent)
        self.note_manager = note_manager
        self.current_document = None
        self.notes = []
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = BodyLabel("Notes")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add note button
        self.add_button = QPushButton("+")
        self.add_button.setFixedSize(24, 24)
        self.add_button.setToolTip("Add Note")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF8C00;
            }
        """)
        header_layout.addWidget(self.add_button)
        
        layout.addLayout(header_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        # Category filter
        self.category_filter = ComboBox()
        self.category_filter.addItem("All Categories", "")
        filter_layout.addWidget(self.category_filter)
        
        # Sort options
        self.sort_combo = ComboBox()
        self.sort_combo.addItem("Newest First", "newest")
        self.sort_combo.addItem("Oldest First", "oldest")
        self.sort_combo.addItem("Page Order", "page")
        filter_layout.addWidget(self.sort_combo)
        
        layout.addLayout(filter_layout)
        
        # Search
        self.search_input = LineEdit()
        self.search_input.setPlaceholderText("Search notes...")
        layout.addWidget(self.search_input)
        
        # Notes list
        self.notes_scroll = ScrollArea()
        self.notes_scroll.setWidgetResizable(True)
        self.notes_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.notes_container = QWidget()
        self.notes_layout = QVBoxLayout(self.notes_container)
        self.notes_layout.setContentsMargins(0, 0, 0, 0)
        self.notes_layout.setSpacing(4)
        self.notes_layout.addStretch()
        
        self.notes_scroll.setWidget(self.notes_container)
        layout.addWidget(self.notes_scroll)
        
        # Status label
        self.status_label = CaptionLabel("No notes")
        self.status_label.setStyleSheet("color: #888; text-align: center;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.search_input.textChanged.connect(self.filter_notes)
        self.category_filter.currentTextChanged.connect(self.filter_notes)
        self.sort_combo.currentTextChanged.connect(self.filter_notes)
        self.add_button.clicked.connect(self.add_note_requested)
    
    def set_document(self, document_path: str):
        """Set the current document and load its notes"""
        self.current_document = document_path
        self.load_notes()
    
    def load_notes(self):
        """Load notes for the current document"""
        if not self.current_document:
            self.notes = []
        else:
            self.notes = self.note_manager.get_notes(self.current_document)
        
        self.update_category_filter()
        self.display_notes()
    
    def update_category_filter(self):
        """Update category filter options"""
        current_selection = self.category_filter.currentData()
        
        self.category_filter.clear()
        self.category_filter.addItem("All Categories", "")
        
        # Get unique categories from notes
        categories = set(n.category for n in self.notes if n.category != "default")
        for category in sorted(categories):
            self.category_filter.addItem(category, category)
        
        # Restore selection
        for i in range(self.category_filter.count()):
            if self.category_filter.itemData(i) == current_selection:
                self.category_filter.setCurrentIndex(i)
                break
    
    def display_notes(self):
        """Display filtered notes in the list"""
        # Clear existing items
        while self.notes_layout.count() > 1:  # Keep the stretch
            item = self.notes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Filter and sort notes
        filtered_notes = self.get_filtered_notes()
        
        # Group notes by threads
        note_threads = self._group_notes_by_threads(filtered_notes)
        
        # Add note items
        for thread in note_threads:
            for i, note in enumerate(thread):
                is_reply = i > 0  # First note is root, others are replies
                item_widget = NoteListItem(note, is_reply)
                item_widget.note_clicked.connect(self.on_note_clicked)
                item_widget.note_edited.connect(self.note_edited.emit)
                item_widget.note_deleted.connect(self.note_deleted.emit)
                item_widget.note_replied.connect(self.note_replied.emit)
                
                self.notes_layout.insertWidget(self.notes_layout.count() - 1, item_widget)
        
        # Update status
        if filtered_notes:
            self.status_label.setText(f"{len(filtered_notes)} note(s)")
        else:
            self.status_label.setText("No notes found")
    
    def get_filtered_notes(self) -> List[Note]:
        """Get notes filtered by search and category"""
        filtered = self.notes
        
        # Filter by search text
        search_text = self.search_input.text().strip().lower()
        if search_text:
            filtered = [
                n for n in filtered
                if (search_text in n.plain_text.lower() or 
                    search_text in n.content.lower())
            ]
        
        # Filter by category
        category_filter = self.category_filter.currentData()
        if category_filter:
            filtered = [n for n in filtered if n.category == category_filter]
        
        # Sort notes
        sort_option = self.sort_combo.currentData()
        if sort_option == "newest":
            filtered.sort(key=lambda n: n.created_at, reverse=True)
        elif sort_option == "oldest":
            filtered.sort(key=lambda n: n.created_at)
        elif sort_option == "page":
            filtered.sort(key=lambda n: (n.page_number, n.created_at))
        
        return filtered
    
    def _group_notes_by_threads(self, notes: List[Note]) -> List[List[Note]]:
        """Group notes by conversation threads"""
        threads = []
        processed_notes = set()
        
        for note in notes:
            if note.id in processed_notes:
                continue
            
            # Find thread for this note
            if note.parent_note_id is None:
                # This is a root note
                thread = self.note_manager.get_note_thread(note.id)
                thread = [n for n in thread if n in notes]  # Filter to displayed notes
                threads.append(thread)
                processed_notes.update(n.id for n in thread)
            else:
                # This is a reply - find its root
                root_note = note
                while root_note.parent_note_id:
                    parent = self.note_manager.get_note_by_id(root_note.parent_note_id)
                    if parent:
                        root_note = parent
                    else:
                        break
                
                if root_note.id not in processed_notes:
                    thread = self.note_manager.get_note_thread(root_note.id)
                    thread = [n for n in thread if n in notes]  # Filter to displayed notes
                    threads.append(thread)
                    processed_notes.update(n.id for n in thread)
        
        return threads
    
    def filter_notes(self):
        """Apply filters and update display"""
        self.display_notes()
    
    def on_note_clicked(self, note_id: str):
        """Handle note selection"""
        note = next((n for n in self.notes if n.id == note_id), None)
        if note:
            self.note_selected.emit(note.document_path, note.page_number)
    
    def add_note_requested(self):
        """Handle add note button click"""
        # This will be connected to the main window's add note functionality
        pass
    
    def refresh(self):
        """Refresh the note list"""
        self.load_notes()

class NoteCommentDialog(QDialog):
    """Dialog for adding comments/replies to notes"""
    
    comment_saved = pyqtSignal(object)  # Note object (comment)
    
    def __init__(self, parent_note: Note, categories: List[AnnotationCategory] = None, parent=None):
        super().__init__(parent)
        self.parent_note = parent_note
        self.categories = categories or []
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Reply to Note")
        self.setModal(True)
        self.resize(500, 350)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title_label = BodyLabel("Reply to Note")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Original note preview
        original_group = QGroupBox("Original Note")
        original_layout = QVBoxLayout(original_group)
        
        original_preview = CaptionLabel(self.parent_note.plain_text[:200] + "..." if len(self.parent_note.plain_text) > 200 else self.parent_note.plain_text)
        original_preview.setWordWrap(True)
        original_preview.setStyleSheet("color: #666; font-style: italic; padding: 8px; background-color: #f8f8f8; border-radius: 4px;")
        original_layout.addWidget(original_preview)
        
        layout.addWidget(original_group)
        
        # Reply content
        reply_group = QGroupBox("Your Reply")
        reply_layout = QVBoxLayout(reply_group)
        
        # Create rich text editor for reply
        self.reply_editor = RichTextEditor()
        self.reply_editor.setPlaceholderText("Enter your reply here...")
        
        # Create formatting toolbar
        self.formatting_toolbar = NoteFormattingToolbar(self.reply_editor)
        
        reply_layout.addWidget(self.formatting_toolbar)
        reply_layout.addWidget(self.reply_editor)
        
        layout.addWidget(reply_group)
        
        # Category selection
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        
        self.category_combo = ComboBox()
        self.category_combo.addItem("Default", "default")
        for category in self.categories:
            self.category_combo.addItem(category.name, category.id)
        category_layout.addWidget(self.category_combo)
        category_layout.addStretch()
        
        layout.addLayout(category_layout)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("Add Reply")
        
        layout.addWidget(button_box)
        
        # Connect buttons
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.reply_editor.content_changed.connect(self.validate_input)
        self.validate_input()  # Initial validation
    
    def validate_input(self):
        """Validate input and enable/disable OK button"""
        content = self.reply_editor.get_plain_text().strip()
        ok_button = self.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok)
        ok_button.setEnabled(bool(content))
    
    def get_reply_data(self) -> Dict:
        """Get reply data from form"""
        return {
            'content': self.reply_editor.get_html_content(),
            'plain_text': self.reply_editor.get_plain_text(),
            'category': self.category_combo.currentData(),
            'parent_note_id': self.parent_note.id,
            'document_path': self.parent_note.document_path,
            'page_number': self.parent_note.page_number,
            'position': self.parent_note.position  # Same position as parent
        }
    
    def accept(self):
        """Handle dialog acceptance"""
        reply_data = self.get_reply_data()
        self.comment_saved.emit(reply_data)
        super().accept()

class NoteTooltip(QWidget):
    """Tooltip widget for displaying note content on hover"""
    
    def __init__(self, note: Note, parent=None):
        super().__init__(parent)
        self.note = note
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the tooltip UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Note header
        header_layout = QHBoxLayout()
        
        # Note icon
        icon_label = QLabel("📝")
        header_layout.addWidget(icon_label)
        
        # Page info
        page_label = BodyLabel(f"Page {self.note.page_number}")
        page_label.setStyleSheet("font-weight: bold; color: #333;")
        header_layout.addWidget(page_label)
        
        header_layout.addStretch()
        
        # Date
        date_str = self.note.created_at.strftime("%m/%d/%Y %H:%M")
        date_label = CaptionLabel(date_str)
        date_label.setStyleSheet("color: #666;")
        header_layout.addWidget(date_label)
        
        layout.addLayout(header_layout)
        
        # Note content
        content_text = self.note.plain_text[:300]
        if len(self.note.plain_text) > 300:
            content_text += "..."
        
        content_label = BodyLabel(content_text)
        content_label.setWordWrap(True)
        content_label.setMaximumWidth(300)
        content_label.setStyleSheet("color: #333; line-height: 1.4;")
        layout.addWidget(content_label)
        
        # Category (if not default)
        if self.note.category != "default":
            category_label = CaptionLabel(f"Category: {self.note.category}")
            category_label.setStyleSheet("color: #0078d4; font-size: 10px;")
            layout.addWidget(category_label)
        
        # Style the tooltip
        self.setStyleSheet("""
            NoteTooltip {
                background-color: rgba(255, 255, 255, 240);
                border: 1px solid #ccc;
                border-radius: 6px;
            }
        """)
        
        # Auto-size
        self.adjustSize()

class NoteSearchWidget(QWidget):
    """Advanced search widget for notes"""
    
    search_changed = pyqtSignal(dict)  # search_criteria
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the search widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Search input
        self.search_input = LineEdit()
        self.search_input.setPlaceholderText("Search notes content...")
        layout.addWidget(self.search_input)
        
        # Advanced filters
        filters_layout = QHBoxLayout()
        
        # Date range
        date_group = QGroupBox("Date Range")
        date_layout = QHBoxLayout(date_group)
        
        self.date_filter = ComboBox()
        self.date_filter.addItem("All Time", "all")
        self.date_filter.addItem("Today", "today")
        self.date_filter.addItem("This Week", "week")
        self.date_filter.addItem("This Month", "month")
        self.date_filter.addItem("This Year", "year")
        date_layout.addWidget(self.date_filter)
        
        filters_layout.addWidget(date_group)
        
        # Category filter
        category_group = QGroupBox("Category")
        category_layout = QHBoxLayout(category_group)
        
        self.category_filter = ComboBox()
        self.category_filter.addItem("All Categories", "")
        category_layout.addWidget(self.category_filter)
        
        filters_layout.addWidget(category_group)
        
        # Page range
        page_group = QGroupBox("Page Range")
        page_layout = QHBoxLayout(page_group)
        
        self.page_from = LineEdit()
        self.page_from.setPlaceholderText("From")
        self.page_from.setMaximumWidth(60)
        page_layout.addWidget(self.page_from)
        
        page_layout.addWidget(QLabel("-"))
        
        self.page_to = LineEdit()
        self.page_to.setPlaceholderText("To")
        self.page_to.setMaximumWidth(60)
        page_layout.addWidget(self.page_to)
        
        filters_layout.addWidget(page_group)
        
        layout.addLayout(filters_layout)
        
        # Sort options
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("Sort by:"))
        
        self.sort_combo = ComboBox()
        self.sort_combo.addItem("Newest First", "newest")
        self.sort_combo.addItem("Oldest First", "oldest")
        self.sort_combo.addItem("Page Order", "page")
        self.sort_combo.addItem("Relevance", "relevance")
        sort_layout.addWidget(self.sort_combo)
        
        sort_layout.addStretch()
        
        # Clear filters button
        self.clear_button = QPushButton("Clear Filters")
        self.clear_button.setMaximumWidth(100)
        sort_layout.addWidget(self.clear_button)
        
        layout.addLayout(sort_layout)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.search_input.textChanged.connect(self.emit_search_criteria)
        self.date_filter.currentTextChanged.connect(self.emit_search_criteria)
        self.category_filter.currentTextChanged.connect(self.emit_search_criteria)
        self.page_from.textChanged.connect(self.emit_search_criteria)
        self.page_to.textChanged.connect(self.emit_search_criteria)
        self.sort_combo.currentTextChanged.connect(self.emit_search_criteria)
        self.clear_button.clicked.connect(self.clear_filters)
    
    def emit_search_criteria(self):
        """Emit current search criteria"""
        criteria = {
            'text': self.search_input.text().strip(),
            'date_range': self.date_filter.currentData(),
            'category': self.category_filter.currentData(),
            'page_from': self.page_from.text().strip(),
            'page_to': self.page_to.text().strip(),
            'sort_by': self.sort_combo.currentData()
        }
        self.search_changed.emit(criteria)
    
    def clear_filters(self):
        """Clear all search filters"""
        self.search_input.clear()
        self.date_filter.setCurrentIndex(0)
        self.category_filter.setCurrentIndex(0)
        self.page_from.clear()
        self.page_to.clear()
        self.sort_combo.setCurrentIndex(0)
    
    def update_categories(self, categories: List[str]):
        """Update available categories"""
        current_selection = self.category_filter.currentData()
        
        self.category_filter.clear()
        self.category_filter.addItem("All Categories", "")
        
        for category in sorted(categories):
            self.category_filter.addItem(category, category)
        
        # Restore selection
        for i in range(self.category_filter.count()):
            if self.category_filter.itemData(i) == current_selection:
                self.category_filter.setCurrentIndex(i)
                break