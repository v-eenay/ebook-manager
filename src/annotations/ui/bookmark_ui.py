"""
Bookmark UI Components
User interface elements for bookmark management
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QAction, QDialog,
    QLineEdit, QTextEdit, QLabel, QPushButton, QListWidget, QListWidgetItem,
    QMenu, QMessageBox, QComboBox, QFrame, QSplitter, QScrollArea,
    QGroupBox, QFormLayout, QDialogButtonBox, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont, QPalette, QPixmap, QPainter, QColor
from qfluentwidgets import (
    PushButton, LineEdit, TextEdit, ListWidget, ComboBox,
    BodyLabel, CaptionLabel, ScrollArea, TreeWidget
)
import logging
from typing import List, Optional, Dict
from datetime import datetime

from ..models import Bookmark, AnnotationCategory
from ..bookmark_manager import BookmarkManager

logger = logging.getLogger("ebook_reader")

class BookmarkIndicator(QWidget):
    """Visual bookmark indicator for document margins"""
    
    clicked = pyqtSignal(str)  # bookmark_id
    
    def __init__(self, bookmark: Bookmark, parent=None):
        super().__init__(parent)
        self.bookmark = bookmark
        self.setFixedSize(20, 20)
        self.setToolTip(f"{bookmark.title}\n{bookmark.description}")
        self.setCursor(Qt.PointingHandCursor)
        
        # Style the indicator
        self.setStyleSheet("""
            BookmarkIndicator {
                background-color: #0078d4;
                border: 2px solid #005a9e;
                border-radius: 10px;
            }
            BookmarkIndicator:hover {
                background-color: #106ebe;
                border-color: #004578;
            }
        """)
    
    def paintEvent(self, event):
        """Custom paint event for bookmark icon"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw bookmark icon
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QColor(255, 255, 255))
        
        # Simple bookmark shape
        points = [
            (6, 4), (14, 4), (14, 16), (10, 12), (6, 16)
        ]
        
        from PyQt5.QtGui import QPolygon
        from PyQt5.QtCore import QPoint
        polygon = QPolygon([QPoint(x, y) for x, y in points])
        painter.drawPolygon(polygon)
    
    def mousePressEvent(self, event):
        """Handle click events"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.bookmark.id)
        super().mousePressEvent(event)

class BookmarkDialog(QDialog):
    """Dialog for creating and editing bookmarks"""
    
    bookmark_saved = pyqtSignal(object)  # Bookmark object
    
    def __init__(self, bookmark: Optional[Bookmark] = None, 
                 categories: List[AnnotationCategory] = None, parent=None):
        super().__init__(parent)
        self.bookmark = bookmark
        self.categories = categories or []
        self.is_editing = bookmark is not None
        
        self.init_ui()
        self.setup_connections()
        
        if self.is_editing:
            self.load_bookmark_data()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Edit Bookmark" if self.is_editing else "Add Bookmark")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title section
        title_label = BodyLabel("Bookmark Details")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Form layout
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(8)
        
        # Title input
        self.title_input = LineEdit()
        self.title_input.setPlaceholderText("Enter bookmark title...")
        form_layout.addRow("Title:", self.title_input)
        
        # Description input
        self.description_input = TextEdit()
        self.description_input.setPlaceholderText("Enter bookmark description (optional)...")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)
        
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
        
        # Style buttons
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("Save Bookmark" if self.is_editing else "Add Bookmark")
        
        layout.addWidget(button_box)
        
        # Connect buttons
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.title_input.textChanged.connect(self.validate_input)
        self.validate_input()  # Initial validation
    
    def validate_input(self):
        """Validate input and enable/disable OK button"""
        title = self.title_input.text().strip()
        ok_button = self.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok)
        ok_button.setEnabled(bool(title))
    
    def load_bookmark_data(self):
        """Load existing bookmark data into form"""
        if self.bookmark:
            self.title_input.setText(self.bookmark.title)
            self.description_input.setPlainText(self.bookmark.description)
            
            # Set category
            for i in range(self.category_combo.count()):
                if self.category_combo.itemData(i) == self.bookmark.category:
                    self.category_combo.setCurrentIndex(i)
                    break
    
    def get_bookmark_data(self) -> Dict:
        """Get bookmark data from form"""
        return {
            'title': self.title_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'category': self.category_combo.currentData()
        }
    
    def accept(self):
        """Handle dialog acceptance"""
        data = self.get_bookmark_data()
        
        if self.is_editing and self.bookmark:
            # Update existing bookmark
            self.bookmark.title = data['title']
            self.bookmark.description = data['description']
            self.bookmark.category = data['category']
            self.bookmark.update_timestamp()
        else:
            # Create new bookmark (will be handled by caller)
            pass
        
        self.bookmark_saved.emit(self.bookmark)
        super().accept()

class BookmarkListItem(QWidget):
    """Custom list item for bookmarks"""
    
    bookmark_clicked = pyqtSignal(str)  # bookmark_id
    bookmark_edited = pyqtSignal(str)   # bookmark_id
    bookmark_deleted = pyqtSignal(str)  # bookmark_id
    
    def __init__(self, bookmark: Bookmark, parent=None):
        super().__init__(parent)
        self.bookmark = bookmark
        self.init_ui()
    
    def init_ui(self):
        """Initialize the list item UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        
        # Header with title and page
        header_layout = QHBoxLayout()
        
        # Title
        title_label = BodyLabel(self.bookmark.title or f"Page {self.bookmark.page_number}")
        title_label.setStyleSheet("font-weight: bold; color: #0078d4;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Page number
        page_label = CaptionLabel(f"Page {self.bookmark.page_number}")
        page_label.setStyleSheet("color: #666;")
        header_layout.addWidget(page_label)
        
        layout.addLayout(header_layout)
        
        # Description (if exists)
        if self.bookmark.description:
            desc_label = CaptionLabel(self.bookmark.description)
            desc_label.setStyleSheet("color: #888;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # Footer with date and category
        footer_layout = QHBoxLayout()
        
        # Date
        date_str = self.bookmark.created_at.strftime("%m/%d/%Y %H:%M")
        date_label = CaptionLabel(date_str)
        date_label.setStyleSheet("color: #999; font-size: 10px;")
        footer_layout.addWidget(date_label)
        
        footer_layout.addStretch()
        
        # Category (if not default)
        if self.bookmark.category != "default":
            category_label = CaptionLabel(self.bookmark.category)
            category_label.setStyleSheet("color: #0078d4; font-size: 10px;")
            footer_layout.addWidget(category_label)
        
        layout.addLayout(footer_layout)
        
        # Style the widget
        self.setStyleSheet("""
            BookmarkListItem {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                margin: 2px;
            }
            BookmarkListItem:hover {
                background-color: #f5f5f5;
                border-color: #0078d4;
            }
        """)
        
        # Make clickable
        self.setCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks"""
        if event.button() == Qt.LeftButton:
            self.bookmark_clicked.emit(self.bookmark.id)
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())
        super().mousePressEvent(event)
    
    def show_context_menu(self, position):
        """Show context menu for bookmark"""
        menu = QMenu(self)
        
        edit_action = menu.addAction("Edit Bookmark")
        edit_action.triggered.connect(lambda: self.bookmark_edited.emit(self.bookmark.id))
        
        delete_action = menu.addAction("Delete Bookmark")
        delete_action.triggered.connect(self.confirm_delete)
        
        menu.exec_(position)
    
    def confirm_delete(self):
        """Confirm bookmark deletion"""
        reply = QMessageBox.question(
            self, "Delete Bookmark",
            f"Are you sure you want to delete the bookmark '{self.bookmark.title}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.bookmark_deleted.emit(self.bookmark.id)

class BookmarkSidebar(QWidget):
    """Sidebar widget for bookmark navigation and management"""
    
    bookmark_selected = pyqtSignal(str, int)  # document_path, page_number
    bookmark_edited = pyqtSignal(str)         # bookmark_id
    bookmark_deleted = pyqtSignal(str)        # bookmark_id
    
    def __init__(self, bookmark_manager: BookmarkManager, parent=None):
        super().__init__(parent)
        self.bookmark_manager = bookmark_manager
        self.current_document = None
        self.bookmarks = []
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = BodyLabel("Bookmarks")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add bookmark button
        self.add_button = QPushButton("+")
        self.add_button.setFixedSize(24, 24)
        self.add_button.setToolTip("Add Bookmark")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        header_layout.addWidget(self.add_button)
        
        layout.addLayout(header_layout)
        
        # Search/filter
        self.search_input = LineEdit()
        self.search_input.setPlaceholderText("Search bookmarks...")
        layout.addWidget(self.search_input)
        
        # Category filter
        self.category_filter = ComboBox()
        self.category_filter.addItem("All Categories", "")
        layout.addWidget(self.category_filter)
        
        # Bookmarks list
        self.bookmarks_scroll = ScrollArea()
        self.bookmarks_scroll.setWidgetResizable(True)
        self.bookmarks_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.bookmarks_container = QWidget()
        self.bookmarks_layout = QVBoxLayout(self.bookmarks_container)
        self.bookmarks_layout.setContentsMargins(0, 0, 0, 0)
        self.bookmarks_layout.setSpacing(4)
        self.bookmarks_layout.addStretch()
        
        self.bookmarks_scroll.setWidget(self.bookmarks_container)
        layout.addWidget(self.bookmarks_scroll)
        
        # Status label
        self.status_label = CaptionLabel("No bookmarks")
        self.status_label.setStyleSheet("color: #888; text-align: center;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.search_input.textChanged.connect(self.filter_bookmarks)
        self.category_filter.currentTextChanged.connect(self.filter_bookmarks)
        self.add_button.clicked.connect(self.add_bookmark_requested)
    
    def set_document(self, document_path: str):
        """Set the current document and load its bookmarks"""
        self.current_document = document_path
        self.load_bookmarks()
    
    def load_bookmarks(self):
        """Load bookmarks for the current document"""
        if not self.current_document:
            self.bookmarks = []
        else:
            self.bookmarks = self.bookmark_manager.get_bookmarks(self.current_document)
        
        self.update_category_filter()
        self.display_bookmarks()
    
    def update_category_filter(self):
        """Update category filter options"""
        current_selection = self.category_filter.currentData()
        
        self.category_filter.clear()
        self.category_filter.addItem("All Categories", "")
        
        # Get unique categories from bookmarks
        categories = set(b.category for b in self.bookmarks if b.category != "default")
        for category in sorted(categories):
            self.category_filter.addItem(category, category)
        
        # Restore selection
        for i in range(self.category_filter.count()):
            if self.category_filter.itemData(i) == current_selection:
                self.category_filter.setCurrentIndex(i)
                break
    
    def display_bookmarks(self):
        """Display filtered bookmarks in the list"""
        # Clear existing items
        while self.bookmarks_layout.count() > 1:  # Keep the stretch
            item = self.bookmarks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Filter bookmarks
        filtered_bookmarks = self.get_filtered_bookmarks()
        
        # Add bookmark items
        for bookmark in filtered_bookmarks:
            item_widget = BookmarkListItem(bookmark)
            item_widget.bookmark_clicked.connect(self.on_bookmark_clicked)
            item_widget.bookmark_edited.connect(self.bookmark_edited.emit)
            item_widget.bookmark_deleted.connect(self.bookmark_deleted.emit)
            
            self.bookmarks_layout.insertWidget(self.bookmarks_layout.count() - 1, item_widget)
        
        # Update status
        if filtered_bookmarks:
            self.status_label.setText(f"{len(filtered_bookmarks)} bookmark(s)")
        else:
            self.status_label.setText("No bookmarks found")
    
    def get_filtered_bookmarks(self) -> List[Bookmark]:
        """Get bookmarks filtered by search and category"""
        filtered = self.bookmarks
        
        # Filter by search text
        search_text = self.search_input.text().strip().lower()
        if search_text:
            filtered = [
                b for b in filtered
                if (search_text in b.title.lower() or 
                    search_text in b.description.lower())
            ]
        
        # Filter by category
        category_filter = self.category_filter.currentData()
        if category_filter:
            filtered = [b for b in filtered if b.category == category_filter]
        
        # Sort by page number
        filtered.sort(key=lambda b: b.page_number)
        
        return filtered
    
    def filter_bookmarks(self):
        """Apply filters and update display"""
        self.display_bookmarks()
    
    def on_bookmark_clicked(self, bookmark_id: str):
        """Handle bookmark selection"""
        bookmark = next((b for b in self.bookmarks if b.id == bookmark_id), None)
        if bookmark:
            self.bookmark_selected.emit(bookmark.document_path, bookmark.page_number)
    
    def add_bookmark_requested(self):
        """Handle add bookmark button click"""
        # This will be connected to the main window's add bookmark functionality
        pass
    
    def refresh(self):
        """Refresh the bookmark list"""
        self.load_bookmarks()

class BookmarkToolbar(QToolBar):
    """Toolbar with bookmark-related actions"""
    
    add_bookmark_requested = pyqtSignal()
    toggle_bookmarks_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Bookmarks", parent)
        self.init_actions()
    
    def init_actions(self):
        """Initialize toolbar actions"""
        # Add bookmark action
        self.add_bookmark_action = QAction("Add Bookmark", self)
        self.add_bookmark_action.setToolTip("Add bookmark to current page")
        self.add_bookmark_action.setShortcut("Ctrl+B")
        self.add_bookmark_action.triggered.connect(self.add_bookmark_requested.emit)
        self.addAction(self.add_bookmark_action)
        
        self.addSeparator()
        
        # Toggle bookmarks panel
        self.toggle_bookmarks_action = QAction("Show Bookmarks", self)
        self.toggle_bookmarks_action.setToolTip("Show/hide bookmarks panel")
        self.toggle_bookmarks_action.setShortcut("Ctrl+Shift+B")
        self.toggle_bookmarks_action.setCheckable(True)
        self.toggle_bookmarks_action.triggered.connect(self.toggle_bookmarks_requested.emit)
        self.addAction(self.toggle_bookmarks_action)
    
    def set_bookmark_exists(self, exists: bool):
        """Update add bookmark action based on whether bookmark exists"""
        if exists:
            self.add_bookmark_action.setText("Remove Bookmark")
            self.add_bookmark_action.setToolTip("Remove bookmark from current page")
        else:
            self.add_bookmark_action.setText("Add Bookmark")
            self.add_bookmark_action.setToolTip("Add bookmark to current page")
    
    def set_bookmarks_panel_visible(self, visible: bool):
        """Update toggle action based on panel visibility"""
        self.toggle_bookmarks_action.setChecked(visible)
        self.toggle_bookmarks_action.setText("Hide Bookmarks" if visible else "Show Bookmarks")