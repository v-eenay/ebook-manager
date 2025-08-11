"""
Main Window for Modern EBook Reader
Clean, minimal, professional design focused on document viewing.
"""

from pathlib import Path

try:
    from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QStackedWidget
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QIcon, QKeySequence, QAction
    QT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QStackedWidget
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QIcon, QKeySequence, QAction
    QT_VERSION = 5

# Logger
try:
    from utils.logger import setup_logging
    logger = setup_logging()
except Exception:
    import logging
    logger = logging.getLogger("ebook_reader")

class MainWindow(QMainWindow):
    """Main window with clean, minimal design focused on document viewing."""

    def __init__(self):
        super().__init__()
        self.current_document = None
        self.document_manager = None
        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        """Initialize the clean, minimal user interface."""
        self.setWindowTitle("Modern EBook Reader")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Create welcome page
        self.create_welcome_page()

        # Create document viewer page
        self.create_document_page()

        # Start with welcome page
        self.stacked_widget.setCurrentIndex(0)

    def create_welcome_page(self):
        """Create a clean, minimal welcome page."""
        from ui.welcome_widget import WelcomeWidget
        
        self.welcome_widget = WelcomeWidget()
        self.welcome_widget.open_file_requested.connect(self.open_file)
        self.welcome_widget.open_recent_requested.connect(self.load_document)
        
        self.stacked_widget.addWidget(self.welcome_widget)

    def create_document_page(self):
        """Create the document viewer page."""
        document_widget = QWidget()
        layout = QVBoxLayout(document_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create minimal toolbar
        self.create_minimal_toolbar(layout)

        # Create document viewer (lazy loading)
        self.document_viewer = None
        self.document_viewer_container = QWidget()
        self.document_viewer_layout = QVBoxLayout(self.document_viewer_container)
        self.document_viewer_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.document_viewer_container)

        self.stacked_widget.addWidget(document_widget)

    def create_minimal_toolbar(self, parent_layout):
        """Create a minimal, clean toolbar."""
        from qfluentwidgets import (ToolButton, FluentIcon as FIF, CardWidget)

        # Create minimal toolbar
        toolbar = CardWidget()
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet("""
            CardWidget {
                background-color: #F8F8F8;
                border: none;
                border-bottom: 1px solid #E0E0E0;
                border-radius: 0px;
                margin: 0px;
                padding: 0px;
            }
        """)

        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(20, 10, 20, 10)
        toolbar_layout.setSpacing(15)

        # Home button
        home_btn = ToolButton(FIF.HOME)
        home_btn.setText("Home")
        home_btn.setToolTip("Return to home screen")
        home_btn.clicked.connect(self.show_welcome)
        toolbar_layout.addWidget(home_btn)

        # Separator
        toolbar_layout.addWidget(self.create_separator())

        # File operations
        open_btn = ToolButton(FIF.FOLDER)
        open_btn.setText("Open")
        open_btn.setToolTip("Open document (Ctrl+O)")
        open_btn.clicked.connect(self.open_file)
        toolbar_layout.addWidget(open_btn)

        # Separator
        toolbar_layout.addWidget(self.create_separator())

        # Navigation
        prev_btn = ToolButton(FIF.LEFT_ARROW)
        prev_btn.setText("Previous")
        prev_btn.setToolTip("Previous page (Left Arrow)")
        prev_btn.clicked.connect(self.previous_page)
        toolbar_layout.addWidget(prev_btn)

        next_btn = ToolButton(FIF.RIGHT_ARROW)
        next_btn.setText("Next")
        next_btn.setToolTip("Next page (Right Arrow)")
        next_btn.clicked.connect(self.next_page)
        toolbar_layout.addWidget(next_btn)

        # Separator
        toolbar_layout.addWidget(self.create_separator())

        # Zoom controls
        zoom_out_btn = ToolButton(FIF.ZOOM_OUT)
        zoom_out_btn.setText("Zoom Out")
        zoom_out_btn.setToolTip("Zoom out (Ctrl+-)")
        zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar_layout.addWidget(zoom_out_btn)

        zoom_in_btn = ToolButton(FIF.ZOOM_IN)
        zoom_in_btn.setText("Zoom In")
        zoom_in_btn.setToolTip("Zoom in (Ctrl++)")
        zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar_layout.addWidget(zoom_in_btn)

        fit_btn = ToolButton(FIF.FULL_SCREEN)
        fit_btn.setText("Fit Page")
        fit_btn.setToolTip("Fit page to window")
        fit_btn.clicked.connect(self.fit_to_window)
        toolbar_layout.addWidget(fit_btn)

        toolbar_layout.addStretch()

        # Apply minimal button styling
        button_style = """
            ToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                color: #333333;
            }
            ToolButton:hover {
                background-color: #E8E8E8;
                border: 1px solid #D0D0D0;
            }
            ToolButton:pressed {
                background-color: #D0D0D0;
            }
        """
        
        for button in toolbar.findChildren(ToolButton):
            button.setStyleSheet(button_style)

        parent_layout.addWidget(toolbar)

    def create_separator(self):
        """Create a minimal separator."""
        separator = QWidget()
        separator.setFixedWidth(1)
        separator.setFixedHeight(30)
        separator.setStyleSheet("""
            QWidget {
                background-color: #D0D0D0;
                margin: 5px 0px;
            }
        """)
        return separator

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # File operations
        open_action = QAction(self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        self.addAction(open_action)

        # Navigation
        if QT_VERSION == 6:
            left_action = QAction(self)
            left_action.setShortcut(Qt.Key.Key_Left)
            left_action.triggered.connect(self.previous_page)
            self.addAction(left_action)

            right_action = QAction(self)
            right_action.setShortcut(Qt.Key.Key_Right)
            right_action.triggered.connect(self.next_page)
            self.addAction(right_action)
        else:
            left_action = QAction(self)
            left_action.setShortcut(Qt.Key_Left)
            left_action.triggered.connect(self.previous_page)
            self.addAction(left_action)

            right_action = QAction(self)
            right_action.setShortcut(Qt.Key_Right)
            right_action.triggered.connect(self.next_page)
            self.addAction(right_action)

    def ensure_document_viewer(self):
        """Ensure document viewer is created when needed."""
        if self.document_viewer is None:
            logger.info("Creating DocumentViewer...")
            from ui.document_viewer import DocumentViewer
            self.document_viewer = DocumentViewer()
            self.document_viewer_layout.addWidget(self.document_viewer)
            logger.info("DocumentViewer created successfully")

    def show_welcome(self):
        """Show the welcome page."""
        self.stacked_widget.setCurrentIndex(0)

    def show_document(self):
        """Show the document viewer page."""
        self.stacked_widget.setCurrentIndex(1)

    def open_file(self):
        """Open a document file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            "",
            "All Supported (*.pdf *.epub *.mobi);;PDF Files (*.pdf);;EPUB Files (*.epub);;MOBI Files (*.mobi)"
        )

        if file_path:
            self.load_document(file_path)

    def load_document(self, file_path):
        """Load and display a document."""
        try:
            # Import document manager
            from readers.document_manager import DocumentManager
            from utils.settings import add_recent_book
            
            if not self.document_manager:
                self.document_manager = DocumentManager()

            # Load document
            self.current_document = self.document_manager.load_document(file_path)
            
            if self.current_document:
                # Add to recent books
                add_recent_book(file_path)
                
                # Update welcome widget recent books
                if hasattr(self, 'welcome_widget'):
                    self.welcome_widget.add_recent_book(file_path)
                
                # Ensure document viewer exists
                self.ensure_document_viewer()
                
                # Load document into viewer
                self.document_viewer.load_document(self.current_document)
                
                # Switch to document view
                self.show_document()
                
                # Update window title
                filename = Path(file_path).name
                self.setWindowTitle(f"Modern EBook Reader - {filename}")
                
                logger.info("Document loaded successfully: %s", filename)

        except Exception as e:
            logger.exception("Error loading document: %s", e)
            # TODO: Show error message to user

    def previous_page(self):
        """Navigate to previous page."""
        if self.document_viewer:
            self.document_viewer.previous_page()

    def next_page(self):
        """Navigate to next page."""
        if self.document_viewer:
            self.document_viewer.next_page()

    def zoom_in(self):
        """Zoom in."""
        if self.document_viewer:
            self.document_viewer.zoom_in()

    def zoom_out(self):
        """Zoom out."""
        if self.document_viewer:
            self.document_viewer.zoom_out()

    def fit_to_window(self):
        """Fit page to window."""
        if self.document_viewer:
            self.document_viewer.fit_to_window()

    def closeEvent(self, event):
        """Handle window close event."""
        if self.current_document:
            self.current_document = None
        event.accept()
