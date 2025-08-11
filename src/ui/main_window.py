"""
Main Window for Modern EBook Reader
Clean, minimal, professional design focused on document viewing.
"""

from pathlib import Path

try:
    from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QStackedWidget
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QIcon, QKeySequence, QAction
    QT_VERSION = 5
except ImportError:
    from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QStackedWidget
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QIcon, QKeySequence, QAction
    QT_VERSION = 6

# Logger will be imported inside methods to avoid early initialization

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
        """Create an extremely minimal, professional toolbar."""
        # Import qfluentwidgets here to avoid early widget creation
        from qfluentwidgets import ToolButton, FluentIcon as FIF, CaptionLabel

        # Create ultra-minimal toolbar - reduced height for more document space
        toolbar = QWidget()
        toolbar.setFixedHeight(45)
        toolbar.setStyleSheet("""
            QWidget {
                background-color: #FAFAFA;
                border-bottom: 1px solid #E5E5E5;
            }
        """)

        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(15, 8, 15, 8)
        toolbar_layout.setSpacing(8)

        # Essential buttons only - icon-only for space efficiency
        home_btn = ToolButton(FIF.HOME)
        home_btn.setToolTip("Home (Alt+H)")
        home_btn.clicked.connect(self.show_welcome)
        toolbar_layout.addWidget(home_btn)

        open_btn = ToolButton(FIF.FOLDER)
        open_btn.setToolTip("Open Document (Ctrl+O)")
        open_btn.clicked.connect(self.open_file)
        toolbar_layout.addWidget(open_btn)

        # Minimal separator
        sep1 = QWidget()
        sep1.setFixedSize(1, 25)
        sep1.setStyleSheet("background-color: #D5D5D5;")
        toolbar_layout.addWidget(sep1)

        # Navigation - essential for document viewing
        prev_btn = ToolButton(FIF.LEFT_ARROW)
        prev_btn.setToolTip("Previous Page (←)")
        prev_btn.clicked.connect(self.previous_page)
        toolbar_layout.addWidget(prev_btn)

        next_btn = ToolButton(FIF.RIGHT_ARROW)
        next_btn.setToolTip("Next Page (→)")
        next_btn.clicked.connect(self.next_page)
        toolbar_layout.addWidget(next_btn)

        # Page info - minimal and unobtrusive
        self.page_info = CaptionLabel("No document")
        self.page_info.setStyleSheet("""
            CaptionLabel {
                color: #666666;
                font-size: 11px;
                padding: 4px 8px;
                background-color: transparent;
            }
        """)
        toolbar_layout.addWidget(self.page_info)

        toolbar_layout.addStretch()

        # Zoom controls - minimal
        zoom_out_btn = ToolButton(FIF.ZOOM_OUT)
        zoom_out_btn.setToolTip("Zoom Out (Ctrl+-)")
        zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar_layout.addWidget(zoom_out_btn)

        zoom_in_btn = ToolButton(FIF.ZOOM_IN)
        zoom_in_btn.setToolTip("Zoom In (Ctrl++)")
        zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar_layout.addWidget(zoom_in_btn)

        fit_btn = ToolButton(FIF.FULL_SCREEN)
        fit_btn.setToolTip("Fit to Window (Ctrl+0)")
        fit_btn.clicked.connect(self.fit_to_window)
        toolbar_layout.addWidget(fit_btn)

        # Ultra-minimal button styling - no text, smaller size
        button_style = """
            ToolButton {
                background-color: transparent;
                border: none;
                border-radius: 3px;
                padding: 6px;
                margin: 1px;
                color: #555555;
                min-width: 28px;
                max-width: 28px;
                min-height: 28px;
                max-height: 28px;
            }
            ToolButton:hover {
                background-color: #E0E0E0;
            }
            ToolButton:pressed {
                background-color: #D0D0D0;
            }
        """
        
        for button in toolbar.findChildren(ToolButton):
            button.setStyleSheet(button_style)

        parent_layout.addWidget(toolbar)

    def update_page_info(self, current_page=None, total_pages=None):
        """Update the minimal page info display."""
        if hasattr(self, 'page_info'):
            if current_page and total_pages:
                self.page_info.setText(f"{current_page}/{total_pages}")
            else:
                self.page_info.setText("No document")

    def setup_shortcuts(self):
        """Setup comprehensive keyboard shortcuts for professional use."""
        # File operations
        open_action = QAction(self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        self.addAction(open_action)

        # Home shortcut
        home_action = QAction(self)
        if QT_VERSION == 6:
            home_action.setShortcut(QKeySequence(Qt.Modifier.ALT | Qt.Key.Key_H))
        else:
            home_action.setShortcut(QKeySequence(Qt.ALT | Qt.Key_H))
        home_action.triggered.connect(self.show_welcome)
        self.addAction(home_action)

        # Navigation shortcuts
        if QT_VERSION == 6:
            # Arrow keys
            left_action = QAction(self)
            left_action.setShortcut(Qt.Key.Key_Left)
            left_action.triggered.connect(self.previous_page)
            self.addAction(left_action)

            right_action = QAction(self)
            right_action.setShortcut(Qt.Key.Key_Right)
            right_action.triggered.connect(self.next_page)
            self.addAction(right_action)

            # Page Up/Down
            page_up_action = QAction(self)
            page_up_action.setShortcut(Qt.Key.Key_PageUp)
            page_up_action.triggered.connect(self.previous_page)
            self.addAction(page_up_action)

            page_down_action = QAction(self)
            page_down_action.setShortcut(Qt.Key.Key_PageDown)
            page_down_action.triggered.connect(self.next_page)
            self.addAction(page_down_action)

            # Zoom shortcuts
            zoom_in_action = QAction(self)
            zoom_in_action.setShortcut(QKeySequence.ZoomIn)
            zoom_in_action.triggered.connect(self.zoom_in)
            self.addAction(zoom_in_action)

            zoom_out_action = QAction(self)
            zoom_out_action.setShortcut(QKeySequence.ZoomOut)
            zoom_out_action.triggered.connect(self.zoom_out)
            self.addAction(zoom_out_action)

            # Fit to window
            fit_action = QAction(self)
            fit_action.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_0))
            fit_action.triggered.connect(self.fit_to_window)
            self.addAction(fit_action)
        else:
            # Arrow keys
            left_action = QAction(self)
            left_action.setShortcut(Qt.Key_Left)
            left_action.triggered.connect(self.previous_page)
            self.addAction(left_action)

            right_action = QAction(self)
            right_action.setShortcut(Qt.Key_Right)
            right_action.triggered.connect(self.next_page)
            self.addAction(right_action)

            # Page Up/Down
            page_up_action = QAction(self)
            page_up_action.setShortcut(Qt.Key_PageUp)
            page_up_action.triggered.connect(self.previous_page)
            self.addAction(page_up_action)

            page_down_action = QAction(self)
            page_down_action.setShortcut(Qt.Key_PageDown)
            page_down_action.triggered.connect(self.next_page)
            self.addAction(page_down_action)

            # Zoom shortcuts
            zoom_in_action = QAction(self)
            zoom_in_action.setShortcut(QKeySequence.ZoomIn)
            zoom_in_action.triggered.connect(self.zoom_in)
            self.addAction(zoom_in_action)

            zoom_out_action = QAction(self)
            zoom_out_action.setShortcut(QKeySequence.ZoomOut)
            zoom_out_action.triggered.connect(self.zoom_out)
            self.addAction(zoom_out_action)

            # Fit to window
            fit_action = QAction(self)
            fit_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_0))
            fit_action.triggered.connect(self.fit_to_window)
            self.addAction(fit_action)

    def ensure_document_viewer(self):
        """Ensure document viewer is created when needed."""
        if self.document_viewer is None:
            try:
                from utils.logger import setup_logging
                logger = setup_logging()
                logger.info("Creating DocumentViewer...")
            except:
                pass
            from ui.document_viewer import DocumentViewer
            self.document_viewer = DocumentViewer()
            self.document_viewer_layout.addWidget(self.document_viewer)
            try:
                logger.info("DocumentViewer created successfully")
            except:
                pass

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
                
                # Update window title and page info
                filename = Path(file_path).name
                self.setWindowTitle(f"Modern EBook Reader - {filename}")
                self.update_page_info_display()
                
                try:
                    from utils.logger import setup_logging
                    logger = setup_logging()
                    logger.info("Document loaded successfully: %s", filename)
                except:
                    pass

        except Exception as e:
            try:
                from utils.logger import setup_logging
                logger = setup_logging()
                logger.exception("Error loading document: %s", e)
            except:
                pass
            # TODO: Show error message to user

    def previous_page(self):
        """Navigate to previous page."""
        if self.document_viewer and self.document_viewer.previous_page():
            self.update_page_info_display()

    def next_page(self):
        """Navigate to next page."""
        if self.document_viewer and self.document_viewer.next_page():
            self.update_page_info_display()

    def update_page_info_display(self):
        """Update page info display after navigation."""
        if self.document_viewer:
            current = self.document_viewer.get_current_page()
            total = self.document_viewer.get_total_pages()
            self.update_page_info(current, total)

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
