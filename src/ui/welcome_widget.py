"""
Welcome Widget - Clean, minimal welcome screen with recent books functionality
"""

from pathlib import Path

try:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QPixmap
    QT_VERSION = 5
except ImportError:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QPixmap
    QT_VERSION = 6

# qfluentwidgets imports moved to methods to avoid early widget creation

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
        """Create minimal, professional welcome content."""
        from qfluentwidgets import CardWidget, PrimaryPushButton, TitleLabel, BodyLabel, CaptionLabel
        
        welcome_container = QWidget()
        welcome_container.setMaximumWidth(450)
        layout = QVBoxLayout(welcome_container)
        
        if QT_VERSION == 6:
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            layout.setAlignment(Qt.AlignCenter)
        
        layout.setSpacing(25)

        # Minimal welcome card with clean styling
        card = CardWidget()
        card.setStyleSheet("""
            CardWidget {
                background-color: #FEFEFE;
                border: 1px solid #F0F0F0;
                border-radius: 8px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 35, 35, 35)
        card_layout.setSpacing(20)

        # Minimal app title - no icon for cleaner look
        title = TitleLabel("Modern EBook Reader")
        title.setStyleSheet("""
            TitleLabel {
                font-size: 24px;
                font-weight: 300;
                color: #2C2C2C;
                margin-bottom: 5px;
            }
        """)
        if QT_VERSION == 6:
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        # Minimal description
        desc = BodyLabel("Professional document reading for PDF, EPUB, and MOBI files")
        desc.setStyleSheet("""
            BodyLabel {
                font-size: 14px;
                color: #666666;
                font-weight: 400;
                line-height: 1.4;
            }
        """)
        desc.setWordWrap(True)
        if QT_VERSION == 6:
            desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            desc.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(desc)
        
        # Clean, minimal open button
        open_button = PrimaryPushButton("Open Document")
        open_button.setStyleSheet("""
            PrimaryPushButton {
                background-color: #0078D4;
                border: none;
                border-radius: 4px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                color: white;
            }
            PrimaryPushButton:hover {
                background-color: #106EBE;
            }
            PrimaryPushButton:pressed {
                background-color: #005A9E;
            }
        """)
        open_button.setMinimumWidth(160)
        open_button.setMinimumHeight(36)
        open_button.clicked.connect(self.open_file_requested.emit)
        card_layout.addWidget(open_button)
        
        # Minimal keyboard shortcut hint
        shortcut_label = CaptionLabel("Ctrl+O")
        shortcut_label.setStyleSheet("""
            CaptionLabel {
                font-size: 11px;
                color: #999999;
                font-weight: 400;
            }
        """)
        if QT_VERSION == 6:
            shortcut_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            shortcut_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(shortcut_label)

        layout.addWidget(card)
        parent_layout.addWidget(welcome_container)

    def create_recent_books_panel(self, parent_layout):
        """Create a minimal, professional recent books panel."""
        from qfluentwidgets import CardWidget, PrimaryPushButton, SubtitleLabel
        
        recent_container = QWidget()
        recent_container.setMaximumWidth(350)
        layout = QVBoxLayout(recent_container)
        layout.setSpacing(15)

        # Minimal recent books card
        recent_card = CardWidget()
        recent_card.setStyleSheet("""
            CardWidget {
                background-color: #FEFEFE;
                border: 1px solid #F0F0F0;
                border-radius: 8px;
            }
        """)
        recent_layout = QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(18, 18, 18, 18)
        recent_layout.setSpacing(12)

        # Minimal title
        recent_title = SubtitleLabel("Recent")
        recent_title.setStyleSheet("""
            SubtitleLabel {
                font-size: 16px;
                font-weight: 500;
                color: #2C2C2C;
                margin-bottom: 5px;
            }
        """)
        recent_layout.addWidget(recent_title)

        # Clean recent books list
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(280)
        self.recent_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                outline: none;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-radius: 3px;
                margin: 1px 0px;
                color: #444444;
            }
            QListWidget::item:hover {
                background-color: #F5F5F5;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
        """)
        
        # Populate recent books - show max 8 for cleaner look
        for book_path in self.recent_books[:8]:
            if Path(book_path).exists():
                # Show only filename, truncate if too long
                filename = Path(book_path).name
                if len(filename) > 35:
                    filename = filename[:32] + "..."
                
                item = QListWidgetItem(filename)
                item.setData(Qt.UserRole, book_path)
                item.setToolTip(book_path)
                self.recent_list.addItem(item)

        self.recent_list.itemDoubleClicked.connect(self.on_recent_book_selected)
        recent_layout.addWidget(self.recent_list)

        # Minimal clear button
        clear_button = PrimaryPushButton("Clear")
        clear_button.setStyleSheet("""
            PrimaryPushButton {
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-radius: 3px;
                padding: 6px 12px;
                font-size: 12px;
                color: #666666;
            }
            PrimaryPushButton:hover {
                background-color: #EEEEEE;
                border-color: #D0D0D0;
            }
        """)
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
