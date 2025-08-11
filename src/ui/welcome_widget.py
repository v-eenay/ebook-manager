"""
Welcome Widget - Clean, minimal welcome screen with recent books functionality
"""

from pathlib import Path

try:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QPixmap
    QT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QPixmap
    QT_VERSION = 5

from qfluentwidgets import (
    CardWidget, PrimaryPushButton, TitleLabel, BodyLabel, CaptionLabel,
    FluentIcon as FIF, SubtitleLabel
)

class WelcomeWidget(QWidget):
    """Clean, minimal welcome screen with recent books functionality."""
    
    # Signals
    open_file_requested = pyqtSignal()
    open_recent_requested = pyqtSignal(str)  # Emit file path
    
    def __init__(self):
        super().__init__()
        self.recent_books = self.load_recent_books()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the clean welcome screen UI."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(40)

        # Left side - Welcome content
        self.create_welcome_content(main_layout)
        
        # Right side - Recent books (if any)
        if self.recent_books:
            self.create_recent_books_panel(main_layout)

    def create_welcome_content(self, parent_layout):
        """Create the main welcome content."""
        welcome_container = QWidget()
        welcome_container.setMaximumWidth(500)
        layout = QVBoxLayout(welcome_container)
        
        if QT_VERSION == 6:
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            layout.setAlignment(Qt.AlignCenter)
        
        layout.setSpacing(30)

        # Main welcome card
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(25)

        # App icon
        icon_label = BodyLabel("📚")
        icon_label.setStyleSheet("font-size: 48px;")
        if QT_VERSION == 6:
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            icon_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(icon_label)
        
        # App title
        title = TitleLabel("Modern EBook Reader")
        if QT_VERSION == 6:
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        # Description
        desc = BodyLabel("A clean, minimal ebook reader for PDF, EPUB, and MOBI files.")
        desc.setWordWrap(True)
        if QT_VERSION == 6:
            desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            desc.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(desc)
        
        # Open button
        open_button = PrimaryPushButton("Open Document", FIF.FOLDER)
        open_button.setMinimumWidth(180)
        open_button.setMinimumHeight(40)
        open_button.clicked.connect(self.open_file_requested.emit)
        card_layout.addWidget(open_button)
        
        # Keyboard shortcut hint
        shortcut_label = CaptionLabel("Press Ctrl+O to open a document")
        if QT_VERSION == 6:
            shortcut_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            shortcut_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(shortcut_label)

        layout.addWidget(card)
        parent_layout.addWidget(welcome_container)

    def create_recent_books_panel(self, parent_layout):
        """Create the recent books panel."""
        recent_container = QWidget()
        recent_container.setMaximumWidth(400)
        layout = QVBoxLayout(recent_container)
        layout.setSpacing(20)

        # Recent books card
        recent_card = CardWidget()
        recent_layout = QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(20, 20, 20, 20)
        recent_layout.setSpacing(15)

        # Title
        recent_title = SubtitleLabel("Recent Books")
        recent_layout.addWidget(recent_title)

        # Recent books list
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(300)
        self.recent_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px 0px;
            }
            QListWidget::item:hover {
                background-color: #E8E8E8;
            }
            QListWidget::item:selected {
                background-color: #0078D4;
                color: white;
            }
        """)
        
        # Populate recent books
        for book_path in self.recent_books[:10]:  # Show max 10 recent books
            if Path(book_path).exists():
                item = QListWidgetItem(Path(book_path).name)
                item.setData(Qt.UserRole, book_path)
                item.setToolTip(book_path)
                self.recent_list.addItem(item)

        self.recent_list.itemDoubleClicked.connect(self.on_recent_book_selected)
        recent_layout.addWidget(self.recent_list)

        # Clear recent button
        clear_button = PrimaryPushButton("Clear Recent", FIF.DELETE)
        clear_button.clicked.connect(self.clear_recent_books)
        recent_layout.addWidget(clear_button)

        layout.addWidget(recent_card)
        parent_layout.addWidget(recent_container)

    def on_recent_book_selected(self, item):
        """Handle recent book selection."""
        file_path = item.data(Qt.UserRole)
        if file_path and Path(file_path).exists():
            self.open_recent_requested.emit(file_path)

    def load_recent_books(self):
        """Load recent books from settings."""
        try:
            from utils.settings import load_recent_books
            return load_recent_books()
        except ImportError:
            # Create basic recent books functionality
            return []

    def add_recent_book(self, file_path):
        """Add a book to recent books list."""
        try:
            from utils.settings import add_recent_book
            add_recent_book(file_path)
            self.recent_books = self.load_recent_books()
            self.refresh_recent_books()
        except ImportError:
            pass

    def clear_recent_books(self):
        """Clear all recent books."""
        try:
            from utils.settings import clear_recent_books
            clear_recent_books()
            self.recent_books = []
            self.recent_list.clear()
        except ImportError:
            pass

    def refresh_recent_books(self):
        """Refresh the recent books display."""
        if hasattr(self, 'recent_list'):
            self.recent_list.clear()
            for book_path in self.recent_books[:10]:
                if Path(book_path).exists():
                    item = QListWidgetItem(Path(book_path).name)
                    item.setData(Qt.UserRole, book_path)
                    item.setToolTip(book_path)
                    self.recent_list.addItem(item)
